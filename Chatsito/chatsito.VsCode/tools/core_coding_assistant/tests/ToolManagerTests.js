const assert = require('assert');
const ToolManager = require('../../../ToolManager');

describe('ToolManager Tests', () => {
    let toolManager;

    beforeEach(() => {
        toolManager = new ToolManager();
    });

    it('should register all 57 tools on construction', () => {
        assert.strictEqual(toolManager.tools.size, 57);
        assert.ok(toolManager.tools.has('search_workspace'));
        assert.ok(toolManager.tools.has('get_full_graph'));
        assert.ok(toolManager.tools.has('get_current_editor_context'));
        assert.ok(toolManager.tools.has('read_file'));
        assert.ok(toolManager.tools.has('get_context_at_location'));
        assert.ok(toolManager.tools.has('find_definition'));
        assert.ok(toolManager.tools.has('find_references'));
        assert.ok(toolManager.tools.has('get_symbols_in_file'));
        assert.ok(toolManager.tools.has('get_diagnostics'));
        assert.ok(toolManager.tools.has('insert_code'));
        assert.ok(toolManager.tools.has('replace_code'));
        assert.ok(toolManager.tools.has('delete_code'));
        assert.ok(toolManager.tools.has('rename_symbol'));
        assert.ok(toolManager.tools.has('move_file'));
        assert.ok(toolManager.tools.has('move_type'));
        assert.ok(toolManager.tools.has('extract_method'));
        assert.ok(toolManager.tools.has('format_file'));
        assert.ok(toolManager.tools.has('organize_imports'));

        // New category tools check
        assert.ok(toolManager.tools.has('search_knowledge'));
        assert.ok(toolManager.tools.has('run_command'));
        assert.ok(toolManager.tools.has('create_plan'));
        assert.ok(toolManager.tools.has('find_symbol'));
        assert.ok(toolManager.tools.has('search_docs'));
        assert.ok(toolManager.tools.has('get_project_dependencies'));
    });

    it('should format tool definitions correctly for the model', () => {
        const definitions = toolManager.getToolsDefinition();
        assert.strictEqual(definitions.length, 57);
        
        definitions.forEach(def => {
            assert.strictEqual(def.type, 'function');
            assert.ok(def.function);
            assert.ok(def.function.name);
            assert.ok(def.function.description);
            assert.ok(def.function.parameters);
        });

        const searchDef = definitions.find(d => d.function.name === 'search_workspace');
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
