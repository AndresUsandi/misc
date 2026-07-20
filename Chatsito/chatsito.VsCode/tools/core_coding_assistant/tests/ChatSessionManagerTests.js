const assert = require('assert');
const ChatSessionManager = require('../../../ChatSessionManager');

describe('ChatSessionManager Tests', () => {
    let mockContext;
    let manager;

    beforeEach(() => {
        mockContext = {
            workspaceState: {
                _data: {},
                get(key) {
                    return this._data[key];
                },
                update(key, value) {
                    this._data[key] = value;
                    return Promise.resolve();
                }
            },
            globalState: {
                _data: {},
                get(key) {
                    return this._data[key];
                },
                update(key, value) {
                    this._data[key] = value;
                    return Promise.resolve();
                }
            }
        };
        manager = new ChatSessionManager(mockContext);
    });

    it('should initialize with default empty values', () => {
        const state = manager.getState();
        assert.deepStrictEqual(state.conversationHistory, []);
        assert.strictEqual(state.contextTokenSize, 16384);
        assert.strictEqual(state.selectedMode, 'hybrid');
        assert.deepStrictEqual(state.pendingToolResults, {});
        assert.deepStrictEqual(state.pendingApprovals, []);
        assert.deepStrictEqual(state.previousPrompts, []);
        assert.deepStrictEqual(state.availableModels, []);
    });

    it('should start a new session properly', () => {
        manager.conversationHistory.push({ role: 'user', content: 'hello' });
        manager.contextTokenSize = 32768;
        manager.startNewSession({ activeModel: 'test-model', selectedMode: 'plan' });

        const state = manager.getState();
        assert.deepStrictEqual(state.conversationHistory, []);
        assert.strictEqual(state.contextTokenSize, 16384);
        assert.strictEqual(state.activeModel, 'test-model');
        assert.strictEqual(state.selectedMode, 'plan');
    });

    it('should reset session', () => {
        manager.conversationHistory.push({ role: 'user', content: 'test' });
        manager.resetSession();

        const state = manager.getState();
        assert.deepStrictEqual(state.conversationHistory, []);
        assert.strictEqual(state.contextTokenSize, 16384);
    });

    it('should export and import session state', () => {
        manager.conversationHistory = [
            { role: 'user', content: 'hi' },
            { role: 'assistant', content: 'hello' }
        ];
        manager.contextTokenSize = 32768;
        manager.activeModel = 'model-abc';
        manager.selectedMode = 'execution';
        manager.previousPrompts = ['hi'];

        const exported = manager.exportSession();

        const manager2 = new ChatSessionManager(mockContext);
        manager2.importSession(exported);

        const state2 = manager2.getState();
        assert.deepStrictEqual(state2.conversationHistory, [
            { role: 'user', content: 'hi' },
            { role: 'assistant', content: 'hello' }
        ]);
        assert.strictEqual(state2.contextTokenSize, 32768);
        assert.strictEqual(state2.activeModel, 'model-abc');
        assert.strictEqual(state2.selectedMode, 'execution');
        assert.deepStrictEqual(state2.previousPrompts, ['hi']);
    });

    it('should save and restore session to/from workspaceState', async () => {
        manager.conversationHistory = [
            { role: 'user', content: 'save me' }
        ];
        manager.activeModel = 'persistence-model';
        
        const sessionId = await manager.saveSession('My Session');
        assert.ok(sessionId, 'Should return a sessionId');

        // Check metadata loaded
        assert.strictEqual(manager.savedSessionMetadata.length, 1);
        assert.strictEqual(manager.savedSessionMetadata[0].name, 'My Session');

        // Recreate manager with the same context
        const manager2 = new ChatSessionManager(mockContext);
        assert.strictEqual(manager2.savedSessionMetadata.length, 1);

        const restored = await manager2.restoreSession(sessionId);
        assert.strictEqual(restored, true);

        const state2 = manager2.getState();
        assert.deepStrictEqual(state2.conversationHistory, [
            { role: 'user', content: 'save me' }
        ]);
        assert.strictEqual(state2.activeModel, 'persistence-model');
    });

    it('should execute tools successfully', async () => {
        // Test searchWorkspace tool execution route (which fails gracefully on missing params/no query instead of throwing)
        const result = await manager.toolManager.executeTool('searchWorkspace', {});
        assert.ok(result.includes('Error'), 'Should fail gracefully with an Error message on missing parameter');
    });

    it('should call continueSession and communicate with the client', async () => {
        manager.chatsitoApiClient.sendChat = async () => {
            return {
                success: true,
                message: { role: 'assistant', content: 'Response content' },
                contextTokenSize: 4096
            };
        };

        const mockClient = {
            progressCalls: [],
            stateUpdates: 0,
            cycleFinishedCalled: false,
            errorCalls: [],
            sendProgress(text) {
                this.progressCalls.push(text);
            },
            sendStateUpdate() {
                this.stateUpdates++;
            },
            sendCycleFinished() {
                this.cycleFinishedCalled = true;
            },
            sendError(msg) {
                this.errorCalls.push(msg);
            }
        };

        await manager.continueSession('Test user prompt', mockClient);

        assert.strictEqual(mockClient.stateUpdates, 2); // Initial user prompt push + assistant response push
        assert.ok(mockClient.progressCalls.includes('Chatsito is thinking...'));
        assert.strictEqual(mockClient.cycleFinishedCalled, true);
        assert.strictEqual(mockClient.errorCalls.length, 0);
    });

    it('should persist activeModel and selectedMode in globalState', async () => {
        manager.activeModel = 'persisted-model-123';
        manager.selectedMode = 'plan';

        assert.strictEqual(mockContext.globalState.get('chatsito.activeModel'), 'persisted-model-123');
        assert.strictEqual(mockContext.globalState.get('chatsito.selectedMode'), 'plan');

        // Create new manager instance with same mockContext state
        const manager2 = new ChatSessionManager(mockContext);
        assert.strictEqual(manager2.selectedMode, 'plan');
        
        // Mock client calls to return our persisted model list
        manager2.chatsitoApiClient.loadAvailableModels = async () => {
            manager2.chatsitoApiClient.availableModels = ['persisted-model-123'];
            return manager2.chatsitoApiClient.availableModels;
        };
        manager2.chatsitoApiClient.loadConfig = async () => { return {}; };
        
        await manager2.initializeApiClient();
        assert.strictEqual(manager2.activeModel, 'persisted-model-123');
    });

    it('should log critical warning when doneReason indicates cutoff', async () => {
        const logger = require('../../../logger');
        let criticalLogCalled = false;
        let criticalLogMsg = '';
        const originalLogCritical = logger.logCritical;
        logger.logCritical = (msg) => {
            criticalLogCalled = true;
            criticalLogMsg = msg;
        };

        try {
            manager.chatsitoApiClient.sendChat = async () => {
                return {
                    success: true,
                    message: { 
                        role: 'assistant', 
                        content: '', 
                        thinking: 'Reasoning process cut off at line...' 
                    },
                    doneReason: 'length',
                    contextTokenSize: 4096
                };
            };

            manager.chatsitoApiClient.estimateTokens = async () => {
                return 10;
            };

            const mockClient = {
                sendProgress() {},
                sendStateUpdate() {},
                sendCycleFinished() {},
                sendError() {}
            };

            await manager.continueSession('Test prompt', mockClient);

            assert.strictEqual(criticalLogCalled, true, 'Should have logged a critical warning');
            assert.ok(criticalLogMsg.includes('stopped prematurely'), 'Warning should report premature stop');
            assert.ok(criticalLogMsg.includes('length'), 'Warning should report doneReason: length');
            assert.ok(criticalLogMsg.includes('Thinking Token Estimate: ~10 tokens'), 'Warning should include thinking token estimate');
        } finally {
            logger.logCritical = originalLogCritical;
        }
    });
});
