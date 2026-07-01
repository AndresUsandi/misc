using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Threading.Tasks;

namespace chatsito.Core
{
    public class ModelClient : IDisposable
    {
        private readonly OllamaClient _ollamaClient;

        public ModelClient(HttpClient httpClient, string baseUrl = "http://localhost:11434")
        {
            _ollamaClient = new OllamaClient(httpClient, baseUrl);
        }

        public ModelClient()
        {
            _ollamaClient = new OllamaClient();
        }

        public async Task<ChatMessage?> SendChatAsync(string model, Chat chat, List<object>? tools = null)
        {
            return await _ollamaClient.SendChatAsync(model, chat, tools);
        }

        public IAsyncEnumerable<ChatMessage> SendChatStreamAsync(string model, Chat chat, List<object>? tools = null, System.Threading.CancellationToken cancellationToken = default)
        {
            return _ollamaClient.SendChatStreamAsync(model, chat, tools, cancellationToken);
        }

        public async Task<List<string>> ListModelsAsync()
        {
            return await _ollamaClient.ListModelsAsync();
        }

        public void Dispose()
        {
            _ollamaClient.Dispose();
        }
    }
}
