import os
import sys
import json
import requests
from flask import Flask, render_template, request, jsonify, Response, stream_with_context

# Add parent directory to sys.path to import Bookito modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processors.concept_extractor import ConceptExtractor
from processors.augmented_content_generator import (
    AugmentedContentGenerator,
    format_augmented_results_to_text,
    NO_RESULTS_MESSAGE
)
from web.model import ClassifierWord2VecMLP

# Top-of-File Constants
WEB_USE_WORD_SCORING = True
WEB_USE_MULTI_INSTANCE_BOOST = True
WEB_USE_SEMANTIC_BOOST = True
WEB_MAX_DF_THRESHOLD = 0.90

DEFAULT_FLASK_PORT = 5000

app = Flask(__name__)

# Initialize extractor, search generator, and prompt classifier at startup
extractor = ConceptExtractor(
    use_word_scoring=WEB_USE_WORD_SCORING,
    use_multi_instance_boost=WEB_USE_MULTI_INSTANCE_BOOST,
    use_semantic_boost=WEB_USE_SEMANTIC_BOOST,
    max_df_threshold=WEB_MAX_DF_THRESHOLD
)
generator = AugmentedContentGenerator()
classifier = ClassifierWord2VecMLP()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    user_message = data.get("message", '') if data else ''

    if not user_message:
        return jsonify({"response": ''})

    # Step 1: Prompt Classification (executed BEFORE collecting context)
    category = classifier.infer(user_message)

    # Step 2: Extract concept phrases from user prompt
    kept_tuples, _ = extractor.extract_with_details(user_message)
    extracted_concepts = [phrase for phrase, score, occ in kept_tuples]

    if not extracted_concepts:
        return jsonify({"response": NO_RESULTS_MESSAGE})

    # Step 3: Perform multi-concept search, expansion, and aggregation
    results = generator.generate_augmented_content(extracted_concepts)

    # Step 4: Format results into text (book title, ordered chunks, "...", "----")
    formatted_context = format_augmented_results_to_text(results)

    # Step 5: Stream response from Chatsito.Web
    system_prompt = "YOU ARE A DESIGN DOCUMENT ASSISTANT. YOU WILL DESIGN TECHNICAL DOCUMENTS FOCUSING ON PROS AND CONS OF THE CHOICES REQUIRED BY THE DESIGN. YOU WILL ALWAYS CREATE A DESIGN DOCUMENT WITH THIS EMPHASIS ON PROS/CONS NO MATTER WHAT THE USER ASKS FOR. ALL PROMPTS WILL RESULT IN A NEW REVISION OF THE DESIGN DOCUMENT."
    
    def generate():
        import traceback
        import web.tools as custom_tools
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"CATEGORY: {category}\n\nPrompt: {user_message}\n\nContext:\n{formatted_context}"}
            ]
            
            tools_schema = [
                {
                    "type": "function",
                    "function": {
                        "name": "webSearch",
                        "description": "Performs a web search.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"}
                            },
                            "required": ["query"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "urlGet",
                        "description": "Fetches text content from a URL.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string"}
                            },
                            "required": ["url"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "semanticChapterSearch",
                        "description": "Performs a semantic + lexical search for chapters.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"}
                            },
                            "required": ["query"]
                        }
                    }
                }
            ]

            def run_stream(msgs):
                headers = {"Content-Type": "application/json"}
                # PascalCase for Chatsito wrapper if needed, but standard schema inside
                payload = {
                    "Model": "",
                    "Messages": msgs,
                    "Tools": tools_schema
                }
                resp = requests.post("http://localhost:5257/api/chat/stream", json=payload, headers=headers, stream=True, timeout=150)
                if resp.status_code != 200:
                    yield f"Error from Chatsito: {resp.status_code} {resp.text}"
                    return
                
                for line in resp.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data: '):
                            data_str = decoded_line[6:]
                            try:
                                data_json = json.loads(data_str)
                                if data_json.get("type") == "content" and "content" in data_json:
                                    yield data_json["content"]
                                elif data_json.get("type") == "tool_call":
                                    yield {"tool_calls": data_json.get("toolCalls", [])}
                            except Exception:
                                pass

            while True:
                tool_calls_to_execute = None
                
                for chunk in run_stream(messages):
                    if isinstance(chunk, dict) and "tool_calls" in chunk:
                        tool_calls_to_execute = chunk["tool_calls"]
                        yield "\n\n*Using tools...*\n\n"
                    elif isinstance(chunk, str):
                        yield chunk
                        
                if tool_calls_to_execute:
                    # Append assistant message with tool calls
                    messages.append({
                        "role": "assistant",
                        "content": "",
                        "tool_calls": tool_calls_to_execute
                    })
                    
                    # Execute tools and append results
                    for tc in tool_calls_to_execute:
                        func_name = tc.get("function", {}).get("name")
                        args_str = tc.get("function", {}).get("arguments", "{}")
                        tc_id = tc.get("id", "call_123")  # Fallback ID if not provided
                        try:
                            args = json.loads(args_str)
                        except:
                            args = {}
                            
                        result = ""
                        try:
                            if func_name == "webSearch":
                                result = custom_tools.web_search(args.get("query", ""))
                            elif func_name == "urlGet":
                                result = custom_tools.url_get(args.get("url", ""))
                            elif func_name == "semanticChapterSearch":
                                result = custom_tools.semantic_chapter_search(args.get("query", ""))
                            else:
                                result = "Unknown tool"
                        except Exception as e:
                            result = f"Error executing tool: {e}"
                            
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc_id,
                            "content": str(result)
                        })
                else:
                    break
        except Exception as e:
            yield f"Exception connecting to Chatsito: {str(e)}\n\n{traceback.format_exc()}"

    return Response(stream_with_context(generate()), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, port=DEFAULT_FLASK_PORT)
