using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace chatsito.Core
{
    public static class Utils
    {
        public static int EstimateTokenCount(string text)
        {
            int tokens = 0;
            int currentWordLength = 0;

            foreach (char c in text)
            {
                if (char.IsLetterOrDigit(c))
                {
                    currentWordLength++;
                }
                else
                {
                    if (currentWordLength > 0)
                    {
                        tokens += Math.Max(1,
                            (currentWordLength + 3) / 4);

                        currentWordLength = 0;
                    }

                    if (!char.IsWhiteSpace(c))
                        tokens++;
                }
            }

            if (currentWordLength > 0)
            {
                tokens += Math.Max(1,
                    (currentWordLength + 3) / 4);
            }

            return tokens;
        }
    }
}