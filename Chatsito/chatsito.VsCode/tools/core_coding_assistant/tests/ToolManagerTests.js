const assert = require('assert');
const ToolManager = require('../../../ToolManager');

describe('ToolManager Tests', () => {
    let toolManager;

    beforeEach(() => {
        toolManager = new ToolManager();
    });

    it('should register all 68 tools on construction', () => {
        assert.strictEqual(toolManager.tools.size, 68);
        assert.ok(toolManager.tools.has('searchWorkspace'));
        assert.ok(toolManager.tools.has('getFullGraph'));
        assert.ok(toolManager.tools.has('getCurrentEditorContext'));
        assert.ok(toolManager.tools.has('readFile'));
        assert.ok(toolManager.tools.has('getContextAtLocation'));
        assert.ok(toolManager.tools.has('findDefinition'));
        assert.ok(toolManager.tools.has('findReferences'));
        assert.ok(toolManager.tools.has('getSymbolsInFile'));
        assert.ok(toolManager.tools.has('getDiagnostics'));
        assert.ok(toolManager.tools.has('insertCode'));
        assert.ok(toolManager.tools.has('replaceCode'));
        assert.ok(toolManager.tools.has('deleteCode'));
        assert.ok(toolManager.tools.has('renameSymbol'));
        assert.ok(toolManager.tools.has('moveFile'));
        assert.ok(toolManager.tools.has('moveType'));
        assert.ok(toolManager.tools.has('extractMethod'));
        assert.ok(toolManager.tools.has('formatFile'));
        assert.ok(toolManager.tools.has('organizeImports'));

        // New category tools check
        assert.ok(toolManager.tools.has('searchKnowledge'));
        assert.ok(toolManager.tools.has('runCommand'));
        assert.ok(toolManager.tools.has('createPlan'));
        assert.ok(toolManager.tools.has('findSymbol'));
        assert.ok(toolManager.tools.has('searchDocs'));
        assert.ok(toolManager.tools.has('getProjectDependencies'));
    });

    it('should format tool definitions correctly for the model', () => {
        const definitions = toolManager.getToolsDefinition();
        assert.strictEqual(definitions.length, 68);
        
        definitions.forEach(def => {
            assert.strictEqual(def.type, 'function');
            assert.ok(def.function);
            assert.ok(def.function.name);
            assert.ok(def.function.description);
            assert.ok(def.function.parameters);
        });

        const searchDef = definitions.find(d => d.function.name === 'searchWorkspace');
        assert.ok(searchDef);
        assert.strictEqual(searchDef.function.description.includes('Searches the current workspace'), true);
    });

    it('should throw an error for unknown tool execution', async () => {
        await assert.rejects(
            async () => {
                await toolManager.executeTool('nonexistent_tool', {});
            },
            /Unknown tool: nonexistent_tool/
        );
    });

    it('should execute a custom registered tool and return its value', async () => {
        toolManager.registerTool('test_tool', { name: 'test_tool', description: 'desc', parameters: {} }, async (args) => {
            return `Hello ${args.user}`;
        });

        const result = await toolManager.executeTool('test_tool', { user: 'Antigravity' });
        assert.strictEqual(result, 'Hello Antigravity');
    });

    it('should catch runtime errors gracefully and return error string', async () => {
        toolManager.registerTool('buggy_tool', { name: 'buggy_tool', description: 'desc', parameters: {} }, async () => {
            throw new Error('Something failed');
        });

        const result = await toolManager.executeTool('buggy_tool', {});
        assert.strictEqual(result, 'Error: Something failed');
    });
});
