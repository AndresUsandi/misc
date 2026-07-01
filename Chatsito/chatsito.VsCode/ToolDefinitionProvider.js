class ToolDefinitionProvider {
    constructor() {
        this.tools = [
            {
                name: 'search_web',
                category: 'Misc',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/misc/webSearch',
                adapter: async (args, impl) => await impl(args.query),
                getProgressText: args => 'Searching the web for "' + (args.query || '') + '"...',
                schema: {
                    name: "search_web",
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
                name: 'get_current_date_time',
                category: 'Misc',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/misc/getCurrentDateTime',
                adapter: async (args, impl) => await impl(args),
                getProgressText: args => 'Getting current date and time...',
                schema: {
                    name: "get_current_date_time",
                    description: "Gets the current date and time. Use this to determine the current date, time, and day of the week if you are unsure.",
                    parameters: {
                        type: "object",
                        properties: {},
                        required: []
                    }
                }
            },
            {
                name: 'execute_http_request',
                category: 'Misc',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/misc/executeHttpRequest',
                adapter: async (args, impl) => await impl(args.url, args.method, args.body),
                getProgressText: args => 'Executing HTTP request to "' + (args.url || '') + '"...',
                schema: {
                    name: "execute_http_request",
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
                name: 'search_workspace',
                category: 'Coding Assistant',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/core_coding_assistant/searchWorkspace',
                adapter: async (args, impl) => await impl(args.query, args.file_glob),
                getProgressText: args => 'Searching workspace for "' + (args.query || '') + '"...',
                schema: {
                    name: "search_workspace",
                    description: "Searches the current workspace files recursively for a specific text, code query, or symbol name. Returns matching lines and file paths.",
                    parameters: {
                        type: "object",
                        properties: {
                            query: {
                                type: "string",
                                description: "The text, keyword, or code symbol to search for."
                            },
                            file_glob: {
                                type: "string",
                                description: "Optional glob pattern to filter target files, e.g. '**/*.cs' or '**/*.js'."
                            }
                        },
                        required: ["query"]
                    }
                }
            },
            {
                name: 'get_full_graph',
                category: 'Coding Assistant',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/core_coding_assistant/getFullGraph',
                adapter: async (args, impl) => await impl(args.file_path, parseInt(args.line_number, 10), parseInt(args.character_number || '1', 10)),
                getProgressText: args => 'Generating full dependency call graph...',
                schema: {
                    name: "get_full_graph",
                    description: "Generates a full backward invocation dependency tree (call graph) for a symbol at a specific location, listing all callers recursively up to the root caller methods. Detects and stops on circular dependencies.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: {
                                type: "string",
                                description: "The relative or absolute file path containing the symbol."
                            },
                            line_number: {
                                type: "integer",
                                description: "The 1-based line number of the symbol declaration or reference."
                            },
                            character_number: {
                                type: "integer",
                                description: "Optional. The 1-based character/column offset of the symbol on that line. Defaults to 1."
                            }
                        },
                        required: ["file_path", "line_number"]
                    }
                }
            },
            {
                name: 'get_current_editor_context',
                category: 'Coding Assistant',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/core_coding_assistant/getCurrentEditorContext',
                adapter: async (args, impl) => await impl(),
                getProgressText: args => 'Getting current editor context...',
                schema: {
                    name: "get_current_editor_context",
                    description: "Gets the context (file path, cursor line, selected text, and surrounding code lines) of the active document in the editor.",
                    parameters: {
                        type: "object",
                        properties: {}
                    }
                }
            },
            {
                name: 'read_file',
                category: 'Coding Assistant',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/core_coding_assistant/readFile',
                adapter: async (args, impl) => await impl(args.file_path),
                getProgressText: args => 'Reading file ' + (args.file_path || '') + '...',
                schema: {
                    name: "read_file",
                    description: "Reads the entire content of a file in the workspace.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: {
                                type: "string",
                                description: "The relative or absolute path of the file to read."
                            }
                        },
                        required: ["file_path"]
                    }
                }
            },
            {
                name: 'get_context_at_location',
                category: 'Coding Assistant',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/core_coding_assistant/getContextAtLocation',
                adapter: async (args, impl) => await impl.getContextAtLocation(args.file_path, Math.max(0, parseInt(args.line, 10) - 1), Math.max(0, parseInt(args.character, 10) - 1), parseInt(args.call_stack_level || '2', 10)),
                getProgressText: args => 'Getting context at location ' + (args.file_path || '') + ':' + (args.line || 0) + '...',
                schema: {
                    name: "get_context_at_location",
                    description: "Gets the code context (e.g. method/class body) enclosing the specified 1-based line and character location, and traces its callers recursively.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: {
                                type: "string",
                                description: "The relative or absolute path of the file."
                            },
                            line: {
                                type: "integer",
                                description: "The 1-based line number."
                            },
                            character: {
                                type: "integer",
                                description: "The 1-based character/column position on the line."
                            },
                            call_stack_level: {
                                type: "integer",
                                description: "Optional. Number of call stack levels to trace. Defaults to 2."
                            }
                        },
                        required: ["file_path", "line", "character"]
                    }
                }
            },
            {
                name: 'find_definition',
                category: 'Coding Assistant',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/core_coding_assistant/findDefinition',
                adapter: async (args, impl) => await impl(args.file_path, Math.max(0, parseInt(args.line, 10) - 1), Math.max(0, parseInt(args.character, 10) - 1)),
                getProgressText: args => 'Finding definition...',
                schema: {
                    name: "find_definition",
                    description: "Finds the definition location (file, range) of the symbol at the given 1-based line and character location.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: {
                                type: "string",
                                description: "The relative or absolute path of the file containing the symbol reference."
                            },
                            line: {
                                type: "integer",
                                description: "The 1-based line number."
                            },
                            character: {
                                type: "integer",
                                description: "The 1-based character/column position of the symbol reference."
                            }
                        },
                        required: ["file_path", "line", "character"]
                    }
                }
            },
            {
                name: 'find_references',
                category: 'Coding Assistant',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/core_coding_assistant/findReferences',
                adapter: async (args, impl) => await impl(args.file_path, Math.max(0, parseInt(args.line, 10) - 1), Math.max(0, parseInt(args.character, 10) - 1)),
                getProgressText: args => 'Finding references...',
                schema: {
                    name: "find_references",
                    description: "Finds all references (locations and line texts) of the symbol at the given 1-based line and character location.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: {
                                type: "string",
                                description: "The relative or absolute path of the file containing the symbol reference."
                            },
                            line: {
                                type: "integer",
                                description: "The 1-based line number."
                            },
                            character: {
                                type: "integer",
                                description: "The 1-based character/column position of the symbol reference."
                            }
                        },
                        required: ["file_path", "line", "character"]
                    }
                }
            },
            {
                name: 'get_symbols_in_file',
                category: 'Coding Assistant',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/core_coding_assistant/getSymbolsInFile',
                adapter: async (args, impl) => await impl(args.file_path),
                getProgressText: args => 'Getting symbols in ' + (args.file_path || '') + '...',
                schema: {
                    name: "get_symbols_in_file",
                    description: "Gets structural symbols (classes, methods, variables, etc.) defined in a file.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: {
                                type: "string",
                                description: "The relative or absolute path of the file."
                            }
                        },
                        required: ["file_path"]
                    }
                }
            },
            {
                name: 'get_diagnostics',
                category: 'Coding Assistant',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/core_coding_assistant/getDiagnostics',
                adapter: async (args, impl) => await impl(args.file_path),
                getProgressText: args => 'Getting diagnostics...',
                schema: {
                    name: "get_diagnostics",
                    description: "Gets the active compiler/linter diagnostics (errors, warnings, etc.) in the workspace or for a specific file.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: {
                                type: "string",
                                description: "Optional relative or absolute path of the file to filter diagnostics."
                            }
                        }
                    }
                }
            },
            {
                name: 'insert_code',
                category: 'Uncategorized',
                isDestructive: true,
                isPatchingTool: true,
                modulePath: './tools/code_modification/insertCode',
                adapter: async (args, impl) => await impl(args.file_path, Math.max(0, parseInt(args.line, 10) - 1), Math.max(0, parseInt(args.character, 10) - 1), args.text_to_insert),
                getProgressText: args => 'Inserting code in ' + (args.file_path || '') + '...',
                schema: {
                    name: "insert_code",
                    description: "Inserts code at a validated location in a file.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: { type: "string", description: "The relative or absolute path of the file." },
                            line: { type: "integer", description: "The 1-based line number where the insertion starts." },
                            character: { type: "integer", description: "The 1-based character offset on the line." },
                            text_to_insert: { type: "string", description: "The code text to insert." }
                        },
                        required: ["file_path", "line", "character", "text_to_insert"]
                    }
                }
            },
            {
                name: 'replace_code',
                category: 'Uncategorized',
                isDestructive: true,
                isPatchingTool: true,
                modulePath: './tools/code_modification/replaceCode',
                adapter: async (args, impl) => await impl(args.file_path, Math.max(0, parseInt(args.start_line, 10) - 1), Math.max(0, parseInt(args.start_char, 10) - 1), Math.max(0, parseInt(args.end_line, 10) - 1), Math.max(0, parseInt(args.end_char, 10) - 1), args.text_to_replace, args.expected_original_text),
                getProgressText: args => 'Replacing code in ' + (args.file_path || '') + '...',
                schema: {
                    name: "replace_code",
                    description: "Replaces a validated range of code after checking that the original text still matches.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: { type: "string", description: "The relative or absolute path of the file." },
                            start_line: { type: "integer", description: "The 1-based start line of the range to replace." },
                            start_char: { type: "integer", description: "The 1-based start character offset of the range." },
                            end_line: { type: "integer", description: "The 1-based end line of the range to replace." },
                            end_char: { type: "integer", description: "The 1-based end character offset of the range." },
                            text_to_replace: { type: "string", description: "The new replacement text." },
                            expected_original_text: { type: "string", description: "Required. The exact text currently present at the specified range. This is CRITICAL for the system to auto-correct line number discrepancies and prevent stale edits." }
                        },
                        required: ["file_path", "start_line", "start_char", "end_line", "end_char", "text_to_replace", "expected_original_text"]
                    }
                }
            },
            {
                name: 'delete_code',
                category: 'Uncategorized',
                isDestructive: true,
                isPatchingTool: true,
                modulePath: './tools/code_modification/deleteCode',
                adapter: async (args, impl) => await impl(args.file_path, Math.max(0, parseInt(args.start_line, 10) - 1), Math.max(0, parseInt(args.start_char, 10) - 1), Math.max(0, parseInt(args.end_line, 10) - 1), Math.max(0, parseInt(args.end_char, 10) - 1), args.expected_original_text),
                getProgressText: args => 'Deleting code in ' + (args.file_path || '') + '...',
                schema: {
                    name: "delete_code",
                    description: "Deletes a validated range of code.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: { type: "string", description: "The relative or absolute path of the file." },
                            start_line: { type: "integer", description: "The 1-based start line of the range to delete." },
                            start_char: { type: "integer", description: "The 1-based start character offset of the range." },
                            end_line: { type: "integer", description: "The 1-based end line of the range to delete." },
                            end_char: { type: "integer", description: "The 1-based end character offset of the range." },
                            expected_original_text: { type: "string", description: "Required. The exact text currently present at the specified range. This is CRITICAL for the system to auto-correct line number discrepancies and prevent stale edits." }
                        },
                        required: ["file_path", "start_line", "start_char", "end_line", "end_char", "expected_original_text"]
                    }
                }
            },
            {
                name: 'rename_symbol',
                category: 'Uncategorized',
                isDestructive: true,
                isPatchingTool: true,
                modulePath: './tools/code_modification/renameSymbol',
                adapter: async (args, impl) => await impl(args.file_path, Math.max(0, parseInt(args.line, 10) - 1), Math.max(0, parseInt(args.character, 10) - 1), args.new_name),
                getProgressText: args => 'Renaming symbol in ' + (args.file_path || '') + '...',
                schema: {
                    name: "rename_symbol",
                    description: "Uses the language server to safely rename a symbol across the workspace.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: { type: "string", description: "The relative or absolute path of the file." },
                            line: { type: "integer", description: "The 1-based line number of the symbol declaration/reference." },
                            character: { type: "integer", description: "The 1-based character offset of the symbol." },
                            new_name: { type: "string", description: "The new name for the symbol." }
                        },
                        required: ["file_path", "line", "character", "new_name"]
                    }
                }
            },
            {
                name: 'move_file',
                category: 'Uncategorized',
                isDestructive: true,
                isPatchingTool: true,
                modulePath: './tools/code_modification/moveFile',
                adapter: async (args, impl) => await impl(args.source_path, args.dest_path),
                getProgressText: args => 'Moving file ' + (args.source_path || '') + ' to ' + (args.dest_path || '') + '...',
                schema: {
                    name: "move_file",
                    description: "Moves or renames a file and updates references/imports where supported.",
                    parameters: {
                        type: "object",
                        properties: {
                            source_path: { type: "string", description: "The source file path." },
                            dest_path: { type: "string", description: "The destination file path." }
                        },
                        required: ["source_path", "dest_path"]
                    }
                }
            },
            {
                name: 'move_type',
                category: 'Uncategorized',
                isDestructive: true,
                isPatchingTool: true,
                modulePath: './tools/code_modification/moveType',
                adapter: async (args, impl) => await impl(args.file_path, args.type_name, args.dest_file_path),
                getProgressText: args => 'Moving type ' + (args.type_name || '') + ' to ' + (args.dest_file_path || '') + '...',
                schema: {
                    name: "move_type",
                    description: "Moves a class/type to another file or namespace where supported.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: { type: "string", description: "The source file path where the type is defined." },
                            type_name: { type: "string", description: "The name of the class or type to move." },
                            dest_file_path: { type: "string", description: "The destination file path." }
                        },
                        required: ["file_path", "type_name", "dest_file_path"]
                    }
                }
            },
            {
                name: 'extract_method',
                category: 'Uncategorized',
                isDestructive: true,
                isPatchingTool: true,
                modulePath: './tools/code_modification/extractMethod',
                adapter: async (args, impl) => await impl(args.file_path, Math.max(0, parseInt(args.start_line, 10) - 1), Math.max(0, parseInt(args.start_char, 10) - 1), Math.max(0, parseInt(args.end_line, 10) - 1), Math.max(0, parseInt(args.end_char, 10) - 1), args.new_method_name),
                getProgressText: args => 'Extracting method in ' + (args.file_path || '') + '...',
                schema: {
                    name: "extract_method",
                    description: "Extracts selected code into a new method/function.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: { type: "string", description: "The relative or absolute path of the file." },
                            start_line: { type: "integer", description: "The 1-based start line of the selected code." },
                            start_char: { type: "integer", description: "The 1-based start character offset." },
                            end_line: { type: "integer", description: "The 1-based end line of the selected code." },
                            end_char: { type: "integer", description: "The 1-based end character offset." },
                            new_method_name: { type: "string", description: "The name of the new method/function." }
                        },
                        required: ["file_path", "start_line", "start_char", "end_line", "end_char", "new_method_name"]
                    }
                }
            },
            {
                name: 'format_file',
                category: 'Uncategorized',
                isDestructive: true,
                isPatchingTool: true,
                modulePath: './tools/code_modification/formatFile',
                adapter: async (args, impl) => await impl(args.file_path),
                getProgressText: args => 'Formatting file ' + (args.file_path || '') + '...',
                schema: {
                    name: "format_file",
                    description: "Runs the configured formatter on a file.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: { type: "string", description: "The relative or absolute path of the file to format." }
                        },
                        required: ["file_path"]
                    }
                }
            },
            {
                name: 'organize_imports',
                category: 'Uncategorized',
                isDestructive: true,
                isPatchingTool: true,
                modulePath: './tools/code_modification/organizeImports',
                adapter: async (args, impl) => await impl(args.file_path),
                getProgressText: args => 'Organizing imports in ' + (args.file_path || '') + '...',
                schema: {
                    name: "organize_imports",
                    description: "Adds, removes, or sorts imports/usings/includes for a file.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: { type: "string", description: "The relative or absolute path of the file." }
                        },
                        required: ["file_path"]
                    }
                }
            },
            {
                name: 'list_workspace_files',
                category: 'Project Understanding',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/project_understanding/listWorkspaceFiles',
                adapter: async (args, impl) => await impl(args.filterGlob),
                getProgressText: args => `Executing tool list_workspace_files...`,
                schema: {
                    name: "list_workspace_files",
                    description: "Lists workspace files, optionally filtered by glob, extension, folder, or ignore rules.",
                    parameters: {
                        type: "object",
                        properties: {
                            filterGlob: { type: "string", description: "Optional glob pattern to filter, e.g. '**/*.cs'." }
                        }
                    }
                }
            },
            {
                name: 'list_directory',
                category: 'Project Understanding',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/project_understanding/listDirectory',
                adapter: async (args, impl) => await impl(args.dirPath),
                getProgressText: args => `Executing tool list_directory...`,
                schema: {
                    name: "list_directory",
                    description: "Lists files and subdirectories under a specific workspace folder.",
                    parameters: {
                        type: "object",
                        properties: {
                            dirPath: { type: "string", description: "Optional relative or absolute directory path." }
                        }
                    }
                }
            },
            {
                name: 'find_symbol',
                category: 'Project Understanding',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/project_understanding/findSymbol',
                adapter: async (args, impl) => await impl(args.symbolName),
                getProgressText: args => `Executing tool find_symbol...`,
                schema: {
                    name: "find_symbol",
                    description: "Finds a symbol by exact or fuzzy name across the workspace.",
                    parameters: {
                        type: "object",
                        properties: {
                            symbolName: { type: "string", description: "The name of the symbol to search for." }
                        },
                        required: ["symbolName"]
                    }
                }
            },
            {
                name: 'search_symbols',
                category: 'Project Understanding',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/project_understanding/searchSymbols',
                adapter: async (args, impl) => await impl(args.query),
                getProgressText: args => `Executing tool search_symbols...`,
                schema: {
                    name: "search_symbols",
                    description: "Searches workspace symbols by name, kind, namespace, class, or partial match.",
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
                name: 'find_implementations',
                category: 'Project Understanding',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/project_understanding/findImplementations',
                adapter: async (args, impl) => await impl(args.file_path, args.line !== undefined ? Math.max(0, parseInt(args.line, 10) - 1) : undefined, args.character !== undefined ? Math.max(0, parseInt(args.character, 10) - 1) : undefined),
                getProgressText: args => `Executing tool find_implementations...`,
                schema: {
                    name: "find_implementations",
                    description: "Finds implementations of an interface, abstract method, virtual method, or base type.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: { type: "string", description: "The relative or absolute file path containing the type/member." },
                            line: { type: "integer", description: "The 1-based line number of the symbol declaration." },
                            character: { type: "integer", description: "The 1-based character/column offset." }
                        }
                    }
                }
            },
            {
                name: 'find_base_types',
                category: 'Project Understanding',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/project_understanding/findBaseTypes',
                adapter: async (args, impl) => await impl(args.file_path, args.line !== undefined ? Math.max(0, parseInt(args.line, 10) - 1) : undefined, args.character !== undefined ? Math.max(0, parseInt(args.character, 10) - 1) : undefined),
                getProgressText: args => `Executing tool find_base_types...`,
                schema: {
                    name: "find_base_types",
                    description: "Finds base classes, implemented interfaces, or inherited members for a type.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: { type: "string", description: "The relative or absolute file path containing the symbol." },
                            line: { type: "integer", description: "The 1-based line number of the symbol declaration." },
                            character: { type: "integer", description: "The 1-based character/column offset." }
                        }
                    }
                }
            },
            {
                name: 'find_derived_types',
                category: 'Project Understanding',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/project_understanding/findDerivedTypes',
                adapter: async (args, impl) => await impl(args.file_path, args.line !== undefined ? Math.max(0, parseInt(args.line, 10) - 1) : undefined, args.character !== undefined ? Math.max(0, parseInt(args.character, 10) - 1) : undefined),
                getProgressText: args => `Executing tool find_derived_types...`,
                schema: {
                    name: "find_derived_types",
                    description: "Finds subclasses, implementers, or derived types of a class/interface.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: { type: "string", description: "The relative or absolute file path containing the symbol." },
                            line: { type: "integer", description: "The 1-based line number of the symbol declaration." },
                            character: { type: "integer", description: "The 1-based character/column offset." }
                        }
                    }
                }
            },
            {
                name: 'find_callers',
                category: 'Project Understanding',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/project_understanding/findCallers',
                adapter: async (args, impl) => await impl(args.file_path, args.line !== undefined ? Math.max(0, parseInt(args.line, 10) - 1) : undefined, args.character !== undefined ? Math.max(0, parseInt(args.character, 10) - 1) : undefined),
                getProgressText: args => `Executing tool find_callers...`,
                schema: {
                    name: "find_callers",
                    description: "Finds methods/functions that call the symbol at a given location.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: { type: "string", description: "The relative or absolute file path containing the symbol." },
                            line: { type: "integer", description: "The 1-based line number of the symbol declaration." },
                            character: { type: "integer", description: "The 1-based character/column offset." }
                        }
                    }
                }
            },
            {
                name: 'find_callees',
                category: 'Project Understanding',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/project_understanding/findCallees',
                adapter: async (args, impl) => await impl(args.file_path, args.line !== undefined ? Math.max(0, parseInt(args.line, 10) - 1) : undefined, args.character !== undefined ? Math.max(0, parseInt(args.character, 10) - 1) : undefined),
                getProgressText: args => `Executing tool find_callees...`,
                schema: {
                    name: "find_callees",
                    description: "Finds methods/functions called by the symbol at a given location.",
                    parameters: {
                        type: "object",
                        properties: {
                            file_path: { type: "string", description: "The relative or absolute file path containing the symbol." },
                            line: { type: "integer", description: "The 1-based line number of the symbol declaration." },
                            character: { type: "integer", description: "The 1-based character/column offset." }
                        }
                    }
                }
            },
            {
                name: 'search_docs',
                category: 'Documentation',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/documentation/searchDocs',
                adapter: async (args, impl) => await impl(args.query),
                getProgressText: args => `Executing tool search_docs...`,
                schema: {
                    name: "search_docs",
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
                name: 'read_doc',
                category: 'Documentation',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/documentation/readDoc',
                adapter: async (args, impl) => await impl(args.docPath),
                getProgressText: args => `Executing tool read_doc...`,
                schema: {
                    name: "read_doc",
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
                name: 'lookup_api',
                category: 'Documentation',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/documentation/lookupApi',
                adapter: async (args, impl) => await impl(args.apiName),
                getProgressText: args => `Executing tool lookup_api...`,
                schema: {
                    name: "lookup_api",
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
                name: 'lookup_package',
                category: 'Documentation',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/documentation/lookupPackage',
                adapter: async (args, impl) => await impl(args.packageName),
                getProgressText: args => `Executing tool lookup_package...`,
                schema: {
                    name: "lookup_package",
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
                name: 'generate_doc_comment',
                category: 'Documentation',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/documentation/generateDocComment',
                adapter: async (args, impl) => await impl(args.signature),
                getProgressText: args => `Executing tool generate_doc_comment...`,
                schema: {
                    name: "generate_doc_comment",
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
                name: 'summarize_file',
                category: 'Documentation',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/documentation/summarizeFile',
                adapter: async (args, impl) => await impl(args.filePath),
                getProgressText: args => `Executing tool summarize_file...`,
                schema: {
                    name: "summarize_file",
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
                name: 'get_project_dependencies',
                category: 'Architecture Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/architecture_tools/getProjectDependencies',
                adapter: async (args, impl) => await impl(args.projectPath),
                getProgressText: args => `Executing tool get_project_dependencies...`,
                schema: {
                    name: "get_project_dependencies",
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
                name: 'find_module_dependencies',
                category: 'Architecture Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/architecture_tools/findModuleDependencies',
                adapter: async (args, impl) => await impl(args.filePath),
                getProgressText: args => `Executing tool find_module_dependencies...`,
                schema: {
                    name: "find_module_dependencies",
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
                name: 'find_cycles',
                category: 'Architecture Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/architecture_tools/findCycles',
                adapter: async (args, impl) => await impl(args.directory),
                getProgressText: args => `Executing tool find_cycles...`,
                schema: {
                    name: "find_cycles",
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
                name: 'analyze_layering',
                category: 'Architecture Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/architecture_tools/analyzeLayering',
                adapter: async (args, impl) => await impl(args.directory, args.rulesJsonStr),
                getProgressText: args => `Executing tool analyze_layering...`,
                schema: {
                    name: "analyze_layering",
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
                name: 'find_dead_code',
                category: 'Architecture Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/architecture_tools/findDeadCode',
                adapter: async (args, impl) => await impl(args.directory),
                getProgressText: args => `Executing tool find_dead_code...`,
                schema: {
                    name: "find_dead_code",
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
                name: 'find_duplicate_code',
                category: 'Architecture Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/architecture_tools/findDuplicateCode',
                adapter: async (args, impl) => await impl(args.directory),
                getProgressText: args => `Executing tool find_duplicate_code...`,
                schema: {
                    name: "find_duplicate_code",
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
                name: 'search_knowledge',
                category: 'RAG / Knowledge Base',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/rag_knowledge_base/searchKnowledge',
                adapter: async (args, impl) => await impl(args.query),
                getProgressText: args => `Executing tool search_knowledge...`,
                schema: {
                    name: "search_knowledge",
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
                name: 'read_knowledge_item',
                category: 'RAG / Knowledge Base',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/rag_knowledge_base/readKnowledgeItem',
                adapter: async (args, impl) => await impl(args.itemId),
                getProgressText: args => `Executing tool read_knowledge_item...`,
                schema: {
                    name: "read_knowledge_item",
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
                name: 'search_tickets',
                category: 'RAG / Knowledge Base',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/rag_knowledge_base/searchTickets',
                adapter: async (args, impl) => await impl(args.query),
                getProgressText: args => `Executing tool search_tickets...`,
                schema: {
                    name: "search_tickets",
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
                name: 'read_ticket',
                category: 'RAG / Knowledge Base',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/rag_knowledge_base/readTicket',
                adapter: async (args, impl) => await impl(args.ticketId),
                getProgressText: args => `Executing tool read_ticket...`,
                schema: {
                    name: "read_ticket",
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
                name: 'search_pull_requests',
                category: 'RAG / Knowledge Base',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/rag_knowledge_base/searchPullRequests',
                adapter: async (args, impl) => await impl(args.query),
                getProgressText: args => `Executing tool search_pull_requests...`,
                schema: {
                    name: "search_pull_requests",
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
                name: 'read_pull_request',
                category: 'RAG / Knowledge Base',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/rag_knowledge_base/readPullRequest',
                adapter: async (args, impl) => await impl(args.pullRequestId),
                getProgressText: args => `Executing tool read_pull_request...`,
                schema: {
                    name: "read_pull_request",
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
                name: 'search_design_docs',
                category: 'RAG / Knowledge Base',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/rag_knowledge_base/searchDesignDocs',
                adapter: async (args, impl) => await impl(args.query),
                getProgressText: args => `Executing tool search_design_docs...`,
                schema: {
                    name: "search_design_docs",
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
                name: 'search_decisions',
                category: 'RAG / Knowledge Base',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/rag_knowledge_base/searchDecisions',
                adapter: async (args, impl) => await impl(args.query),
                getProgressText: args => `Executing tool search_decisions...`,
                schema: {
                    name: "search_decisions",
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
                name: 'run_command',
                category: 'Agent Tools',
                isDestructive: true,
                isPatchingTool: false,
                modulePath: './tools/agent_tools/runCommand',
                adapter: async (args, impl) => await impl(args.command),
                getProgressText: args => `Executing tool run_command...`,
                schema: {
                    name: "run_command",
                    description: "Runs a command on the user's local terminal system (requires user confirmation).",
                    parameters: {
                        type: "object",
                        properties: {
                            command: { type: "string", description: "The shell command to execute." }
                        },
                        required: ["command"]
                    }
                }
            },
            {
                name: 'create_plan',
                category: 'Agent Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/agent_tools/createPlan',
                adapter: async (args, impl) => await impl(args.stepsInput),
                getProgressText: args => `Executing tool create_plan...`,
                schema: {
                    name: "create_plan",
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
                name: 'update_plan',
                category: 'Agent Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/agent_tools/updatePlan',
                adapter: async (args, impl) => await impl(args.stepsInput),
                getProgressText: args => `Executing tool update_plan...`,
                schema: {
                    name: "update_plan",
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
                name: 'mark_plan_step_complete',
                category: 'Agent Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/agent_tools/markPlanStepComplete',
                adapter: async (args, impl) => await impl(args.stepIndex),
                getProgressText: args => `Executing tool mark_plan_step_complete...`,
                schema: {
                    name: "mark_plan_step_complete",
                    description: "Marks a specific step in the plan as completed.",
                    parameters: {
                        type: "object",
                        properties: {
                            stepIndex: { type: "integer", description: "The 1-based index of the step to complete." }
                        },
                        required: ["stepIndex"]
                    }
                }
            },
            {
                name: 'create_task',
                category: 'Agent Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/agent_tools/createTask',
                adapter: async (args, impl) => await impl(args.description),
                getProgressText: args => `Executing tool create_task...`,
                schema: {
                    name: "create_task",
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
                name: 'complete_task',
                category: 'Agent Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/agent_tools/completeTask',
                adapter: async (args, impl) => await impl(args.taskId),
                getProgressText: args => `Executing tool complete_task...`,
                schema: {
                    name: "complete_task",
                    description: "Marks a tracking subtask complete.",
                    parameters: {
                        type: "object",
                        properties: {
                            taskId: { type: "integer", description: "The ID of the task to complete." }
                        },
                        required: ["taskId"]
                    }
                }
            },
            {
                name: 'request_user_confirmation',
                category: 'Agent Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/agent_tools/requestUserConfirmation',
                adapter: async (args, impl) => await impl(args.message),
                getProgressText: args => `Executing tool request_user_confirmation...`,
                schema: {
                    name: "request_user_confirmation",
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
                name: 'summarize_progress',
                category: 'Agent Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/agent_tools/summarizeProgress',
                adapter: async (args, impl) => await impl(),
                getProgressText: args => `Executing tool summarize_progress...`,
                schema: {
                    name: "summarize_progress",
                    description: "Summarizes what has been inspected, changed, learned, and what remains.",
                    parameters: {
                        type: "object",
                        properties: {}
                    }
                }
            },
            {
                name: 'save_session_memory',
                category: 'Agent Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/agent_tools/saveSessionMemory',
                adapter: async (args, impl) => await impl(args.memoryString),
                getProgressText: args => `Executing tool save_session_memory...`,
                schema: {
                    name: "save_session_memory",
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
                name: 'restore_session_memory',
                category: 'Agent Tools',
                isDestructive: false,
                isPatchingTool: false,
                modulePath: './tools/agent_tools/restoreSessionMemory',
                adapter: async (args, impl) => await impl(),
                getProgressText: args => `Executing tool restore_session_memory...`,
                schema: {
                    name: "restore_session_memory",
                    description: "Restores previous session task summary memory if present.",
                    parameters: {
                        type: "object",
                        properties: {}
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
