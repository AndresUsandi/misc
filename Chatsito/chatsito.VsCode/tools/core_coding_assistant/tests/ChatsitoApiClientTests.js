const assert = require('assert');
const ChatsitoApiClient = require('../../../ChatsitoApiClient');

describe('ChatsitoApiClient Tests', () => {
    let originalFetch;
    let mockFetchCalls = [];
    let mockFetchResponse = {};
    let mockFetchStatus = 200;
    let mockFetchStatusText = 'OK';
    let mockFetchOk = true;
    let mockFetchText = '';

    beforeEach(() => {
        originalFetch = global.fetch;
        mockFetchCalls = [];
        mockFetchResponse = {};
        mockFetchStatus = 200;
        mockFetchStatusText = 'OK';
        mockFetchOk = true;
        mockFetchText = '';

        global.fetch = async (url, options) => {
            mockFetchCalls.push({ url, options });
            return {
                ok: mockFetchOk,
                status: mockFetchStatus,
                statusText: mockFetchStatusText,
                json: async () => mockFetchResponse,
                text: async () => mockFetchText
            };
        };
    });

    afterEach(() => {
        global.fetch = originalFetch;
    });

    it('should initialize with default empty values', () => {
        const manager = new ChatsitoApiClient();
        assert.strictEqual(manager.activeModel, '');
        assert.deepStrictEqual(manager.availableModels, []);
    });

    it('should load config and update activeModel', async () => {
        const manager = new ChatsitoApiClient();
        mockFetchResponse = { defaultModel: 'custom-model' };

        const config = await manager.loadConfig();

        assert.strictEqual(mockFetchCalls.length, 1);
        assert.ok(mockFetchCalls[0].url.endsWith('/api/config'));
        assert.deepStrictEqual(config, { defaultModel: 'custom-model' });
        assert.strictEqual(manager.activeModel, 'custom-model');
    });

    it('should handle config load failure gracefully', async () => {
        const manager = new ChatsitoApiClient();
        mockFetchOk = false;
        mockFetchStatus = 500;
        mockFetchStatusText = 'Internal Server Error';

        const config = await manager.loadConfig();

        assert.strictEqual(config, null);
        assert.strictEqual(manager.activeModel, '');
    });

    it('should load available models and fallback to first if activeModel is empty', async () => {
        const manager = new ChatsitoApiClient();
        mockFetchResponse = ['model-a', 'model-b'];

        const models = await manager.loadAvailableModels();

        assert.strictEqual(mockFetchCalls.length, 1);
        assert.ok(mockFetchCalls[0].url.endsWith('/api/models'));
        assert.deepStrictEqual(models, ['model-a', 'model-b']);
        assert.deepStrictEqual(manager.availableModels, ['model-a', 'model-b']);
        assert.strictEqual(manager.activeModel, 'model-a');
    });

    it('should load available models and retain activeModel if already set', async () => {
        const manager = new ChatsitoApiClient();
        manager.activeModel = 'model-b';
        mockFetchResponse = ['model-a', 'model-b'];

        const models = await manager.loadAvailableModels();

        assert.deepStrictEqual(models, ['model-a', 'model-b']);
        assert.strictEqual(manager.activeModel, 'model-b');
    });

    it('should send chat payload to backend', async () => {
        const manager = new ChatsitoApiClient();
        manager.activeModel = 'chat-model';
        mockFetchResponse = { success: true, message: { role: 'assistant', content: 'hello back' }, contextTokenSize: 100 };

        const result = await manager.sendChat([{ role: 'user', content: 'hello' }], []);

        assert.strictEqual(mockFetchCalls.length, 1);
        const call = mockFetchCalls[0];
        assert.ok(call.url.endsWith('/api/chat'));
        assert.strictEqual(call.options.method, 'POST');
        assert.strictEqual(call.options.headers['Content-Type'], 'application/json');

        const body = JSON.parse(call.options.body);
        assert.strictEqual(body.model, 'chat-model');
        assert.deepStrictEqual(body.messages, [{ role: 'user', content: 'hello' }]);
        assert.strictEqual(body.contextTokenSize, undefined);
        assert.strictEqual(body.options, undefined);
        assert.deepStrictEqual(body.tools, []);

        assert.deepStrictEqual(result, mockFetchResponse);
    });

    it('should throw error when sendChat fails', async () => {
        const manager = new ChatsitoApiClient();
        mockFetchOk = false;
        mockFetchStatus = 400;
        mockFetchText = 'Bad Request';

        await assert.rejects(
            async () => {
                await manager.sendChat([], []);
            },
            /Server returned error/
        );
    });

    it('should respect the chatsito.logThinking setting when it is false', async () => {
        const vscode = require('vscode');

        const originalGetConfiguration = vscode.workspace.getConfiguration;
        vscode.workspace.getConfiguration = (section) => {
            if (section === 'chatsito') {
                return {
                    get: (key, defaultValue) => {
                        if (key === 'logThinking') {
                            return false;
                        }
                        return defaultValue;
                    }
                };
            }
            return originalGetConfiguration(section);
        };

        try {
            const manager = new ChatsitoApiClient();
            manager.activeModel = 'chat-model';
            mockFetchResponse = { success: true, message: { role: 'assistant', content: 'hello back' }, contextTokenSize: 100 };

            await manager.sendChat([{ role: 'user', content: 'hello' }], []);

            assert.strictEqual(mockFetchCalls.length, 1);
            const body = JSON.parse(mockFetchCalls[0].options.body);
            assert.strictEqual(body.think, undefined);
        } finally {
            vscode.workspace.getConfiguration = originalGetConfiguration;
        }
    });

    it('should log to debug channel if configuration loading throws an error', async () => {
        const vscode = require('vscode');
        const logger = require('../../../logger');

        let debugLogCalled = false;
        let debugLogMsg = '';
        const originalLogDebug = logger.logDebug;
        logger.logDebug = (msg) => {
            debugLogCalled = true;
            debugLogMsg = msg;
        };

        const originalGetConfiguration = vscode.workspace.getConfiguration;
        vscode.workspace.getConfiguration = () => {
            throw new Error('Simulated config load error');
        };

        try {
            const manager = new ChatsitoApiClient();
            manager.activeModel = 'chat-model';
            mockFetchResponse = { success: true, message: { role: 'assistant', content: 'hello back' }, contextTokenSize: 100 };

            await manager.sendChat([{ role: 'user', content: 'hello' }], []);

            assert.strictEqual(debugLogCalled, true, 'Should have called logDebug');
            assert.ok(debugLogMsg.includes('Simulated config load error'), 'Log message should contain the config error');
        } finally {
            vscode.workspace.getConfiguration = originalGetConfiguration;
            logger.logDebug = originalLogDebug;
        }
    });

    it('should call estimateTokens API and return estimated count', async () => {
        const manager = new ChatsitoApiClient();
        mockFetchResponse = { count: 42 };

        const count = await manager.estimateTokens('Hello world');

        assert.strictEqual(mockFetchCalls.length, 1);
        const call = mockFetchCalls[0];
        assert.ok(call.url.endsWith('/api/estimate-tokens'));
        assert.strictEqual(call.options.method, 'POST');
        assert.deepStrictEqual(JSON.parse(call.options.body), { text: 'Hello world' });
        assert.strictEqual(count, 42);
    });

    it('should fallback to length-based approximation if estimateTokens API fails', async () => {
        const manager = new ChatsitoApiClient();
        mockFetchOk = false;
        mockFetchStatus = 500;

        const count = await manager.estimateTokens('Hello world');

        // 'Hello world' is 11 chars. Math.ceil(11 / 4) = 3.
        assert.strictEqual(count, 3);
    });

    it('should log config load failure to debug channel', async () => {
        const logger = require('../../../logger');
        let debugLogCalled = false;
        let debugLogMsg = '';
        const originalLogDebug = logger.logDebug;
        logger.logDebug = (msg) => {
            debugLogCalled = true;
            debugLogMsg = msg;
        };

        try {
            const manager = new ChatsitoApiClient();
            mockFetchOk = false;
            mockFetchStatus = 500;
            mockFetchStatusText = 'Internal Server Error';

            await manager.loadConfig();

            assert.strictEqual(debugLogCalled, true, 'Should have called logDebug');
            assert.ok(debugLogMsg.includes('Internal Server Error'), 'Log message should contain the config error');
        } finally {
            logger.logDebug = originalLogDebug;
        }
    });

    it('should retry initializing until config succeeds', async () => {
        const manager = new ChatsitoApiClient();
        manager.retryIntervalMs = 5; // 5ms for fast test execution

        let callCount = 0;
        global.fetch = async (url, options) => {
            callCount++;
            if (url.endsWith('/api/config')) {
                if (callCount < 3) {
                    return {
                        ok: false,
                        status: 500,
                        statusText: 'Temporary Server Error',
                        json: async () => ({}),
                        text: async () => ''
                    };
                } else {
                    return {
                        ok: true,
                        status: 200,
                        statusText: 'OK',
                        json: async () => ({ defaultModel: 'retry-model' }),
                        text: async () => ''
                    };
                }
            } else if (url.endsWith('/api/models')) {
                return {
                    ok: true,
                    status: 200,
                    statusText: 'OK',
                    json: async () => ['retry-model'],
                    text: async () => ''
                };
            }
            return { ok: false, status: 404 };
        };

        await manager.initialize();

        assert.strictEqual(manager.activeModel, 'retry-model');
        assert.ok(callCount >= 3, `Should have fetched multiple times, got: ${callCount}`);
    });
});
