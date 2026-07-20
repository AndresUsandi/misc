class ToolDefinitionProvider {
    constructor() {
        this.tools = [
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
                adapter: async (args, impl) => await impl.getContextAtLocation(args.filePath, Math.max(0, parseInt(args.line, 10) - 1), Math.max(0, parseInt(args.character, 10) - 1), parseInt(args.callStackLevel || '2', 10)),
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
                name: 'insertCode',
                category: 'Uncategorized',
                isDestructive: true,
                isPatchingTool: true,
                modulePath: './tools/code_modification/insertCode',
                adapter: async (args, impl) => await impl(args),
                getProgressText: args => 'Inserting code in ' + (args.filePath || '') + '...',
                schema: {
                    name: "insertCode",
                    description: "Inserts code at a validated 1-based line and character location in a file. Target file must exist on disk.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: { type: "string", description: "The relative or absolute path of the file." },
                            line: { type: "integer", description: "The 1-based line number where the insertion starts (1 is the first line). Must be positive." },
                            character: { type: "integer", description: "The 1-based character offset on the line (1 is the first character). Must be positive." },
                            textToInsert: { type: "string", description: "The code text to insert." }
                        },
                        required: ["filePath", "line", "character", "textToInsert"]
                    }
                }
            },
            {
                name: 'replaceCode',
                category: 'Uncategorized',
                isDestructive: true,
                isPatchingTool: true,
                modulePath: './tools/code_modification/replaceCode',
                adapter: async (args, impl) => await impl(args),
                getProgressText: args => 'Replacing code in ' + (args.filePath || '') + '...',
                schema: {
                    name: "replaceCode",
                    description: "Replaces a validated range of code with new, modified code. CRITICAL: The new code ('textToReplace') must be different from the original code ('expectedOriginalText'). A replacement that is identical to the original text will be rejected as it results in no changes.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: { type: "string", description: "The relative or absolute path of the file." },
                            startLine: { type: "integer", description: "The 1-based start line of the range to replace (inclusive)." },
                            startChar: { type: "integer", description: "Optional. The 1-based start character offset of the range (inclusive, 1 is the first character). If omitted, the replacement starts from character 1 of startLine." },
                            endLine: { type: "integer", description: "The 1-based end line of the range to replace (inclusive)." },
                            endChar: { type: "integer", description: "Optional. The 1-based end character offset of the range (inclusive). If omitted, the replacement extends to the end of endLine." },
                            textToReplace: { type: "string", description: "The new replacement text. This MUST contain the actual modifications or completed code implementation, and must not be identical to expectedOriginalText." },
                            expectedOriginalText: { type: "string", description: "Required. The exact text currently present at the specified range. This is CRITICAL for the system to auto-correct line number discrepancies and prevent stale edits." }
                        },
                        required: ["filePath", "startLine", "endLine", "textToReplace", "expectedOriginalText"]
                    }
                }
            },
            {
                name: 'deleteCode',
                category: 'Uncategorized',
                isDestructive: true,
                isPatchingTool: true,
                modulePath: './tools/code_modification/deleteCode',
                adapter: async (args, impl) => await impl(args),
                getProgressText: args => 'Deleting code in ' + (args.filePath || '') + '...',
                schema: {
                    name: "deleteCode",
                    description: "Deletes a validated range of code. CRITICAL: expectedOriginalText must match the text to be deleted exactly.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: { type: "string", description: "The relative or absolute path of the file." },
                            startLine: { type: "integer", description: "The 1-based start line of the range to delete (inclusive, 1 is the first line). Must be positive." },
                            startChar: { type: "integer", description: "The 1-based start character offset of the range (inclusive, 1 is the first character). Must be positive." },
                            endLine: { type: "integer", description: "The 1-based end line of the range to delete (inclusive). Must be positive." },
                            endChar: { type: "integer", description: "The 1-based end character offset of the range (inclusive). Must be positive." },
                            expectedOriginalText: { type: "string", description: "Required. The exact text currently present at the specified range. Must match exactly, including leading spaces, tabs, newlines, and trailing characters, otherwise the edit will be rejected." }
                        },
                        required: ["filePath", "startLine", "startChar", "endLine", "endChar", "expectedOriginalText"]
                    }
                }
            },
            {
                name: 'renameSymbol',
                category: 'Uncategorized',
                isDestructive: true,
                isPatchingTool: true,
                modulePath: './tools/code_modification/renameSymbol',
                adapter: async (args, impl) => await impl(args),
                getProgressText: args => 'Renaming symbol in ' + (args.filePath || '') + '...',
                schema: {
                    name: "renameSymbol",
                    description: "Uses the language server to safely rename a symbol across the workspace, updating all imports and references.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: { type: "string", description: "The relative or absolute path of the file containing the symbol reference." },
                            line: { type: "integer", description: "The 1-based line number of the symbol declaration/reference. Must be positive." },
                            character: { type: "integer", description: "The 1-based character offset of the symbol. Must be positive." },
                            newName: { type: "string", description: "The new name for the symbol. Must be a valid programming language identifier (alphanumeric and underscores, not starting with a digit)." }
                        },
                        required: ["filePath", "line", "character", "newName"]
                    }
                }
            },
            {
                name: 'moveFile',
                category: 'Uncategorized',
                isDestructive: true,
                isPatchingTool: true,
                modulePath: './tools/code_modification/moveFile',
                adapter: async (args, impl) => await impl(args),
                getProgressText: args => 'Moving file ' + (args.sourcePath || '') + ' to ' + (args.destPath || '') + '...',
                schema: {
                    name: "moveFile",
                    description: "Moves or renames a file and updates references/imports where supported. Destination directory must already exist on disk.",
                    parameters: {
                        type: "object",
                        properties: {
                            sourcePath: { type: "string", description: "The source file path to move. Must exist." },
                            destPath: { type: "string", description: "The destination file path. Ensure the parent directory exists." }
                        },
                        required: ["sourcePath", "destPath"]
                    }
                }
            },
            {
                name: 'moveType',
                category: 'Uncategorized',
                isDestructive: true,
                isPatchingTool: true,
                modulePath: './tools/code_modification/moveType',
                adapter: async (args, impl) => await impl(args),
                getProgressText: args => 'Moving type ' + (args.typeName || '') + ' to ' + (args.destFilePath || '') + '...',
                schema: {
                    name: "moveType",
                    description: "Moves a class/type to another file or namespace where supported. Updates references automatically.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: { type: "string", description: "The source file path where the type is defined." },
                            typeName: { type: "string", description: "The name of the class or type to move. Must exist." },
                            destFilePath: { type: "string", description: "The destination file path. Must be a valid write target path." }
                        },
                        required: ["filePath", "typeName", "destFilePath"]
                    }
                }
            },
            {
                name: 'extractMethod',
                category: 'Uncategorized',
                isDestructive: true,
                isPatchingTool: true,
                modulePath: './tools/code_modification/extractMethod',
                adapter: async (args, impl) => await impl(args),
                getProgressText: args => 'Extracting method in ' + (args.filePath || '') + '...',
                schema: {
                    name: "extractMethod",
                    description: "Extracts selected code range into a new method/function.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: { type: "string", description: "The relative or absolute path of the file." },
                            startLine: { type: "integer", description: "The 1-based start line of the selected code (inclusive). Must be positive." },
                            startChar: { type: "integer", description: "The 1-based start character offset (inclusive). Must be positive." },
                            endLine: { type: "integer", description: "The 1-based end line of the selected code (inclusive). Must be positive." },
                            endChar: { type: "integer", description: "The 1-based end character offset (inclusive). Must be positive." },
                            newMethodName: { type: "string", description: "The name of the new method/function. Must be a valid identifier name." }
                        },
                        required: ["filePath", "startLine", "startChar", "endLine", "endChar", "newMethodName"]
                    }
                }
            },
            {
                name: 'formatFile',
                category: 'Uncategorized',
                isDestructive: true,
                isPatchingTool: true,
                modulePath: './tools/code_modification/formatFile',
                adapter: async (args, impl) => await impl(args),
                getProgressText: args => 'Formatting file ' + (args.filePath || '') + '...',
                schema: {
                    name: "formatFile",
                    description: "Runs the configured formatter (e.g. Prettier, Black, dotnet format) on a file. File must exist.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: { type: "string", description: "The relative or absolute path of the file to format." }
                        },
                        required: ["filePath"]
                    }
                }
            },
            {
                name: 'organizeImports',
                category: 'Uncategorized',
                isDestructive: true,
                isPatchingTool: true,
                modulePath: './tools/code_modification/organizeImports',
                adapter: async (args, impl) => await impl(args),
                getProgressText: args => 'Organizing imports in ' + (args.filePath || '') + '...',
                schema: {
                    name: "organizeImports",
                    description: "Adds, removes, or sorts imports/usings/includes for a file using the language server provider.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: { type: "string", description: "The relative or absolute path of the target file. Must exist." }
                        },
                        required: ["filePath"]
                    }
                }
            },
            {
                name: 'listWorkspaceFiles',
                category: 'Project Understanding',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/project_understanding/listWorkspaceFiles',
                adapter: async (args, impl) => await impl(args.filterGlob),
                getProgressText: args => `Executing tool listWorkspaceFiles...`,
                schema: {
                    name: "listWorkspaceFiles",
                    description: "Lists workspace files recursively, optionally filtered by glob, extension, folder, or ignore rules.",
                    parameters: {
                        type: "object",
                        properties: {
                            filterGlob: { type: "string", description: "Optional glob pattern to filter, e.g. '**/*.cs' or '**/*.py'. Relative to the workspace root." }
                        }
                    }
                }
            },
            {
                name: 'listDirectory',
                category: 'Project Understanding',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/project_understanding/listDirectory',
                adapter: async (args, impl) => await impl(args.dirPath),
                getProgressText: args => `Executing tool listDirectory...`,
                schema: {
                    name: "listDirectory",
                    description: "Lists files and subdirectories directly under a specific folder (not recursive). Folder must exist.",
                    parameters: {
                        type: "object",
                        properties: {
                            dirPath: { type: "string", description: "Optional relative or absolute directory path to list. If omitted, lists the workspace root folder." }
                        }
                    }
                }
            },
            {
                name: 'findSymbol',
                category: 'Project Understanding',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/project_understanding/findSymbol',
                adapter: async (args, impl) => await impl(args.symbolName),
                getProgressText: args => `Executing tool findSymbol...`,
                schema: {
                    name: "findSymbol",
                    description: "Finds structural code symbols (classes, methods, variables, interfaces) by exact or fuzzy name across the workspace.",
                    parameters: {
                        type: "object",
                        properties: {
                            symbolName: { type: "string", description: "The name of the symbol to search for (e.g., ClassName or methodName)." }
                        },
                        required: ["symbolName"]
                    }
                }
            },
            {
                name: 'searchSymbols',
                category: 'Project Understanding',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/project_understanding/searchSymbols',
                adapter: async (args, impl) => await impl(args.query),
                getProgressText: args => `Executing tool searchSymbols...`,
                schema: {
                    name: "searchSymbols",
                    description: "Searches workspace symbols by name, kind, namespace, class, or partial match using language server providers.",
                    parameters: {
                        type: "object",
                        properties: {
                            query: { type: "string", description: "Query string, optionally containing filters like 'kind:class' or 'container:myClass'." }
                        },
                        required: ["query"]
                    }
                }
            },
            {
                name: 'findImplementations',
                category: 'Project Understanding',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/project_understanding/findImplementations',
                adapter: async (args, impl) => await impl(args.filePath, args.line !== undefined ? Math.max(0, parseInt(args.line, 10) - 1) : undefined, args.character !== undefined ? Math.max(0, parseInt(args.character, 10) - 1) : undefined),
                getProgressText: args => `Executing tool findImplementations...`,
                schema: {
                    name: "findImplementations",
                    description: "Finds implementations of an interface, abstract method, virtual method, or base type across the workspace.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: { type: "string", description: "The relative or absolute file path containing the type/member declaration." },
                            line: { type: "integer", description: "The 1-based line number of the symbol declaration. Must be positive." },
                            character: { type: "integer", description: "The 1-based character/column offset. Must be positive." }
                        }
                    }
                }
            },
            {
                name: 'findBaseTypes',
                category: 'Project Understanding',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/project_understanding/findBaseTypes',
                adapter: async (args, impl) => await impl(args.filePath, args.line !== undefined ? Math.max(0, parseInt(args.line, 10) - 1) : undefined, args.character !== undefined ? Math.max(0, parseInt(args.character, 10) - 1) : undefined),
                getProgressText: args => `Executing tool findBaseTypes...`,
                schema: {
                    name: "findBaseTypes",
                    description: "Finds base classes, implemented interfaces, or inherited members for a type definition.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: { type: "string", description: "The relative or absolute file path containing the symbol." },
                            line: { type: "integer", description: "The 1-based line number of the symbol declaration. Must be positive." },
                            character: { type: "integer", description: "The 1-based character/column offset. Must be positive." }
                        }
                    }
                }
            },
            {
                name: 'findDerivedTypes',
                category: 'Project Understanding',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/project_understanding/findDerivedTypes',
                adapter: async (args, impl) => await impl(args.filePath, args.line !== undefined ? Math.max(0, parseInt(args.line, 10) - 1) : undefined, args.character !== undefined ? Math.max(0, parseInt(args.character, 10) - 1) : undefined),
                getProgressText: args => `Executing tool findDerivedTypes...`,
                schema: {
                    name: "findDerivedTypes",
                    description: "Finds subclasses, implementers, or derived types of a class/interface across the workspace.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: { type: "string", description: "The relative or absolute file path containing the symbol." },
                            line: { type: "integer", description: "The 1-based line number of the symbol declaration. Must be positive." },
                            character: { type: "integer", description: "The 1-based character/column offset. Must be positive." }
                        }
                    }
                }
            },
            {
                name: 'findCallers',
                category: 'Project Understanding',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/project_understanding/findCallers',
                adapter: async (args, impl) => await impl(args.filePath, args.line !== undefined ? Math.max(0, parseInt(args.line, 10) - 1) : undefined, args.character !== undefined ? Math.max(0, parseInt(args.character, 10) - 1) : undefined),
                getProgressText: args => `Executing tool findCallers...`,
                schema: {
                    name: "findCallers",
                    description: "Finds methods/functions that directly call the symbol at a given location.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: { type: "string", description: "The relative or absolute file path containing the symbol." },
                            line: { type: "integer", description: "The 1-based line number of the symbol declaration. Must be positive." },
                            character: { type: "integer", description: "The 1-based character/column offset. Must be positive." }
                        }
                    }
                }
            },
            {
                name: 'findCallees',
                category: 'Project Understanding',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/project_understanding/findCallees',
                adapter: async (args, impl) => await impl(args.filePath, args.line !== undefined ? Math.max(0, parseInt(args.line, 10) - 1) : undefined, args.character !== undefined ? Math.max(0, parseInt(args.character, 10) - 1) : undefined),
                getProgressText: args => `Executing tool findCallees...`,
                schema: {
                    name: "findCallees",
                    description: "Finds methods/functions called directly by the symbol at a given location.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: { type: "string", description: "The relative or absolute file path containing the symbol." },
                            line: { type: "integer", description: "The 1-based line number of the symbol declaration. Must be positive." },
                            character: { type: "integer", description: "The 1-based character/column offset. Must be positive." }
                        }
                    }
                }
            },
            {
                name: 'searchDocs',
                category: 'Documentation',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/documentation/searchDocs',
                adapter: async (args, impl) => await impl(args.query),
                getProgressText: args => `Executing tool searchDocs...`,
                schema: {
                    name: "searchDocs",
                    description: "Searches project documentation, markdown files, local docs, or wiki exports.",
                    parameters: {
                        type: "object",
                        properties: {
                            query: { type: "string", description: "The search query term." }
                        },
                        required: ["query"]
                    }
                }
            },
            {
                name: 'readDoc',
                category: 'Documentation',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/documentation/readDoc',
                adapter: async (args, impl) => await impl(args.docPath),
                getProgressText: args => `Executing tool readDoc...`,
                schema: {
                    name: "readDoc",
                    description: "Reads a specific documentation file or page by path or ID.",
                    parameters: {
                        type: "object",
                        properties: {
                            docPath: { type: "string", description: "The path or ID of the doc file to read." }
                        },
                        required: ["docPath"]
                    }
                }
            },
            {
                name: 'lookupApi',
                category: 'Documentation',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/documentation/lookupApi',
                adapter: async (args, impl) => await impl(args.apiName),
                getProgressText: args => `Executing tool lookupApi...`,
                schema: {
                    name: "lookupApi",
                    description: "Looks up API documentation for a class, method, package, framework, or library.",
                    parameters: {
                        type: "object",
                        properties: {
                            apiName: { type: "string", description: "The class, namespace, or function name to search for." }
                        },
                        required: ["apiName"]
                    }
                }
            },
            {
                name: 'lookupPackage',
                category: 'Documentation',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/documentation/lookupPackage',
                adapter: async (args, impl) => await impl(args.packageName),
                getProgressText: args => `Executing tool lookupPackage...`,
                schema: {
                    name: "lookupPackage",
                    description: "Retrieves package metadata, installed version, README, and usage info.",
                    parameters: {
                        type: "object",
                        properties: {
                            packageName: { type: "string", description: "The name of the npm or NuGet package." }
                        },
                        required: ["packageName"]
                    }
                }
            },
            {
                name: 'generateDocComment',
                category: 'Documentation',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/documentation/generateDocComment',
                adapter: async (args, impl) => await impl(args.signature),
                getProgressText: args => `Executing tool generateDocComment...`,
                schema: {
                    name: "generateDocComment",
                    description: "Generates or updates XMLDoc/JSDoc/docstrings for a symbol signature.",
                    parameters: {
                        type: "object",
                        properties: {
                            signature: { type: "string", description: "The function or method signature." }
                        },
                        required: ["signature"]
                    }
                }
            },
            {
                name: 'summarizeFile',
                category: 'Documentation',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/documentation/summarizeFile',
                adapter: async (args, impl) => await impl(args.filePath),
                getProgressText: args => `Executing tool summarizeFile...`,
                schema: {
                    name: "summarizeFile",
                    description: "Produces a concise summary of a source file, including purpose, symbols, and dependencies.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: { type: "string", description: "The path to the source file." }
                        },
                        required: ["filePath"]
                    }
                }
            },
            {
                name: 'getProjectDependencies',
                category: 'Architecture Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/architecture_tools/getProjectDependencies',
                adapter: async (args, impl) => await impl(args.projectPath),
                getProgressText: args => `Executing tool getProjectDependencies...`,
                schema: {
                    name: "getProjectDependencies",
                    description: "Lists project/package/module dependencies and dependency versions.",
                    parameters: {
                        type: "object",
                        properties: {
                            projectPath: { type: "string", description: "Relative or absolute directory path containing package.json." }
                        },
                        required: ["projectPath"]
                    }
                }
            },
            {
                name: 'findModuleDependencies',
                category: 'Architecture Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/architecture_tools/findModuleDependencies',
                adapter: async (args, impl) => await impl(args.filePath),
                getProgressText: args => `Executing tool findModuleDependencies...`,
                schema: {
                    name: "findModuleDependencies",
                    description: "Finds import/require dependencies for a given file.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: { type: "string", description: "The path to the target source file." }
                        },
                        required: ["filePath"]
                    }
                }
            },
            {
                name: 'findCycles',
                category: 'Architecture Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/architecture_tools/findCycles',
                adapter: async (args, impl) => await impl(args.directory),
                getProgressText: args => `Executing tool findCycles...`,
                schema: {
                    name: "findCycles",
                    description: "Detects circular dependencies between modules or files in a directory.",
                    parameters: {
                        type: "object",
                        properties: {
                            directory: { type: "string", description: "The directory to analyze recursively." }
                        },
                        required: ["directory"]
                    }
                }
            },
            {
                name: 'analyzeLayering',
                category: 'Architecture Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/architecture_tools/analyzeLayering',
                adapter: async (args, impl) => await impl(args.directory, args.rulesJsonStr),
                getProgressText: args => `Executing tool analyzeLayering...`,
                schema: {
                    name: "analyzeLayering",
                    description: "Checks whether code follows configured architectural layers or dependency rules.",
                    parameters: {
                        type: "object",
                        properties: {
                            directory: { type: "string", description: "The directory to analyze." },
                            rulesJsonStr: { type: "string", description: "JSON string mapping layer segments to allowed dependencies." }
                        },
                        required: ["directory", "rulesJsonStr"]
                    }
                }
            },
            {
                name: 'findDeadCode',
                category: 'Architecture Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/architecture_tools/findDeadCode',
                adapter: async (args, impl) => await impl(args.directory),
                getProgressText: args => `Executing tool findDeadCode...`,
                schema: {
                    name: "findDeadCode",
                    description: "Finds unused symbols or unreachable code inside JS/TS files.",
                    parameters: {
                        type: "object",
                        properties: {
                            directory: { type: "string", description: "The directory to analyze." }
                        },
                        required: ["directory"]
                    }
                }
            },
            {
                name: 'findDuplicateCode',
                category: 'Architecture Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/architecture_tools/findDuplicateCode',
                adapter: async (args, impl) => await impl(args.directory),
                getProgressText: args => `Executing tool findDuplicateCode...`,
                schema: {
                    name: "findDuplicateCode",
                    description: "Finds copy-pasted or highly similar code chunks.",
                    parameters: {
                        type: "object",
                        properties: {
                            directory: { type: "string", description: "The directory to scan recursively." }
                        },
                        required: ["directory"]
                    }
                }
            },
            {
                name: 'searchKnowledge',
                category: 'RAG / Knowledge Base',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/rag_knowledge_base/searchKnowledge',
                adapter: async (args, impl) => await impl(args.query),
                getProgressText: args => `Executing tool searchKnowledge...`,
                schema: {
                    name: "searchKnowledge",
                    description: "Searches configured knowledge sources (Confluence, Notion, FAQs).",
                    parameters: {
                        type: "object",
                        properties: {
                            query: { type: "string", description: "Query string to match in knowledge items." }
                        },
                        required: ["query"]
                    }
                }
            },
            {
                name: 'readKnowledgeItem',
                category: 'RAG / Knowledge Base',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/rag_knowledge_base/readKnowledgeItem',
                adapter: async (args, impl) => await impl(args.itemId),
                getProgressText: args => `Executing tool readKnowledgeItem...`,
                schema: {
                    name: "readKnowledgeItem",
                    description: "Reads a specific knowledge-base document/page by ID.",
                    parameters: {
                        type: "object",
                        properties: {
                            itemId: { type: "string", description: "The ID of the knowledge item (e.g. KB-001)." }
                        },
                        required: ["itemId"]
                    }
                }
            },
            {
                name: 'searchTickets',
                category: 'RAG / Knowledge Base',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/rag_knowledge_base/searchTickets',
                adapter: async (args, impl) => await impl(args.query),
                getProgressText: args => `Executing tool searchTickets...`,
                schema: {
                    name: "searchTickets",
                    description: "Searches Jira, DevOps, or Linear tickets and issues.",
                    parameters: {
                        type: "object",
                        properties: {
                            query: { type: "string", description: "The search query to match in tickets." }
                        },
                        required: ["query"]
                    }
                }
            },
            {
                name: 'readTicket',
                category: 'RAG / Knowledge Base',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/rag_knowledge_base/readTicket',
                adapter: async (args, impl) => await impl(args.ticketId),
                getProgressText: args => `Executing tool readTicket...`,
                schema: {
                    name: "readTicket",
                    description: "Reads details, assignee, status, comments, and links of a specific ticket.",
                    parameters: {
                        type: "object",
                        properties: {
                            ticketId: { type: "string", description: "The ticket ID (e.g. TASK-101)." }
                        },
                        required: ["ticketId"]
                    }
                }
            },
            {
                name: 'searchPullRequests',
                category: 'RAG / Knowledge Base',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/rag_knowledge_base/searchPullRequests',
                adapter: async (args, impl) => await impl(args.query),
                getProgressText: args => `Executing tool searchPullRequests...`,
                schema: {
                    name: "searchPullRequests",
                    description: "Searches pull requests and merge requests.",
                    parameters: {
                        type: "object",
                        properties: {
                            query: { type: "string", description: "The search query string." }
                        },
                        required: ["query"]
                    }
                }
            },
            {
                name: 'readPullRequest',
                category: 'RAG / Knowledge Base',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/rag_knowledge_base/readPullRequest',
                adapter: async (args, impl) => await impl(args.pullRequestId),
                getProgressText: args => `Executing tool readPullRequest...`,
                schema: {
                    name: "readPullRequest",
                    description: "Reads comments, changed files, reviews, and status of a specific pull request.",
                    parameters: {
                        type: "object",
                        properties: {
                            pullRequestId: { type: "string", description: "The pull request ID (e.g. PR-201)." }
                        },
                        required: ["pullRequestId"]
                    }
                }
            },
            {
                name: 'searchDesignDocs',
                category: 'RAG / Knowledge Base',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/rag_knowledge_base/searchDesignDocs',
                adapter: async (args, impl) => await impl(args.query),
                getProgressText: args => `Executing tool searchDesignDocs...`,
                schema: {
                    name: "searchDesignDocs",
                    description: "Searches architecture, system design, and context documents.",
                    parameters: {
                        type: "object",
                        properties: {
                            query: { type: "string", description: "The search query." }
                        },
                        required: ["query"]
                    }
                }
            },
            {
                name: 'searchDecisions',
                category: 'RAG / Knowledge Base',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/rag_knowledge_base/searchDecisions',
                adapter: async (args, impl) => await impl(args.query),
                getProgressText: args => `Executing tool searchDecisions...`,
                schema: {
                    name: "searchDecisions",
                    description: "Searches Architecture Decision Records (ADRs) and engineering decisions.",
                    parameters: {
                        type: "object",
                        properties: {
                            query: { type: "string", description: "The search query." }
                        },
                        required: ["query"]
                    }
                }
            },
            {
                name: 'runCommand',
                category: 'Agent Tools',
                isDestructive: true,
                isPatchingTool: false,
                isAdminTool: true,
                modulePath: './tools/agent_tools/runCommand',
                adapter: async (args, impl) => await impl(args.command),
                getProgressText: args => `Executing tool runCommand...`,
                schema: {
                    name: "runCommand",
                    description: "Runs a command on the user's local terminal system. CRITICAL: Must be run non-interactively! The command must not expect stdin, wait for any user prompts (like y/n queries), or spawn blocked processes. Do not use 'cd' chaining as shell state does not persist.",
                    parameters: {
                        type: "object",
                        properties: {
                            command: { type: "string", description: "The shell command to execute non-interactively." }
                        },
                        required: ["command"]
                    }
                }
            },
            {
                name: 'createPlan',
                category: 'Agent Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/agent_tools/createPlan',
                adapter: async (args, impl) => await impl(args.stepsInput),
                getProgressText: args => `Executing tool createPlan...`,
                schema: {
                    name: "createPlan",
                    description: "Creates a structured multi-step plan for a larger task.",
                    parameters: {
                        type: "object",
                        properties: {
                            stepsInput: {
                                type: "array",
                                items: { type: "string" },
                                description: "Array of steps, or a multi-line string containing the steps."
                            }
                        },
                        required: ["stepsInput"]
                    }
                }
            },
            {
                name: 'updatePlan',
                category: 'Agent Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/agent_tools/updatePlan',
                adapter: async (args, impl) => await impl(args.stepsInput),
                getProgressText: args => `Executing tool updatePlan...`,
                schema: {
                    name: "updatePlan",
                    description: "Appends new steps to the active task plan.",
                    parameters: {
                        type: "object",
                        properties: {
                            stepsInput: {
                                type: "array",
                                items: { type: "string" },
                                description: "Array of steps, or a multi-line string to append."
                            }
                        },
                        required: ["stepsInput"]
                    }
                }
            },
            {
                name: 'markPlanStepComplete',
                category: 'Agent Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/agent_tools/markPlanStepComplete',
                adapter: async (args, impl) => await impl(args.stepIndex),
                getProgressText: args => `Executing tool markPlanStepComplete...`,
                schema: {
                    name: "markPlanStepComplete",
                    description: "Marks a specific step in the plan as completed.",
                    parameters: {
                        type: "object",
                        properties: {
                            stepIndex: { type: "integer", description: "The 1-based index of the step to complete. Must be a positive integer." }
                        },
                        required: ["stepIndex"]
                    }
                }
            },
            {
                name: 'createTask',
                category: 'Agent Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/agent_tools/createTask',
                adapter: async (args, impl) => await impl(args.description),
                getProgressText: args => `Executing tool createTask...`,
                schema: {
                    name: "createTask",
                    description: "Creates a subtask for tracking agent work.",
                    parameters: {
                        type: "object",
                        properties: {
                            description: { type: "string", description: "Description details of the subtask." }
                        },
                        required: ["description"]
                    }
                }
            },
            {
                name: 'completeTask',
                category: 'Agent Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/agent_tools/completeTask',
                adapter: async (args, impl) => await impl(args.taskId),
                getProgressText: args => `Executing tool completeTask...`,
                schema: {
                    name: "completeTask",
                    description: "Marks a tracking subtask complete.",
                    parameters: {
                        type: "object",
                        properties: {
                            taskId: { type: "integer", description: "The 1-based ID of the task to complete. Must be a positive integer." }
                        },
                        required: ["taskId"]
                    }
                }
            },
            {
                name: 'requestUserConfirmation',
                category: 'Agent Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/agent_tools/requestUserConfirmation',
                adapter: async (args, impl) => await impl(args.message),
                getProgressText: args => `Executing tool requestUserConfirmation...`,
                schema: {
                    name: "requestUserConfirmation",
                    description: "Pauses execution and asks the user to approve a sensitive operation.",
                    parameters: {
                        type: "object",
                        properties: {
                            message: { type: "string", description: "Message prompt explaining what requires approval." }
                        },
                        required: ["message"]
                    }
                }
            },
            {
                name: 'summarizeProgress',
                category: 'Agent Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/agent_tools/summarizeProgress',
                adapter: async (args, impl) => await impl(),
                getProgressText: args => `Executing tool summarizeProgress...`,
                schema: {
                    name: "summarizeProgress",
                    description: "Summarizes what has been inspected, changed, learned, and what remains.",
                    parameters: {
                        type: "object",
                        properties: {}
                    }
                }
            },
            {
                name: 'saveSessionMemory',
                category: 'Agent Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/agent_tools/saveSessionMemory',
                adapter: async (args, impl) => await impl(args.memoryString),
                getProgressText: args => `Executing tool saveSessionMemory...`,
                schema: {
                    name: "saveSessionMemory",
                    description: "Saves a compact summary of the current task session to local memory.",
                    parameters: {
                        type: "object",
                        properties: {
                            memoryString: { type: "string", description: "The text summary content." }
                        },
                        required: ["memoryString"]
                    }
                }
            },
            {
                name: 'restoreSessionMemory',
                category: 'Agent Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/agent_tools/restoreSessionMemory',
                adapter: async (args, impl) => await impl(),
                getProgressText: args => `Executing tool restoreSessionMemory...`,
                schema: {
                    name: "restoreSessionMemory",
                    description: "Restores previous session task summary memory if present.",
                    parameters: {
                        type: "object",
                        properties: {}
                    }
                }
            },
            {
                name: 'buildProject',
                category: 'Build System',
                isDestructive: true,
                isPatchingTool: false,
                modulePath: './tools/build_system/buildProject',
                adapter: async (args, impl) => await impl(args.projectPath),
                getProgressText: args => `Building project at "${args.projectPath || ''}"...`,
                schema: {
                    name: "buildProject",
                    description: "Compiles or builds the specific project or file path. It dynamically detects if the project is .NET (C#), NPM (Javascript/Typescript), Java (Maven/Gradle), C/C++ (CMake/Makefile/GCC), or Python (py_compile, pip/poetry/setup.py), and invokes the appropriate compiler or build manager.",
                    parameters: {
                        type: "object",
                        properties: {
                            projectPath: { 
                                type: "string", 
                                description: "The relative or absolute file or directory path of the project to build. If not specified, defaults to the workspace root directory." 
                            }
                        }
                    }
                }
            },
            {
                name: 'buildSolution',
                category: 'Build System',
                isDestructive: true,
                isPatchingTool: false,
                modulePath: './tools/build_system/buildSolution',
                adapter: async (args, impl) => await impl(args.solutionPath),
                getProgressText: args => `Building solution at "${args.solutionPath || ''}"...`,
                schema: {
                    name: "buildSolution",
                    description: "Builds the entire solution or default compile target for the project workspace. Automatically detects the project type (.NET, NPM, Java, C/C++, or Python) and triggers the correct build tool (e.g. dotnet build, npm run build, mvn package, cmake/make, or python compile).",
                    parameters: {
                        type: "object",
                        properties: {
                            solutionPath: { 
                                type: "string", 
                                description: "The relative or absolute file or directory path of the solution/workspace. Defaults to the workspace root directory if not provided." 
                            }
                        }
                    }
                }
            },
            {
                name: 'getCodeCoverage',
                category: 'Build System',
                isDestructive: true,
                isPatchingTool: false,
                modulePath: './tools/build_system/getCodeCoverage',
                adapter: async (args, impl) => await impl(args.projectPath),
                getProgressText: args => `Running coverage collection on "${args.projectPath || ''}"...`,
                schema: {
                    name: "getCodeCoverage",
                    description: "Gathers and generates test code coverage reports for the project at the specified path. Automatically runs the appropriate code coverage tool depending on project type (e.g., dotnet test --collect, npm test coverage, mvn jacoco:report, GCC gcov, or pytest-cov).",
                    parameters: {
                        type: "object",
                        properties: {
                            projectPath: { 
                                type: "string", 
                                description: "The relative or absolute path to the project directory or file. Defaults to the workspace root if not provided." 
                            }
                        }
                    }
                }
            },
            {
                name: 'listTests',
                category: 'Build System',
                isDestructive: true,
                isPatchingTool: false,
                modulePath: './tools/build_system/listTests',
                adapter: async (args, impl) => await impl(args.projectPath),
                getProgressText: args => `Listing unit tests at "${args.projectPath || ''}"...`,
                schema: {
                    name: "listTests",
                    description: "Lists and discovers all unit tests in the specified project path without executing them. Uses dotnet test --list-tests, parses NPM Mocha/Jest/Vitest test suites, scans Java JUnit annotations, parses C/C++ GTest/Catch2 cases, or scans Python pytest/unittest files.",
                    parameters: {
                        type: "object",
                        properties: {
                            projectPath: { 
                                type: "string", 
                                description: "The relative or absolute path of the project folder. Defaults to the workspace root if omitted." 
                            }
                        }
                    }
                }
            },
            {
                name: 'runTest',
                category: 'Build System',
                isDestructive: true,
                isPatchingTool: false,
                modulePath: './tools/build_system/runTest',
                adapter: async (args, impl) => await impl(args.projectPath, args.testName),
                getProgressText: args => `Running test "${args.testName || ''}"...`,
                schema: {
                    name: "runTest",
                    description: "Executes a single, specific unit test by name. Automatically identifies project type (.NET, NPM, Java, C/C++, or Python) and passes test filters to the correct test runner (e.g., dotnet filter, npm mocha/jest -g, mvn -Dtest, C/C++ gtest, or pytest/unittest -k).",
                    parameters: {
                        type: "object",
                        properties: {
                            projectPath: { 
                                type: "string", 
                                description: "Optional relative or absolute path to the project directory/file. Defaults to workspace root if not provided." 
                            },
                            testName: { 
                                type: "string", 
                                description: "The name or selector of the specific test to execute." 
                            }
                        },
                        required: ["testName"]
                    }
                }
            },
            {
                name: 'runTests',
                category: 'Build System',
                isDestructive: true,
                isPatchingTool: false,
                modulePath: './tools/build_system/runTests',
                adapter: async (args, impl) => await impl(args.projectPath),
                getProgressText: args => `Running all unit tests at "${args.projectPath || ''}"...`,
                schema: {
                    name: "runTests",
                    description: "Runs all unit tests in the specified project or workspace. Triggers dotnet test, npm test, mvn test, ctest, make test, or pytest depending on the automatically detected project type.",
                    parameters: {
                        type: "object",
                        properties: {
                            projectPath: { 
                                type: "string", 
                                description: "Optional relative or absolute directory path to the project. Defaults to workspace root if not provided." 
                            }
                        }
                    }
                }
            },
            {
                name: 'compileFile',
                category: 'Build System',
                isDestructive: true,
                isPatchingTool: false,
                modulePath: './tools/build_system/compileFile',
                adapter: async (args, impl) => await impl(args.filePath),
                getProgressText: args => `Compiling file "${args.filePath || ''}"...`,
                schema: {
                    name: "compileFile",
                    description: "Compiles, syntax-checks, or dry-runs compilation for a single source file. Supports C# (dotnet build project context or csc), Java (javac), Javascript/Typescript (node --check or tsc --noEmit), C/C++ (gcc/g++ syntax check), and Python (py_compile). Use this to verify a single file's compile-time correctness.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: { 
                                type: "string", 
                                description: "The relative or absolute path of the file to compile/syntax-check." 
                            }
                        },
                        required: ["filePath"]
                    }
                }
            },
            {
                name: 'runFile',
                category: 'Build System',
                isDestructive: true,
                isPatchingTool: false,
                modulePath: './tools/build_system/runFile',
                adapter: async (args, impl) => await impl(args.filePath, args.arguments),
                getProgressText: args => `Running file "${args.filePath || ''}"...`,
                schema: {
                    name: "runFile",
                    description: "Executes a single source file, script, or compiled executable with optional command line arguments. Automatically handles C# (compilation + execution or dotnet run), Java (compilation + execution or direct java run), Javascript/Typescript (node or ts-node), C/C++ (compiles to a temp file and runs), and Python (python script). Use this to validate run-time logic or execute test examples inside a file.",
                    parameters: {
                        type: "object",
                        properties: {
                            filePath: { 
                                type: "string", 
                                description: "The relative or absolute path of the file/script to run." 
                            },
                            arguments: {
                                type: "string",
                                description: "Optional command line arguments to pass to the script or program during execution."
                            }
                        },
                        required: ["filePath"]
                    }
                }
            }
        ];
    }

    getTools() {
        return this.tools;
    }

    getToolDefinition(name) {
        return this.tools.find(t => t.name === name);
    }
}

module.exports = new ToolDefinitionProvider();
