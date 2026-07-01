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

        const result = await manager.sendChat([{ role: 'user', content: 'hello' }], 2000, []);

        assert.strictEqual(mockFetchCalls.length, 1);
        const call = mockFetchCalls[0];
        assert.ok(call.url.endsWith('/api/chat'));
        assert.strictEqual(call.options.method, 'POST');
        assert.strictEqual(call.options.headers['Content-Type'], 'application/json');

        const body = JSON.parse(call.options.body);
        assert.strictEqual(body.model, 'chat-model');
        assert.deepStrictEqual(body.messages, [{ role: 'user', content: 'hello' }]);
        assert.strictEqual(body.contextTokenSize, 2000);
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
                await manager.sendChat([], 1000, []);
            },
            /Server returned error/
        );
    });
});
