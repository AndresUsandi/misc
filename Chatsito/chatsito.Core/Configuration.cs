using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace chatsito.Core
{
    public static class Configuration
    {
        public const int DefaultKeepAliveHours = 48;
        public const string DefaultOllamaUrl = "http://localhost:11434";
        public const float TokenMargin = 1.25f;
        public const int TokenResponse = 2048;
        public const int TokenMin = 1024 * 64;
        public const int TokenMax = 1024 * 64;
        public const int TimeoutMins = 10;
        public const int MaxToolIterations = 20;
    }
}