using System.Text.Json.Serialization;

namespace chatsito.Core
{
    public enum Role
    {
        System,
        User,
        Assistant,
        Tool
    }

    public class ChatMessage
    {
        public Role Role { get; set; }
        public string Content { get; set; } = string.Empty;

        [JsonPropertyName("reasoning_content")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? ReasoningContent { get; set; }

        [JsonPropertyName("thinking")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? ThinkingContent { get; set; }

        [JsonPropertyName("name")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Name { get; set; }

        [JsonPropertyName("tool_calls")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public List<ToolCall>? ToolCalls { get; set; }

        [JsonIgnore]
        public int TokenCount { get; set; }

        [JsonIgnore]
        public string? DoneReason { get; set; }
    }

    public class ToolCall
    {
        [JsonPropertyName("function")]
        public FunctionCall Function { get; set; } = new FunctionCall();
    }

    public class FunctionCall
    {
        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("arguments")]
        public Dictionary<string, object>? Arguments { get; set; }
    }
}
