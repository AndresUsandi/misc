using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using chatsito.Core;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Extensions.Logging;

namespace chatsito.Web.Pages
{
    public class StreamEvent
    {
        [System.Text.Json.Serialization.JsonPropertyName("type")]
        public string Type { get; set; } = string.Empty;

        [System.Text.Json.Serialization.JsonPropertyName("content")]
        public string Content { get; set; } = string.Empty;
    }

    public class IndexModel : PageModel
    {
        private readonly ModelClient _modelClient;
        private readonly ILogger<IndexModel> _logger;
        private const string SessionKeyHistory = "ChatHistory";

        public Chat ChatHistory { get; set; } = new Chat();

        public IReadOnlyList<ChatMessage> ConversationHistory => ChatHistory.Messages;

        public List<string> AvailableModels { get; set; } = new List<string>();
        public string? SelectedModel { get; set; }
        public bool IncludeThinking { get; set; } = false;

        [BindProperty]
        public string? Prompt { get; set; }

        public string? ErrorMessage { get; set; }

        public IndexModel(ModelClient modelClient, ILogger<IndexModel> logger)
        {
            _modelClient = modelClient;
            _logger = logger;
        }

        public async Task OnGetAsync()
        {
            LoadHistory();
            await LoadModelsAsync();
        }

        private async Task LoadModelsAsync()
        {
            try
            {
                AvailableModels = await _modelClient.ListModelsAsync();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to load models list.");
            }

            SelectedModel = HttpContext.Session.GetString("SelectedModel") ?? AvailableModels.FirstOrDefault();
            IncludeThinking = HttpContext.Session.GetString("IncludeThinking") == "true";
        }

