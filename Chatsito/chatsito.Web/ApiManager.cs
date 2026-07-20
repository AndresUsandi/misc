using System;
using System.Collections.Generic;
using System.Linq;
using chatsito.Core;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace chatsito.Web
{
    public static class ApiManager
    {
        public static void MapApiEndpoints(WebApplication app)
        {
            // Expose a CORS-enabled, CSRF-free endpoint for the VS Code extension
            app.MapPost("/api/chat", async (
                [FromBody] ApiChatRequest request,
                [FromServices] ModelClient client) =>
            {
                if (request == null || request.Messages == null)
                {
                    return Results.BadRequest(new { error = "Invalid request payload" });
                }

                try
                {
                    var chat = new Chat();
                    chat.LoadMessages(request.Messages);

                    string targetModel = request.Model;
                    if (string.IsNullOrWhiteSpace(targetModel))
                    {
                        try
                        {
                            var models = await client.ListModelsAsync();
                            targetModel = models.FirstOrDefault();
                        }
                        catch { }

                        if (string.IsNullOrWhiteSpace(targetModel))
                        {
                            return Results.BadRequest(new { error = "No model provided and unable to resolve a default model from Ollama." });
                        }
                    }

                    var assistantMessage = await client.SendChatAsync(targetModel, chat, request.Tools);

                    if (assistantMessage != null)
                    {
                        return Results.Ok(new
                        {
                            success = true,
                            message = assistantMessage,
                            doneReason = assistantMessage.DoneReason,
                            contextTokenSize = chat.ContextTokenSize,
                            predictTokenSize = Configuration.TokenMax
                        });
                    }
                    else
                    {
                        return Results.Json(new { success = false, error = "Empty response from Chatsito." }, statusCode: 500);
                    }
                }
                catch (Exception ex)
                {
                    return Results.Json(new { success = false, error = ex.Message }, statusCode: 500);
                }
            });

            // Expose configuration settings to clients (such as the VS Code extension)
            app.MapGet("/api/config", async ([FromServices] ModelClient client) =>
            {
                string? defaultModel = null;
                try
                {
                    var models = await client.ListModelsAsync();
                    defaultModel = models.FirstOrDefault();
                }
                catch { }

                return Results.Ok(new
                {
                    defaultModel = defaultModel,
                    defaultOllamaUrl = Configuration.DefaultOllamaUrl,
                    timeoutMins = Configuration.TimeoutMins,
                    maxToolIterations = Configuration.MaxToolIterations,
                    tokenMax = Configuration.TokenMax
                });
            });

            // Expose the available models to the VS Code extension
            app.MapGet("/api/models", async ([FromServices] ModelClient client) =>
            {
                try
                {
                    var models = await client.ListModelsAsync();
                    return Results.Ok(models);
                }
                catch (Exception ex)
                {
                    return Results.Json(new { error = ex.Message }, statusCode: 500);
                }
            });

            // Expose utility for estimating token count of raw text strings
            app.MapPost("/api/estimate-tokens", ([FromBody] TokenEstimateRequest request) =>
            {
                if (request == null || request.Text == null)
                {
                    return Results.BadRequest(new { error = "Invalid request payload" });
                }

                int estimatedTokens = Utils.EstimateTokenCount(request.Text);
                return Results.Ok(new { count = estimatedTokens });
            });
        }
    }

    public class ApiChatRequest
    {
        public string Model { get; set; } = string.Empty;
        public List<ChatMessage> Messages { get; set; } = new List<ChatMessage>();
        public List<object>? Tools { get; set; }
    }

    public class TokenEstimateRequest
    {
        public string Text { get; set; } = string.Empty;
    }
}
