using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;

namespace chatsito.Web
{
    public static class ToolDefinitionProvider
    {
        public static List<object> GetTools()
        {
            return new List<object>
            {
                new
                {
                    type = "function",
                    function = new
                    {
                        name = "search_web",
                        description = "Performs a web search for a given query. Returns a summary of relevant information along with URL citations. Use this when you need up-to-date information, news, or factual answers that you don't know.",
                        parameters = new
                        {
                            type = "object",
                            properties = new
                            {
                                query = new
                                {
                                    type = "string",
                                    description = "The search query to look up on the internet."
                                }
                            },
                            required = new[] { "query" }
                        }
                    }
                },
                new
                {
                    type = "function",
                    function = new
                    {
                        name = "get_current_date_time",
                        description = "Gets the current date and time.",
                        parameters = new
                        {
                            type = "object",
                            properties = new { },
                            required = Array.Empty<string>()
                        }
                    }
                },
                new
                {
                    type = "function",
                    function = new
                    {
                        name = "execute_http_request",
                        description = "Executes an arbitrary HTTP request (GET or POST) and returns the raw response body. Use this to fetch specific URLs, interact with APIs, or follow up on search results. You must parse the raw result yourself."
                        + " NOTE: please use sparringly. Unlike the search_web tool, this tool causes the context window to explode and provides a suboptimal user experience. Only execute this tool if it is strictly necessary or if the user explicitly asks you to look for something online.",
                        parameters = new
                        {
                            type = "object",
                            properties = new
                            {
                                url = new { type = "string", description = "The full URL to request." },
                                method = new { type = "string", description = "The HTTP method (GET or POST)." },
                                body = new { type = "string", description = "The request body for POST requests (optional)." }
                            },
                            required = new[] { "url", "method" }
                        }
                    }
                }
            };
        }

        public static async Task<string> ExecuteToolAsync(string name, IDictionary<string, object>? arguments)
        {
            if (name == "search_web")
            {
                string query = "";
                if (arguments != null && arguments.TryGetValue("query", out var queryObj) && queryObj != null)
                {
                    query = queryObj.ToString() ?? "";
                }
                return await ExecuteWebSearchAsync(query);
            }
            else if (name == "get_current_date_time")
            {
                return DateTime.Now.ToString("f");
            }
            else if (name == "execute_http_request")
            {
                string url = "";
                string method = "GET";
                string body = "";


                if (arguments != null)
                {
                    if (arguments.TryGetValue("url", out var urlObj) && urlObj != null) url = urlObj.ToString() ?? "";
                    if (arguments.TryGetValue("method", out var methodObj) && methodObj != null) method = methodObj.ToString() ?? "GET";
                    if (arguments.TryGetValue("body", out var bodyObj) && bodyObj != null) body = bodyObj.ToString() ?? "";
                }


                return await ExecuteHttpRequestAsync(url, method, body);
            }

            return $"Error: Tool '{name}' not found.";
        }

        private static async Task<string> ExecuteHttpRequestAsync(string url, string method, string body)
        {
            try
            {
                using var client = new HttpClient();
                client.DefaultRequestHeaders.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36");


                HttpResponseMessage response;
                if (method.Equals("POST", StringComparison.OrdinalIgnoreCase))
                {
                    var content = new StringContent(body);
                    response = await client.PostAsync(url, content);
                }
                else
                {
                    response = await client.GetAsync(url);
                }


                if (!response.IsSuccessStatusCode)
                {
                    return $"HTTP Error: {(int)response.StatusCode} {response.ReasonPhrase}\n" + await response.Content.ReadAsStringAsync();
                }


                return await response.Content.ReadAsStringAsync();
            }
            catch (Exception ex)
            {
                return $"Error executing HTTP request: {ex.Message}";
            }
        }

        private static async Task<string> ExecuteWebSearchAsync(string query)
        {
            try
            {
                using var client = new HttpClient();
                client.DefaultRequestHeaders.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36");
                var content = new FormUrlEncodedContent(new[] { new KeyValuePair<string, string>("q", query) });
                var response = await client.PostAsync("https://lite.duckduckgo.com/lite/", content);
                response.EnsureSuccessStatusCode();
                var html = await response.Content.ReadAsStringAsync();

                var results = new List<string>();


                var titleRegex = new System.Text.RegularExpressions.Regex(@"<a rel=""nofollow"" href=""([^""]+)"" class='result-link'>([^<]+)</a>");
                var snippetRegex = new System.Text.RegularExpressions.Regex(@"<td class='result-snippet'>([\s\S]*?)</td>");


                var titles = titleRegex.Matches(html);
                var snippets = snippetRegex.Matches(html);

                for (int i = 0; i < Math.Min(3, Math.Min(snippets.Count, titles.Count)); i++)
                {
                    string url = titles[i].Groups[1].Value;
                    string title = titles[i].Groups[2].Value.Trim();
                    string snippet = System.Text.RegularExpressions.Regex.Replace(snippets[i].Groups[1].Value, "<[^>]+>", "").Trim();
                    results.Add($"{i + 1}. {title}\nURL: {url}\nSnippet: {snippet}");
                }

                if (results.Count == 0)
                {
                    var ahrefs = System.Text.RegularExpressions.Regex.Matches(html, @"<a class=""result-snippet""[^>]*href=""([^""]+)""[^>]*>(.*?)</a>", System.Text.RegularExpressions.RegexOptions.Singleline);
                    int count = 0;
                    foreach (System.Text.RegularExpressions.Match m in ahrefs)
                    {
                        if (count >= 3) break;
                        string url = m.Groups[1].Value;
                        string title = System.Text.RegularExpressions.Regex.Replace(m.Groups[2].Value, "<[^>]+>", "").Trim();
                        results.Add($"{++count}. {title}\nURL: {url}");
                    }
                }

                if (results.Count == 0)
                {
                    return "No results found or unable to parse search engine results.";
                }

                return string.Join("\n\n", results);
            }
            catch (Exception ex)
            {
                return $"Error executing web search: {ex.Message}";
            }
        }
    }
}