        // Kept empty string property for layout consistency
        // AJAX endpoint
        public async Task<IActionResult> OnPostSendMessageStreamAsync([FromBody] SendRequest request)
        {
            if (string.IsNullOrWhiteSpace(request?.Prompt))
            {
                Response.StatusCode = 400;
                return new EmptyResult();
            }

            LoadHistory();

            if (ChatHistory.Messages.Count == 0 || ChatHistory.Messages.FirstOrDefault()?.Role != Role.System)
            {
                var systemMessage = new ChatMessage
                {
                    Role = Role.System,
                    Content = "You are a helpful AI assistant with tool-calling capabilities. Always output your thought process in <think>...</think> tags before calling a tool or giving a final answer. YOU MUST close your thinking process with the </think> tag BEFORE providing your final response to the user. Never write your final answer inside the think block."
                };
                ChatHistory.InsertMessage(0, systemMessage);
            }

            var userMessage = new ChatMessage
            {
                Role = Role.User,
                Content = request.Prompt
            };
            ChatHistory.AddMessage(userMessage);
            SaveHistory();

            string model = request.Model;
            if (string.IsNullOrWhiteSpace(model))
            {
                model = HttpContext.Session.GetString("SelectedModel");
                if (string.IsNullOrWhiteSpace(model))
                {
                    try
                    {
                        var models = await _modelClient.ListModelsAsync();
                        model = models.FirstOrDefault() ?? "gemma4:26b";
                    }
                    catch
                    {
                        model = "gemma4:26b";
                    }
                }
            }

            Response.ContentType = "text/event-stream";
            
            Func<string, string, Task> sendEvent = async (type, content) =>
            {
                var data = new StreamEvent { Type = type, Content = content };
                string json = System.Text.Json.JsonSerializer.Serialize(data);
                await Response.WriteAsync($"data: {json}\n\n");
                await Response.Body.FlushAsync();
            };

            try
            {
                bool useTools = true;
                int maxToolCycles = 10;
                int currentCycle = 0;
                
                System.Diagnostics.Debug.WriteLine($"[{DateTime.Now:HH:mm:ss.fff}] [Stream] Starting stream loop. Model: {model}, IncludeThinking: {request.IncludeThinking}");

                while (currentCycle < maxToolCycles)
                {
                    currentCycle++;
                    System.Diagnostics.Debug.WriteLine($"[{DateTime.Now:HH:mm:ss.fff}] [Stream] Beginning cycle {currentCycle}/{maxToolCycles}. Current ChatHistory length: {ChatHistory.Messages.Count}");
                    var assistantMessage = new ChatMessage { Role = Role.Assistant, Content = "" };
                    bool toolCallMade = false;
                    bool hitLengthLimit = false;

                    try
                    {
                        await foreach (var message in _modelClient.SendChatStreamAsync(model, ChatHistory, useTools ? ToolDefinitionProvider.GetTools() : null))
                        {
                        if (message.ToolCalls != null && message.ToolCalls.Any())
                        {
                            System.Diagnostics.Debug.WriteLine($"[{DateTime.Now:HH:mm:ss.fff}] [StreamChunk] Received tool calls chunk: {System.Text.Json.JsonSerializer.Serialize(message.ToolCalls)}");
                            assistantMessage.ToolCalls = message.ToolCalls;
                            toolCallMade = true;
                        }

                        string actualReasoning = message.ThinkingContent ?? message.ReasoningContent ?? string.Empty;
                        if (request.IncludeThinking && !string.IsNullOrEmpty(actualReasoning))
                        {
                            assistantMessage.ReasoningContent += actualReasoning;
                            await sendEvent("reasoning", actualReasoning);
                        }

                        if (!string.IsNullOrEmpty(message.Content))
                        {
                            System.Diagnostics.Debug.WriteLine($"[{DateTime.Now:HH:mm:ss.fff}] [StreamChunk] Content chunk: {message.Content}");
                            assistantMessage.Content += message.Content;
                            await sendEvent("content", message.Content);
                        }
                        
                        if (message.DoneReason == "length")
                        {
                            hitLengthLimit = true;
                        }
                        }
                    }
                    catch (Exception streamEx) when (streamEx.Message.Contains("does not support tools") && useTools)
                    {
                        useTools = false;
                        continue;
                    }

                    if (toolCallMade && assistantMessage.ToolCalls != null)
                    {
                        System.Diagnostics.Debug.WriteLine($"[{DateTime.Now:HH:mm:ss.fff}] [Stream] Tool call detected, preparing to execute tools.");
                        ChatHistory.AddMessage(assistantMessage);

                        foreach (var call in assistantMessage.ToolCalls)
                        {
                            var toolMessage = new ChatMessage { Role = Role.Tool, Name = call.Function.Name, Content = "" };
                            
                            string callLog = $"> [Tool Call] {call.Function.Name}()\n";
                            await sendEvent("tool_call", callLog);

                            IDictionary<string, object>? argumentsDict = call.Function.Arguments;

                            System.Diagnostics.Debug.WriteLine($"[{DateTime.Now:HH:mm:ss.fff}] [Stream] Executing tool: {call.Function.Name} with args: {System.Text.Json.JsonSerializer.Serialize(argumentsDict)}");
                            string result = await ToolDefinitionProvider.ExecuteToolAsync(call.Function.Name, argumentsDict);
                            System.Diagnostics.Debug.WriteLine($"[{DateTime.Now:HH:mm:ss.fff}] [Stream] Tool {call.Function.Name} returned result: {result}");
                            toolMessage.Content = result;

                            string resultLog = $"> [Tool Result] {call.Function.Name} returned {result.Split('\n').Length} lines.\n";
                            await sendEvent("tool_result", resultLog);
                            
                            ChatHistory.AddMessage(toolMessage);
                        }

                        SaveHistory();
                    }
                    else
                    {
                        System.Diagnostics.Debug.WriteLine($"[{DateTime.Now:HH:mm:ss.fff}] [Stream] No tools were called in this cycle. Finalizing.");

                        if (string.IsNullOrEmpty(assistantMessage.Content))
                        {
                            System.Diagnostics.Debug.WriteLine($"[{DateTime.Now:HH:mm:ss.fff}] [Stream] Model did not return any content. Adding fallback message. HitLengthLimit: {hitLengthLimit}");
                            if (hitLengthLimit)
                            {
                                assistantMessage.Content = "⚠️ The assistant ran out of memory (hit its maximum token limit) while thinking, and was abruptly cut off before it could provide a final response.";
                            }
                            else
                            {
                                assistantMessage.Content = "The assistant completed its execution but did not provide a final response text.";
                            }
                            await sendEvent("error", assistantMessage.Content);
                        }

                        if (!string.IsNullOrEmpty(assistantMessage.Content) || toolCallMade)
                        {
                            System.Diagnostics.Debug.WriteLine($"[{DateTime.Now:HH:mm:ss.fff}] [Stream] Saving assistant message:\n{System.Text.Json.JsonSerializer.Serialize(assistantMessage)}");
                            ChatHistory.AddMessage(assistantMessage);
                            SaveHistory();
                        }
                        
                        System.Diagnostics.Debug.WriteLine($"[{DateTime.Now:HH:mm:ss.fff}] [Stream] Breaking out of cycle. Final ChatHistory:\n{System.Text.Json.JsonSerializer.Serialize(ChatHistory.Messages)}");
                        break;
                    }
                }

                if (currentCycle >= maxToolCycles)
                {
                    System.Diagnostics.Debug.WriteLine($"[{DateTime.Now:HH:mm:ss.fff}] [Stream] WARNING: Reached max tool cycles ({maxToolCycles}). Force ending.");
                    await sendEvent("error", "Error: Maximum tool iterations reached. The assistant was unable to provide a final answer.");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to send chat message to Chatsito via streaming AJAX.");
                if (ChatHistory.Messages.Count > 0 && ChatHistory.Messages[^1].Role == Role.User)
                {
                    ChatHistory.RemoveLastMessage();
                    SaveHistory();
                }
                
                if (!Response.HasStarted)
                {
                    Response.StatusCode = 500;
                    await Response.WriteAsync("Error: " + ex.Message);
                }
            }

            return new EmptyResult();
        }
        public IActionResult OnPostChangeSettings([FromBody] ChangeSettingsRequest request)
        {
            if (request != null)
            {
                if (!string.IsNullOrEmpty(request.Model))
                {
                    HttpContext.Session.SetString("SelectedModel", request.Model);
                }
                
                HttpContext.Session.SetString("IncludeThinking", request.IncludeThinking ? "true" : "false");
                return new JsonResult(new { success = true });
            }
            return new JsonResult(new { success = false });
        }

        public IActionResult OnPostClearAsync()
        {
            HttpContext.Session.Remove(SessionKeyHistory);
            HttpContext.Session.Remove("SelectedModel");
            HttpContext.Session.Remove("IncludeThinking");
            ChatHistory.Clear();
            return RedirectToPage();
        }

        private void LoadHistory()
        {
            string? historyJson = HttpContext.Session.GetString(SessionKeyHistory);
            if (!string.IsNullOrEmpty(historyJson))
            {
                try
                {
                    var state = JsonSerializer.Deserialize<ChatSessionState>(historyJson);
                    if (state != null)
                    {
                        ChatHistory.LoadMessages(state.Messages);
                        ChatHistory.ContextTokenSize = state.ContextTokenSize;
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Failed to deserialize session chat history.");
                    ChatHistory.Clear();
                }
            }
            else
            {
                ChatHistory.Clear();
            }
        }

        private void SaveHistory()
        {
            var state = new ChatSessionState
            {
                Messages = new List<ChatMessage>(ChatHistory.Messages),
                ContextTokenSize = ChatHistory.ContextTokenSize
            };
            string historyJson = JsonSerializer.Serialize(state);
            HttpContext.Session.SetString(SessionKeyHistory, historyJson);
        }

        private class ChatSessionState
        {
            public List<ChatMessage> Messages { get; set; } = new List<ChatMessage>();
            public int ContextTokenSize { get; set; }
        }

        public class SendRequest
        {
            public string Prompt { get; set; } = string.Empty;
            public string Model { get; set; } = string.Empty;
            public bool IncludeThinking { get; set; } = false;
        }

        public class ChangeSettingsRequest
        {
            public string Model { get; set; } = string.Empty;
            public bool IncludeThinking { get; set; } = false;
        }
    }
}
