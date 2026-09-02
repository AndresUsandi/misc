import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import sys
import os

# Ensure the parent directory is in the path so we can import the abstractor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from prompt_data_abstractor_v1 import load_models, process_paragraphs
except ImportError as e:
    print(f"Error importing abstractor: {e}")
    sys.exit(1)

class DataGenVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Prompt Data Abstractor Visualizer")
        self.root.geometry("1200x900")
        
        self.models_loaded = False
        self.processing_lock = threading.Lock()
        self.current_processed_paragraph = ""
        
        self.setup_ui()
        
        # Start loading models in background
        self.status_var.set("Status: Loading massive ML models (SpaCy, GLiNER, BERTs)... Please wait (30-60s).")
        self.text_input.config(state=tk.DISABLED)
        threading.Thread(target=self.init_models, daemon=True).start()
        
    def init_models(self):
        try:
            load_models()
            self.models_loaded = True
            self.root.after(0, self.on_models_loaded)
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Status: Error loading models: {e}"))

    def on_models_loaded(self):
        self.status_var.set("Status: Ready. Type or click on a paragraph.")
        self.text_input.config(state=tk.NORMAL)
        self.text_input.focus_set()
        
    def setup_ui(self):
        main_paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top Frame (25%)
        top_frame = ttk.LabelFrame(main_paned, text="Input Paragraphs (One per line)")
        main_paned.add(top_frame, weight=1)
        
        self.text_input = scrolledtext.ScrolledText(top_frame, font=("Consolas", 11), wrap=tk.WORD)
        self.text_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.text_input.bind("<KeyRelease>", self.on_cursor_move)
        self.text_input.bind("<ButtonRelease>", self.on_cursor_move)
        
        # Bottom Frame (75%)
        bottom_frame = ttk.LabelFrame(main_paned, text="Step-by-Step Extraction Trace")
        main_paned.add(bottom_frame, weight=3)
        
        self.trace_output = scrolledtext.ScrolledText(bottom_frame, font=("Consolas", 10), wrap=tk.WORD, state=tk.DISABLED)
        self.trace_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def on_cursor_move(self, event):
        if not self.models_loaded:
            return
            
        # Get the line text where the cursor currently is
        try:
            index = self.text_input.index(tk.INSERT)
            line_num = index.split(".")[0]
            line_text = self.text_input.get(f"{line_num}.0", f"{line_num}.end").strip()
            
            if not line_text:
                return
                
            if line_text != self.current_processed_paragraph:
                self.current_processed_paragraph = line_text
                self.trigger_processing(line_text)
                
        except Exception as e:
            print(f"Cursor error: {e}")
            
    def trigger_processing(self, text):
        if not self.processing_lock.acquire(blocking=False):
            return # Already processing something
            
        self.status_var.set("Status: Processing...")
        self.update_trace_pane(f"Processing paragraph: \n{text}\n\nPlease wait...")
        
        threading.Thread(target=self.run_extraction_thread, args=(text,), daemon=True).start()
        
    def run_extraction_thread(self, text):
        try:
            # We call the modified abstractor logic
            results = process_paragraphs([text], return_debug=True)
            self.root.after(0, self.display_results, results)
        except Exception as e:
            self.root.after(0, self.update_trace_pane, f"Error during processing:\n{e}")
        finally:
            self.root.after(0, lambda: self.status_var.set("Status: Ready."))
            self.processing_lock.release()
            
    def display_results(self, results):
        if not results:
            self.update_trace_pane("No results returned.")
            return
            
        res = results[0]
        debug = res.get("debug", {})
        
        out = []
        out.append("=== 1. SpaCy Raw Extraction (Roots & Subtrees) ===")
        for s in debug.get("spacy_raw", []):
            out.append(f"Root: {s['token']} (dep: {s['dep']}) -> Subtree: {s['subtree']}")
            
        out.append("\n=== 2. Subtree Cleaning (Trimming fluff) ===")
        for c in debug.get("cleaned_subtrees", []):
            out.append(f"Root: {c['root_token']} -> Cleaned: {c['cleaned_text']}")
            
        out.append("\n=== 3. Length Validation ===")
        for l in debug.get("length_validation", []):
            out.append(f"{l['status']}: '{l['candidate']}'")
            
        out.append("\n=== 4. 1-Word Voting Gate ===")
        if not debug.get("voting_gate"):
            out.append("No 1-word candidates evaluated.")
        for v in debug.get("voting_gate", []):
            passed = "PASSED" if v['passed'] else "FAILED"
            out.append(f"[{passed}] '{v['candidate']}' (Votes: {v['total_votes']}) -> GLiNER: {v['gliner_vote']}, IT-Skill: {v['itskill_vote']}, SO-NER: {v['so_vote']}")
            
        out.append("\n=== 5. KeyBERT Cosine Similarity ===")
        for k in debug.get("keybert_scores", []):
            status = "PASSED" if k['passed'] else "FAILED"
            out.append(f"[{status}] Score: {k['score']:.4f} -> '{k['candidate']}'")
            
        out.append("\n=== 6. Final Valid Spans ===")
        for f in debug.get("final_spans", []):
            out.append(f"- {f}")
            
        self.update_trace_pane("\n".join(out))
        
    def update_trace_pane(self, text):
        self.trace_output.config(state=tk.NORMAL)
        self.trace_output.delete("1.0", tk.END)
        self.trace_output.insert(tk.END, text)
        self.trace_output.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = DataGenVisualizerApp(root)
    root.mainloop()
