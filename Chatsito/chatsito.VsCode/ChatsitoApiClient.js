const logger = require('./logger');

class ChatsitoApiClient {
    constructor(baseUrl = 'http://localhost:5257') {
        this.baseUrl = baseUrl;
        this.activeModel = '';
        this.availableModels = [];
        this.timeoutMins = 10;
        this.maxToolIterations = 20;
        this.retryIntervalMs = (typeof global.describe === 'function') ? 0 : 30000;
    }

    async initialize() {
        let config = null;
        while (!config) {
            config = await this.loadConfig();
            if (!config) {
                if (this.retryIntervalMs <= 0) {
                    break;
                }
                await new Promise(resolve => setTimeout(resolve, this.retryIntervalMs));
            }
        }
        await this.loadAvailableModels();
    }

    async loadConfig() {
        try {
            const response = await fetch(`${this.baseUrl}/api/config`);
            if (response.ok) {
                const config = await response.json();
                if (config && config.defaultModel) {
                    this.activeModel = config.defaultModel;
                }
                if (config && config.timeoutMins) {
                    this.timeoutMins = config.timeoutMins;
                }
                if (config && config.maxToolIterations !== undefined) {
                    this.maxToolIterations = config.maxToolIterations;
                }
                return config;
            }
            throw new Error(`Failed to fetch config: ${response.statusText}`);
        } catch (err) {
            logger.logDebug(`Error in ChatsitoApiClient.loadConfig: ${err.message}`);
        }
        return null;
    }

    async loadAvailableModels() {
        try {
            const response = await fetch(`${this.baseUrl}/api/models`);
            if (response.ok) {
                this.availableModels = await response.json();
                if (!this.activeModel && this.availableModels.length > 0) {
                    this.activeModel = this.availableModels[0];
                }
                return this.availableModels;
            }
            throw new Error(`Failed to fetch models: ${response.statusText}`);
        } catch (err) {
            logger.log(`Error in ChatsitoApiClient.loadAvailableModels: ${err.message}`);
        }
        return [];
    }

    async sendChat(messages, tools) {
        let logThinking = false;
        try {
            const vscode = require('vscode');
            const config = vscode.workspace.getConfiguration('chatsito');
            logThinking = config.get('logThinking', true);
        } catch (e) {
            logger.logDebug(`[ChatsitoApiClient] VS Code configuration load error/fallback: ${e.message}`);
        }

        const thinkFallbacks = logThinking ? ['high', true, false, null] : [null];
        let lastError = null;

        for (const thinkVal of thinkFallbacks) {
            try {
                const payload = {
                    model: this.activeModel,
                    messages,
                    tools
                };
                if (thinkVal !== null) {
                    payload.think = thinkVal;
                }

                logger.log(`[ChatsitoApiClient] Sending POST /api/chat. Model: ${this.activeModel}. Think: ${thinkVal}: Last Message: ${logger.formatJson(messages[messages.length - 1])}`);

                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.timeoutMins * 60 * 1000);

                let response;
                try {
                    response = await fetch(`${this.baseUrl}/api/chat`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(payload),
                        signal: controller.signal
                    });
                } finally {
                    clearTimeout(timeoutId);
                }

                if (!response.ok) {
                    const text = await response.text();
                    throw new Error(`Server returned error (${response.status}): ${text}`);
                }

                const result = await response.json();
                logger.log(`[ChatsitoApiClient] Received response from /api/chat. Response: ${logger.formatJson(result)}`);
                if (!result.success) {
                    throw new Error(result.error || "Server returned unsuccessful response.");
                }
                return result;
            } catch (err) {
                lastError = err;
                logger.log(`[ChatsitoApiClient] Request with think: ${thinkVal} failed: ${err.message}. Trying next fallback...`);
            }
        }

        throw lastError || new Error("Failed to send chat message after trying all think fallbacks.");
    }

    async estimateTokens(text) {
        if (!text) return 0;
        try {
            const response = await fetch(`${this.baseUrl}/api/estimate-tokens`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text })
            });

            if (!response.ok) {
                const errText = await response.text();
                throw new Error(`Server error: ${errText}`);
            }

            const result = await response.json();
            return result.count || 0;
        } catch (err) {
            logger.logDebug(`[ChatsitoApiClient] estimateTokens error/fallback: ${err.message}`);
            // Fallback estimation: roughly 4 characters per token
            return Math.ceil(text.length / 4);
        }
    }
}

module.exports = ChatsitoApiClient;
