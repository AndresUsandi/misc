class ToolDefinitionProvider {
    constructor() {
        this.tools = [
            {
                name: 'searchWorkspace',
                category: 'Coding Assistant',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/core_coding_assistant/searchWorkspace',
                adapter: async (args, impl) => await impl(args.query, args.fileGlob),
                getProgressText: args => 'Searching workspace for "' + (args.query || '') + '"...',
                schema: {
                    name: "searchWorkspace",
                    description: "Searches the current workspace files recursively for a specific text, code query, or symbol name. Returns matching lines and file paths. NOTE: Search is literal by default. Filter glob paths must use forward slashes.",
                    parameters: {
                        type: "object",
                        properties: {
                            query: {
                                type: "string",
                                description: "The literal text, keyword, or code symbol to search for in workspace files."
                            },
                            fileGlob: {
                                type: "string",
                                description: "Optional glob pattern to restrict target files, e.g. '**/*.cs' or '**/*.js'. Relative to the workspace root."
                            }
                        },
                        required: ["query"]
                    }
                }
            },
            {
                name: 'getFullGraph',
                category: 'Coding Assistant',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/core_coding_assistant/getFullGraph',
                adapter: async (args, impl) => await impl(args.filePath, parseInt(args.lineNumber, 10), parseInt(args.characterNumber || '1', 10)),
                getProgressText: args => 'Generating full dependency call graph...',
                schema: {
                    name: "getFullGraph",
                    description: "Generates a full backward invocation dependency tree (call graph) for a symbol at a specific location, listing all callers recursively up to the root caller methods. Detects and stops on circular dependencies.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: {
                                type: "string",
                                description: "The relative or absolute file path containing the symbol. Must point to a file that exists."
                            },
                            lineNumber: {
                                type: "integer",
                                description: "The 1-based line number of the symbol declaration or reference (1 represents the first line). Must be positive."
                            },
                            characterNumber: {
                                type: "integer",
                                description: "Optional. The 1-based character/column offset of the symbol on that line (1 represents the first character). Must be positive. Defaults to 1."
                            }
                        },
                        required: ["filePath", "lineNumber"]
                    }
                }
            },
            {
                name: 'getCurrentEditorContext',
                category: 'Coding Assistant',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/core_coding_assistant/getCurrentEditorContext',
                adapter: async (args, impl) => await impl(),
                getProgressText: args => 'Getting current editor context...',
                schema: {
                    name: "getCurrentEditorContext",
                    description: "Gets the context (file path, cursor line, selected text, and surrounding code lines) of the active document in the editor.",
                    parameters: {
                        type: "object",
                        properties: {}
                    }
                }
            },
            {
                name: 'readFile',
                category: 'Coding Assistant',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/core_coding_assistant/readFile',
                adapter: async (args, impl) => await impl(args.filePath),
                getProgressText: args => 'Reading file ' + (args.filePath || '') + '...',
                schema: {
                    name: "readFile",
                    description: "Reads the entire content of a file in the workspace. Use this to inspect file contents before editing or analyzing. File must exist on disk.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: {
                                type: "string",
                                description: "The relative or absolute path of the file to read. Ensure correct capitalization and slashes."
                            }
                        },
                        required: ["filePath"]
                    }
                }
            },
            {
                name: 'getContextAtLocation',
                category: 'Coding Assistant',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/core_coding_assistant/getContextAtLocation',
                adapter: async (args, impl) => await impl(args.filePath, Math.max(0, parseInt(args.line, 10) - 1), Math.max(0, parseInt(args.character, 10) - 1), parseInt(args.callStackLevel || '2', 10)),
                getProgressText: args => 'Getting context at location ' + (args.filePath || '') + ':' + (args.line || 0) + '...',
                schema: {
                    name: "getContextAtLocation",
                    description: "Gets the code context (e.g. method/class body) enclosing the specified 1-based line and character location, and traces its callers recursively. Useful for understanding symbol context.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: {
                                type: "string",
                                description: "The relative or absolute path of the file containing the symbol. Must exist on disk."
                            },
                            line: {
                                type: "integer",
                                description: "The 1-based line number inside the file (1 is the first line). Must be positive."
                            },
                            character: {
                                type: "integer",
                                description: "The 1-based character/column position on the line (1 is the first column). Must be positive."
                            },
                            callStackLevel: {
                                type: "integer",
                                description: "Optional. Number of call stack levels to trace recursively. Defaults to 2."
                            }
                        },
                        required: ["filePath", "line", "character"]
                    }
                }
            },
            {
                name: 'findDefinition',
                category: 'Coding Assistant',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/core_coding_assistant/findDefinition',
                adapter: async (args, impl) => await impl(args.filePath, Math.max(0, parseInt(args.line, 10) - 1), Math.max(0, parseInt(args.character, 10) - 1)),
                getProgressText: args => 'Finding definition...',
                schema: {
                    name: "findDefinition",
                    description: "Finds the definition location (file, range) of the symbol at the given 1-based line and character location using language server providers.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: {
                                type: "string",
                                description: "The relative or absolute path of the file containing the symbol reference. Must exist."
                            },
                            line: {
                                type: "integer",
                                description: "The 1-based line number where the reference is located (1 is the first line). Must be positive."
                            },
                            character: {
                                type: "integer",
                                description: "The 1-based character/column position of the symbol reference (1 is the first column). Must be positive."
                            }
                        },
                        required: ["filePath", "line", "character"]
                    }
                }
            },
            {
                name: 'findReferences',
                category: 'Coding Assistant',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/core_coding_assistant/findReferences',
                adapter: async (args, impl) => await impl(args.filePath, Math.max(0, parseInt(args.line, 10) - 1), Math.max(0, parseInt(args.character, 10) - 1)),
                getProgressText: args => 'Finding references...',
                schema: {
                    name: "findReferences",
                    description: "Finds all references (locations and line texts) of the symbol at the given 1-based line and character location across the workspace.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: {
                                type: "string",
                                description: "The relative or absolute path of the file containing the symbol reference. Must exist."
                            },
                            line: {
                                type: "integer",
                                description: "The 1-based line number where the reference is located (1 is the first line). Must be positive."
                            },
                            character: {
                                type: "integer",
                                description: "The 1-based character/column position of the symbol reference (1 is the first column). Must be positive."
                            }
                        },
                        required: ["filePath", "line", "character"]
                    }
                }
            },
            {
                name: 'getSymbolsInFile',
                category: 'Coding Assistant',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/core_coding_assistant/getSymbolsInFile',
                adapter: async (args, impl) => await impl(args.filePath),
                getProgressText: args => 'Getting symbols in ' + (args.filePath || '') + '...',
                schema: {
                    name: "getSymbolsInFile",
                    description: "Gets structural symbols (classes, methods, variables, interface declarations, etc.) defined in a specific file. Target file must exist.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: {
                                type: "string",
                                description: "The relative or absolute path of the file."
                            }
                        },
                        required: ["filePath"]
                    }
                }
            },
            {
                name: 'getDiagnostics',
                category: 'Coding Assistant',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/core_coding_assistant/getDiagnostics',
                adapter: async (args, impl) => await impl(args.filePath),
                getProgressText: args => 'Getting diagnostics...',
                schema: {
                    name: "getDiagnostics",
                    description: "Gets the active compiler/linter diagnostics (errors, warnings, hints, etc.) in the workspace or for a specific file.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: {
                                type: "string",
                                description: "Optional relative or absolute path of the file to filter diagnostics. If omitted, returns diagnostics for the entire workspace."
                            }
                        }
                    }
                }
            },
            {
                name: 'searchWeb',
                category: 'Misc',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/misc/webSearch',
                adapter: async (args, impl) => await impl(args.query),
                getProgressText: args => 'Searching the web for "' + (args.query || '') + '"...',
                schema: {
                    name: "searchWeb",
                    description: "Performs a web search for a given query. Returns a summary of relevant information along with URL citations. Use this when you need up-to-date information, news, or factual answers that you don't know.",
                    parameters: {
                        type: "object",
                        properties: {
                            query: {
                                type: "string",
                                description: "The search query to look up on the internet."
                            }
                        },
                        required: ["query"]
                    }
                }
            },
            {
                name: 'getCurrentDateTime',
                category: 'Misc',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/misc/getCurrentDateTime',
                adapter: async (args, impl) => await impl(args),
                getProgressText: args => 'Getting current date and time...',
                schema: {
                    name: "getCurrentDateTime",
                    description: "Gets the current date and time. Use this to determine the current date, time, and day of the week if you are unsure.",
                    parameters: {
                        type: "object",
                        properties: {},
                        required: []
                    }
                }
            },
            {
                name: 'executeHttpRequest',
                category: 'Misc',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/misc/executeHttpRequest',
                adapter: async (args, impl) => await impl(args.url, args.method, args.body),
                getProgressText: args => 'Executing HTTP request to "' + (args.url || '') + '"...',
                schema: {
                    name: "executeHttpRequest",
                    description: "Executes an arbitrary HTTP request (GET or POST) and returns the raw response body. Use this to fetch specific URLs, interact with APIs, or follow up on search results. You must parse the raw result yourself."
                        + " NOTE: please use sparringly. Unlike the search_web tool, this tool causes the context window to explode and provides a suboptimal user experience. Only execute this tool if it is strictly necessary or if the user explicitly asks you to look for something online.",
                    parameters: {
                        type: "object",
                        properties: {
                            url: { type: "string", description: "The full URL to request." },
                            method: { type: "string", description: "The HTTP method (GET or POST)." },
                            body: { type: "string", description: "The request body for POST requests (optional)." }
                        },
                        required: ["url", "method"]
                    }
                }
            },
        ];
    }

    getTools() {
        return this.tools;
    }

    getToolDefinition(name) {
        return this.tools.find(t => t.name === name);
    }
}

export default new ToolDefinitionProvider();
