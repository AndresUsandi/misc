import { logger } from './logger.js';

class ChatsitoApiClient {
    constructor(baseUrl = 'http://localhost:5257') {
        this.baseUrl = baseUrl;
        this.activeModel = '';
        this.availableModels = [];
        this.timeoutMins = 10;
        this.maxToolIterations = 20;
    }

    async initialize() {
        await this.loadConfig();
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
            logger.log(`Error in ChatsitoApiClient.loadConfig: ${err.message}`);
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

    async sendChat(messages, contextTokenSize, tools) {
        try {
            const payload = {
                model: this.activeModel,
                messages,
                contextTokenSize,
                tools
            };
            logger.log(`[ChatsitoApiClient] Sending POST /api/chat. Model: ${this.activeModel}. Context size: ${contextTokenSize}.`);
            
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
            logger.log(`[ChatsitoApiClient] Received response from /api/chat. Success: ${result.success}`);
            if (!result.success) {
                throw new Error(result.error || "Server returned unsuccessful response.");
            }
            return result;
        } catch (err) {
            logger.log(`Error in ChatsitoApiClient.sendChat: ${err.message}`);
            throw err;
        }
    }
}

export default ChatsitoApiClient;
