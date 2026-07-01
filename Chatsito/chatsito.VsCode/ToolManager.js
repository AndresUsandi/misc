const logger = require('./logger');
const ToolDefinitionProvider = require('./ToolDefinitionProvider');

class ToolManager {
    constructor() {
        this.tools = new Map();
        this.registerAllTools();
    }

    registerTool(name, definition, implementation) {
        this.tools.set(name, { definition, implementation });
    }

    getToolsDefinition() {
        const definitions = [];
        for (const [name, tool] of this.tools.entries()) {
            definitions.push({
                type: "function",
                function: tool.definition
            });
        }
        return definitions;
    }

    async executeTool(name, args) {
        const tool = this.tools.get(name);
        if (!tool) {
            throw new Error(`Unknown tool: ${name}`);
        }
        if (!tool.implementation) {
            throw new Error(`Tool ${name} cannot be executed by ToolManager directly.`);
        }

        try {
            return await tool.implementation(args);
        } catch (err) {
            logger.log(`Error executing tool ${name}: ${err.message}`);
            return `Error: ${err.message}`;
        }
    }

    registerAllTools() {
        const tools = ToolDefinitionProvider.getTools();
        
        for (const def of tools) {
            let implementation = null;
            if (!def.isPatchingTool) {
                const rawImpl = require(def.modulePath);
                implementation = async (args) => await def.adapter(args, rawImpl);
            }
            this.registerTool(def.name, def.schema, implementation);
        }
    }
}

module.exports = ToolManager;
