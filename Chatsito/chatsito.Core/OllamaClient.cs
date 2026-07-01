using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading;
using System.Threading.Tasks;
using System.IO;
using System.Runtime.CompilerServices;
namespace chatsito.Core
{
    public class OllamaClient : IDisposable
    {
        private readonly HttpClient _httpClient;
        private readonly string _baseUrl;
        private readonly JsonSerializerOptions _serializerOptions;
        private readonly bool _disposeHttpClient;

        // Primary constructor. Suitable for Dependency Injection (like AddHttpClient)
        // and also manual instantiation where HttpClient is provided.
        public OllamaClient(HttpClient httpClient, string baseUrl = "http://localhost:11434")
        {
            _baseUrl = baseUrl.TrimEnd('/');
            _httpClient = httpClient ?? throw new ArgumentNullException(nameof(httpClient));
            _disposeHttpClient = false;

            _serializerOptions = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                Converters = { new JsonStringEnumConverter(JsonNamingPolicy.CamelCase) }
            };
        }

        // Parameterless constructor for simple console use or quick testing
        public OllamaClient() : this(new HttpClient(), "http://localhost:11434")
        {
            _disposeHttpClient = true;
        }

        public async Task<ChatMessage?> SendChatAsync(string model, Chat chat, List<object>? tools = null)
        {
            object?[] thinkFallbacks = { "high", true, false, null };
            HttpResponseMessage? finalResponse = null;
            string lastError = string.Empty;

            foreach (var thinkVal in thinkFallbacks)
            {
                var requestBody = new OllamaRequest
                {
                    Model = model,
                    Messages = chat.Messages.ToList(),
                    Stream = false,
                    Think = thinkVal,
                    Options = new OllamaOptions
                    {
                        NumCtx = chat.UpdateAndGetContextSize()
                    },
                    Tools = tools,
                    KeepAlive = $"{Configuration.DefaultKeepAliveHours}h"
                };

                string jsonPayload = JsonSerializer.Serialize(requestBody, _serializerOptions);
                var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

                string requestUri = _httpClient.BaseAddress != null 
                    ? "api/chat" 
                    : $"{_baseUrl}/api/chat";

                var request = new HttpRequestMessage(HttpMethod.Post, requestUri) { Content = content };
                var responseMessage = await _httpClient.SendAsync(request, HttpCompletionOption.ResponseHeadersRead);

                if (responseMessage.IsSuccessStatusCode)
                {
                    finalResponse = responseMessage;
                    break;
                }
                else
                {
                    lastError = await responseMessage.Content.ReadAsStringAsync();
                    responseMessage.Dispose();
                }
            }

            if (finalResponse == null)
            {
                throw new HttpRequestException($"Server responded with errors. Last error: {lastError}");
            }

            string jsonResponse = await finalResponse.Content.ReadAsStringAsync();
            var ollamaResponse = JsonSerializer.Deserialize<OllamaResponse>(jsonResponse, _serializerOptions);
            finalResponse.Dispose();

            return ollamaResponse?.Message;
        }

        public async IAsyncEnumerable<ChatMessage> SendChatStreamAsync(string model, Chat chat, List<object>? tools = null, [EnumeratorCancellation] CancellationToken cancellationToken = default)
        {
            object?[] thinkFallbacks = { "high", true, false, null };
            HttpResponseMessage? finalResponse = null;
            string lastError = string.Empty;

            foreach (var thinkVal in thinkFallbacks)
            {
                var requestBody = new OllamaRequest
                {
                    Model = model,
                    Messages = chat.Messages.ToList(),
                    Stream = true,
                    Think = thinkVal,
                    Options = new OllamaOptions
                    {
                        NumCtx = chat.UpdateAndGetContextSize()
                    },
                    Tools = tools,
                    KeepAlive = $"{Configuration.DefaultKeepAliveHours}h"
                };

                string jsonPayload = JsonSerializer.Serialize(requestBody, _serializerOptions);
                var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

                string requestUri = _httpClient.BaseAddress != null 
                    ? "api/chat" 
                    : $"{_baseUrl}/api/chat";

                var request = new HttpRequestMessage(HttpMethod.Post, requestUri) { Content = content };
                var responseMessage = await _httpClient.SendAsync(request, HttpCompletionOption.ResponseHeadersRead, cancellationToken);

                if (responseMessage.IsSuccessStatusCode)
                {
                    finalResponse = responseMessage;
                    break;
                }
                else
                {
                    lastError = await responseMessage.Content.ReadAsStringAsync(cancellationToken);
                    responseMessage.Dispose();
                }
            }

            if (finalResponse == null)
            {
                throw new HttpRequestException($"Server responded with errors. Last error: {lastError}");
            }

            using var responseStream = await finalResponse.Content.ReadAsStreamAsync(cancellationToken);
            using var reader = new StreamReader(responseStream);

            while (!reader.EndOfStream && !cancellationToken.IsCancellationRequested)
            {
                var line = await reader.ReadLineAsync();
                if (string.IsNullOrWhiteSpace(line)) continue;

                var ollamaResponse = JsonSerializer.Deserialize<OllamaResponse>(line, _serializerOptions);
                if (ollamaResponse?.Message != null)
                {
                    if (ollamaResponse.Done)
                    {
                        ollamaResponse.Message.DoneReason = ollamaResponse.DoneReason;
                    }
                    yield return ollamaResponse.Message;
                }
            }
        }

        public async Task<List<string>> ListModelsAsync()
        {
            string requestUri = _httpClient.BaseAddress != null 
                ? "api/tags" 
                : $"{_baseUrl}/api/tags";

            HttpResponseMessage responseMessage = await _httpClient.GetAsync(requestUri);

            if (!responseMessage.IsSuccessStatusCode)
            {
                string errorContent = await responseMessage.Content.ReadAsStringAsync();
                throw new HttpRequestException($"Server responded with status code {responseMessage.StatusCode}: {errorContent}");
            }

            string jsonResponse = await responseMessage.Content.ReadAsStringAsync();
            var tagsResponse = JsonSerializer.Deserialize<OllamaTagsResponse>(jsonResponse, _serializerOptions);

            return tagsResponse?.Models?.Select(m => m.Name).ToList() ?? new List<string>();
        }

        public void Dispose()
        {
            if (_disposeHttpClient)
            {
                _httpClient.Dispose();
            }
        }
    }
}
