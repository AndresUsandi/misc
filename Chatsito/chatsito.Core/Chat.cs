using System;
using System.Collections.Generic;
using System.Linq;

namespace chatsito.Core
{
    public class Chat
    {
        private readonly List<ChatMessage> _messages = new List<ChatMessage>();

        public IReadOnlyList<ChatMessage> Messages => _messages.AsReadOnly();

        private static int _contextTokenSize = Configuration.TokenMin;
        private static readonly object _lock = new object();

        public int ContextTokenSize
        {
            get
            {
                lock (_lock)
                {
                    return _contextTokenSize;
                }
            }
            set
            {
                lock (_lock)
                {
                    _contextTokenSize = value;
                }
            }
        }

        public void AddMessage(ChatMessage message)
        {
            if (message == null) throw new ArgumentNullException(nameof(message));


            int tokenCount = Utils.EstimateTokenCount(message.Content ?? string.Empty);
            if (message.ToolCalls != null)
            {
                foreach (var tc in message.ToolCalls)
                {
                    if (tc?.Function != null)
                    {
                        tokenCount += Utils.EstimateTokenCount(tc.Function.Name ?? string.Empty);
                        if (tc.Function.Arguments != null)
                        {
                            tokenCount += Utils.EstimateTokenCount(System.Text.Json.JsonSerializer.Serialize(tc.Function.Arguments));
                        }
                    }
                }
            }
            message.TokenCount = tokenCount;
            _messages.Add(message);
        }

        public void InsertMessage(int index, ChatMessage message)
        {
            if (message == null) throw new ArgumentNullException(nameof(message));


            int tokenCount = Utils.EstimateTokenCount(message.Content ?? string.Empty);
            if (message.ToolCalls != null)
            {
                foreach (var tc in message.ToolCalls)
                {
                    if (tc?.Function != null)
                    {
                        tokenCount += Utils.EstimateTokenCount(tc.Function.Name ?? string.Empty);
                        if (tc.Function.Arguments != null)
                        {
                            tokenCount += Utils.EstimateTokenCount(System.Text.Json.JsonSerializer.Serialize(tc.Function.Arguments));
                        }
                    }
                }
            }
            message.TokenCount = tokenCount;
            _messages.Insert(index, message);
        }

        public void AddMessage(Role role, string content)
        {
            AddMessage(new ChatMessage { Role = role, Content = content });
        }

        public int GetTotalTokens()
        {
            return _messages.Sum(m => m.TokenCount);
        }

        private int CalculateContextSize()
        {
            int totalTokens = GetTotalTokens();
            return (int)((totalTokens + Configuration.TokenResponse) * Configuration.TokenMargin);
        }

        public int UpdateAndGetContextSize()
        {
            lock (_lock)
            {
                if (_contextTokenSize <= 0)
                {
                    _contextTokenSize = Configuration.TokenMin;
                }
                int calculatedSize = CalculateContextSize();
                while (calculatedSize > _contextTokenSize)
                {
                    _contextTokenSize *= 2;
                }
                return _contextTokenSize;
            }
        }

        public void RemoveLastMessage()
        {
            if (_messages.Count > 0)
            {
                _messages.RemoveAt(_messages.Count - 1);
            }
        }

        public void Clear()
        {
            _messages.Clear();
            lock (_lock)
            {
                _contextTokenSize = Configuration.TokenMin;
            }
        }

        // Helper to initialize from an existing collection (useful for deserialization in session)
        public void LoadMessages(IEnumerable<ChatMessage> messages)
        {
            _messages.Clear();
            if (messages != null)
            {
                foreach (var msg in messages)
                {
                    // If TokenCount is 0, estimate it
                    if (msg.TokenCount <= 0)
                    {
                        int tokenCount = Utils.EstimateTokenCount(msg.Content ?? string.Empty);
                        if (msg.ToolCalls != null)
                        {
                            foreach (var tc in msg.ToolCalls)
                            {
                                if (tc?.Function != null)
                                {
                                    tokenCount += Utils.EstimateTokenCount(tc.Function.Name ?? string.Empty);
                                    if (tc.Function.Arguments != null)
                                    {
                                        tokenCount += Utils.EstimateTokenCount(System.Text.Json.JsonSerializer.Serialize(tc.Function.Arguments));
                                    }
                                }
                            }
                        }
                        msg.TokenCount = tokenCount;
                    }
                    _messages.Add(msg);
                }
            }
        }
    }
}
