const vscode = require('vscode');
const logger = require('../logger');
const https = require('https');
const zlib = require('zlib');
const fs = require('fs');
const path = require('path');
const os = require('os');
const cp = require('child_process');

function execCommand(cmd) {
    return new Promise((resolve) => {
        cp.exec(cmd, (error, stdout, stderr) => {
            resolve({
                error,
                stdout: stdout ? stdout.toString() : '',
                stderr: stderr ? stderr.toString() : ''
            });
        });
    });
}

function downloadAndExtractHumanEval(problemFilePath) {
    return new Promise((resolve, reject) => {
        const url = 'https://raw.githubusercontent.com/openai/human-eval/master/data/HumanEval.jsonl.gz';
        https.get(url, (response) => {
            if (response.statusCode !== 200) {
                return reject(new Error(`Failed to download HumanEval. Status: ${response.statusCode}`));
            }

            const gunzip = zlib.createGunzip();
            let rawData = '';

            gunzip.on('data', (chunk) => {
                rawData += chunk.toString();
            });

            gunzip.on('end', () => {
                try {
                    fs.writeFileSync(problemFilePath, rawData, 'utf8');
                } catch (e) {
                    // ignore
                }
                const tasks = rawData.split('\n')
                    .filter(line => line.trim())
                    .map(line => JSON.parse(line));
                resolve(tasks);
            });

            gunzip.on('error', reject);
            response.pipe(gunzip);
        }).on('error', reject);
    });
}

function extractCodeCompletion(rawOutput) {
    let code = rawOutput.trim();
    // Strip markdown code blocks if present
    const markdownRegex = /```(?:python)?\s*([\s\S]*?)```/;
    const match = code.match(markdownRegex);
    if (match) {
        code = match[1].trim();
    }
    return code;
}

async function evaluateHumanEval(sessionManager, extensionPath) {
    const confirmation = await vscode.window.showInformationMessage(
        "This will run 164 tasks against the local LLM. It will type prompts, execute them in the chat panel, and test them. Proceed?",
        "Yes", "No"
    );

    if (confirmation !== "Yes") return;

    // Ensure the chat panel is open
    if (!sessionManager.webviewClient) {
        await vscode.commands.executeCommand('chatsito.openChat');
        // Wait a short moment for the webview to register
        await new Promise(resolve => setTimeout(resolve, 1500));
    }

    const webviewClient = sessionManager.webviewClient;
    if (!webviewClient) {
        vscode.window.showErrorMessage("Failed to open Chatsito chat panel.");
        return;
    }

    // Intercept/hook into the webviewClient's cycle completion calls
    let onCycleFinished = null;
    let onCycleError = null;

    const originalSendCycleFinished = webviewClient.sendCycleFinished;
    webviewClient.sendCycleFinished = function () {
        originalSendCycleFinished.apply(webviewClient, arguments);
        if (onCycleFinished) {
            onCycleFinished();
        }
    };

    const originalSendError = webviewClient.sendError;
    webviewClient.sendError = function (msg) {
        originalSendError.apply(webviewClient, arguments);
        if (onCycleError) {
            onCycleError(new Error(msg));
        }
    };

    const originalMode = sessionManager.selectedMode;
    sessionManager.selectedMode = 'ai'; // Enable auto-approval of tool calls

    function restoreHooks() {
        webviewClient.sendCycleFinished = originalSendCycleFinished;
        webviewClient.sendError = originalSendError;
        sessionManager.selectedMode = originalMode;
    }

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "Chatsito: HumanEval",
        cancellable: true
    }, async (progress, token) => {
        const problemFilePath = (vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0)
            ? path.join(vscode.workspace.workspaceFolders[0].uri.fsPath, 'HumanEval.jsonl')
            : path.join(os.tmpdir(), 'HumanEval.jsonl');

        progress.report({ message: 'Downloading HumanEval dataset...' });

        let tasks;
        try {
            tasks = await downloadAndExtractHumanEval(problemFilePath);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to download HumanEval: ${error.message}`);
            restoreHooks();
            return;
        }

        const samples = [];
        const total = tasks.length;

        let outputFile = '';
        if (vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0) {
            outputFile = path.join(vscode.workspace.workspaceFolders[0].uri.fsPath, 'samples.jsonl');
        } else {
            outputFile = path.join(os.tmpdir(), 'samples.jsonl');
        }

        // Clear or create the file
        fs.writeFileSync(outputFile, '');

        const tempFilePath = path.join(vscode.workspace.workspaceFolders[0].uri.fsPath, 'humaneval_temp.py');

        // Create temp file once and open the editor
        fs.writeFileSync(tempFilePath, "");
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(tempFilePath));
        await vscode.window.showTextDocument(doc);

        for (let i = 0; i < total; i++) {
            if (token.isCancellationRequested) {
                vscode.window.showWarningMessage('HumanEval evaluation cancelled.');
                break;
            }

            const task = tasks[i];
            progress.report({
                message: `Task ${i + 1}/${total} (${task.task_id})...`,
                increment: (1 / total) * 100
            });

            // Write task prompt to temporary python file to simulate active document
            // Normalize newlines to Windows CRLF (\r\n) to standardize.
            const normalizedPrompt = task.prompt.replace(/\r\n/g, '\n');

            // Ensure the document is visible
            const isVisible = vscode.window.visibleTextEditors.some(e => e.document.uri.fsPath === tempFilePath);
            if (!isVisible) {
                await vscode.window.showTextDocument(doc);
            }

            // Replace entire document content using WorkspaceEdit
            const fullRange = new vscode.Range(
                doc.positionAt(0),
                doc.positionAt(doc.getText().length)
            );
            const workspaceEdit = new vscode.WorkspaceEdit();
            workspaceEdit.replace(doc.uri, fullRange, normalizedPrompt);
            await vscode.workspace.applyEdit(workspaceEdit);
            await doc.save();

            // 1. Clear chat history (new chat)
            sessionManager.resetSession();
            webviewClient.sendStateUpdate();
            await new Promise(resolve => setTimeout(resolve, 500));

            // 2. Formulate user prompt
            const userPrompt = `[EVALUATION SYSTEM] You are executing a test case for the purpose of evaluating the HumanEval benchmark.
Your active text editor has a partial function in the file 'humaneval_temp.py'.

Your instructions:
1. Bellow you will find a python function definition and a string inside it with instructions on what the function is supposed to do. You need to implement the function code as instructed by the text inside the string. 
2. Once you have decided what the code should be, you MUST use the 'replace_code' tool to edit 'humaneval_temp.py' and replace the original stub/docstring with the completed code.
3. Ensure you DO NOT USE ANY OTHER TOOLS OTHER THAN 'replace_code'. Specifically, do not use 'run_command', do not run tests, and do not execute shell commands.
4. When you are done making the file replacement, send a simple textual reply back (e.g. "Done.") confirming that you have done what you have done.
5. DO NOT ATTEMPT TO EXECUTE run_code TO TEST ANYTHING OR INVOKE ANY COMMANDS. This task is to generate code, not validate it.
6. When invoking 'replace_code', you MUST provide all required parameters:
   - 'expected_original_text': The exact code currently present at the specified range, matching spacing and characters exactly.
   - 'end_char': The 1-based character offset of the end of the range.
   Note: The active file uses LF (\n) line endings. Ensure your character offset calculations (especially 'end_char') account for the LF (not the CRLF) format when replacing lines.

Do not write explanations, and do not use any tools other than 'replace_code'.

Active file code stub:
${normalizedPrompt}`;

            // Create promise to await cycle completion
            const cyclePromise = new Promise((resolve, reject) => {
                onCycleFinished = resolve;
                onCycleError = reject;
            });

            // 3. Post to webview to simulate entering prompt and submitting
            webviewClient.postMessage('simulate_prompt', { prompt: userPrompt });

            try {
                // Wait for cycle to complete
                await cyclePromise;

                // 4. Retrieve output
                let completionCode = "";
                const currentText = doc.getText();

                if (currentText !== task.prompt) {
                    // File was modified by the tool
                    if (currentText.startsWith(task.prompt)) {
                        completionCode = currentText.slice(task.prompt.length);
                    } else {
                        completionCode = currentText;
                    }
                } else {
                    // File was not modified, extract from message
                    const history = sessionManager.conversationHistory;
                    const lastMessage = history[history.length - 1];
                    if (lastMessage && lastMessage.role === 'assistant' && lastMessage.content) {
                        completionCode = extractCodeCompletion(lastMessage.content);
                    }
                }

                if (completionCode) {
                    const sample = {
                        task_id: task.task_id,
                        completion: completionCode
                    };

                    // Append to file immediately
                    fs.appendFileSync(outputFile, JSON.stringify(sample) + '\n');
                    samples.push(sample);
                } else {
                    const failMsg = `Task ${task.task_id} failed: No completion produced (neither via tool nor chat).`;
                    console.error(failMsg);
                    logger.logCritical(failMsg);
                }
            } catch (error) {
                const errMsg = `Error processing task ${task.task_id}: ${error.message}`;
                console.error(errMsg);
                logger.logCritical(errMsg);
            } finally {
                // Do NOT close the editor here, we reuse it across tasks
            }

            // Pause after every test is completed and wait for "PROCEED"
            // let proceed = false;
            // while (!proceed) {
            //     if (token.isCancellationRequested) {
            //         break;
            //     }
            //     const result = await vscode.window.showInformationMessage(`test #${task.task_id} is completed, proceed?`, "PROCEED");
            //     if (result === "PROCEED") {
            //         proceed = true;
            //     }
            // }
        }

        // Cleanup the document after the entire run is complete
        try {
            await doc.save();
            await vscode.window.showTextDocument(doc, { preserveFocus: false });
            await vscode.commands.executeCommand('workbench.action.closeActiveEditor');
        } catch (e) {
            // ignore
        }
        if (fs.existsSync(tempFilePath)) {
            try {
                fs.unlinkSync(tempFilePath);
            } catch (e) {
                // ignore
            }
        }

        restoreHooks();

        vscode.window.showInformationMessage(`HumanEval generation complete! Wrote ${samples.length} samples to ${outputFile}. Running evaluation...`);

        // 5. Run HumanEval, auto-installing if missing
        try {
            const logFilePath = outputFile.replace('.jsonl', '.log');
            fs.writeFileSync(logFilePath, `--- Started HumanEval evaluation at ${new Date().toISOString()} ---\n`);

            const outputChannel = vscode.window.createOutputChannel("HumanEval Results");
            
            const originalAppendLine = outputChannel.appendLine.bind(outputChannel);
            outputChannel.appendLine = (value) => {
                originalAppendLine(value);
                try { fs.appendFileSync(logFilePath, value + '\n'); } catch (e) {}
            };
            
            const originalAppend = outputChannel.append.bind(outputChannel);
            outputChannel.append = (value) => {
                originalAppend(value);
                try { fs.appendFileSync(logFilePath, value); } catch (e) {}
            };

            outputChannel.show();
            outputChannel.appendLine("[Chatsito] Starting HumanEval evaluation flow...");

            if (samples.length === 0) {
                outputChannel.appendLine("[Chatsito] Warning: No samples generated. Skipping evaluation.");
                vscode.window.showWarningMessage("No samples generated. Skipping evaluation.");
                return;
            }

            // Filter the problem file to only include the attempted tasks
            if (fs.existsSync(problemFilePath)) {
                outputChannel.appendLine("[Chatsito] Filtering HumanEval dataset for attempted tasks...");
                const attemptedTaskIds = new Set(samples.map(s => s.task_id));
                const problemContent = fs.readFileSync(problemFilePath, 'utf8');
                const problemLines = problemContent.split('\n');
                const filteredLines = problemLines.filter(line => {
                    if (!line.trim()) return false;
                    try {
                        const prob = JSON.parse(line);
                        return attemptedTaskIds.has(prob.task_id);
                    } catch (e) {
                        return false;
                    }
                });
                fs.writeFileSync(problemFilePath, filteredLines.join('\n') + '\n', 'utf8');
                outputChannel.appendLine(`[Chatsito] Retained ${filteredLines.length} tasks matching generated samples.`);
            }

            // Check if human-eval is installed
            const checkCmd = 'python -c "import human_eval"';
            outputChannel.appendLine(`[Chatsito] Checking package: ${checkCmd}`);

            const check = await execCommand(checkCmd);
            if (check.error) {
                outputChannel.appendLine("[Chatsito] human-eval package not found. Preparing build environment (setuptools<82, wheel)...");
                const prepCmd = 'python -m pip install --user "setuptools<82" wheel';
                outputChannel.appendLine(`[Chatsito] Running: ${prepCmd}`);

                const prep = await execCommand(prepCmd);
                if (prep.error) {
                    outputChannel.appendLine(`[Chatsito] Setup preparation warning/error:\n${prep.stderr || prep.stdout}`);
                }

                // Clone human-eval locally to patch setup.py compatibility issue with modern pip
                const tempClonePath = path.join(os.tmpdir(), `human-eval-clone-${Date.now()}`);
                try {
                    if (fs.existsSync(tempClonePath)) {
                        fs.rmSync(tempClonePath, { recursive: true, force: true });
                    }
                } catch (e) {
                    // ignore
                }

                outputChannel.appendLine(`[Chatsito] Cloning human-eval repository to: ${tempClonePath}`);
                const cloneCmd = `git clone --depth 1 https://github.com/openai/human-eval.git "${tempClonePath}"`;
                const clone = await execCommand(cloneCmd);
                if (clone.error) {
                    outputChannel.appendLine(`[Chatsito] Clone failed:\n${clone.stderr || clone.stdout}`);
                    vscode.window.showErrorMessage("Failed to clone human-eval repository.");
                    return;
                }

                const setupPyPath = path.join(tempClonePath, 'setup.py');
                if (fs.existsSync(setupPyPath)) {
                    outputChannel.appendLine("[Chatsito] Patching setup.py for modern pip compatibility...");
                    let setupContent = fs.readFileSync(setupPyPath, 'utf8');
                    // Add ':main' callable suffix to entry point
                    setupContent = setupContent.replace(
                        /["']evaluate_functional_correctness\s*=\s*human_eval\.evaluate_functional_correctness["']/g,
                        '"evaluate_functional_correctness = human_eval.evaluate_functional_correctness:main"'
                    );
                    fs.writeFileSync(setupPyPath, setupContent, 'utf8');
                }

                outputChannel.appendLine("[Chatsito] Installing human-eval from patched local source...");
                const installCmd = `python -m pip install --user "${tempClonePath}"`;
                outputChannel.appendLine(`[Chatsito] Running: ${installCmd}`);

                const install = await execCommand(installCmd);
                if (install.error) {
                    outputChannel.appendLine(`[Chatsito] Installation failed:\n${install.stderr || install.stdout}`);
                    vscode.window.showErrorMessage("Failed to automatically install human-eval.");
                    return;
                }
                outputChannel.appendLine("[Chatsito] human-eval installed successfully!");

                try {
                    fs.rmSync(tempClonePath, { recursive: true, force: true });
                } catch (e) {
                    // ignore
                }
            } else {
                outputChannel.appendLine("[Chatsito] human-eval is already installed.");
            }

            // Patch human-eval for Windows multiprocessing and signals compatibility
            await patchInstalledHumanEval(outputChannel);

            // Run functional correctness
            const evalCmd = `python -m human_eval.evaluate_functional_correctness "${outputFile}" --problem_file="${problemFilePath}"`;
            outputChannel.appendLine(`[Chatsito] Running evaluation: ${evalCmd}`);

            const evaluation = await execCommand(evalCmd);
            outputChannel.appendLine("\n=== HumanEval Output ===");
            outputChannel.appendLine(evaluation.stdout);
            if (evaluation.stderr) {
                outputChannel.appendLine("\n=== Errors / Warnings ===");
                outputChannel.appendLine(evaluation.stderr);
                logger.logCritical(`HumanEval python execution produced errors/warnings:\n${evaluation.stderr}`);
            }

            vscode.window.showInformationMessage("HumanEval evaluation completed! See the 'HumanEval Results' output channel for the score.");
        } catch (termErr) {
            vscode.window.showErrorMessage(`Failed to execute HumanEval: ${termErr.message}`);
            logger.logCritical(`HumanEval execution threw exception: ${termErr.message}\n${termErr.stack || ''}`);
        } finally {
            if (problemFilePath && fs.existsSync(problemFilePath)) {
                try {
                    fs.unlinkSync(problemFilePath);
                } catch (e) {
                    // ignore
                }
            }
        }
    });
}

async function patchInstalledHumanEval(outputChannel) {
    try {
        const getPathCmd = 'python -c "import human_eval; print(human_eval.__file__)"';
        const result = await execCommand(getPathCmd);
        if (result.error || !result.stdout) {
            return false;
        }
        const initPath = result.stdout.trim();
        const moduleDir = path.dirname(initPath);

        // 1. Patch evaluate_functional_correctness.py to wrap sys.exit(main()) in if __name__ == '__main__':
        const evalPyPath = path.join(moduleDir, 'evaluate_functional_correctness.py');
        if (fs.existsSync(evalPyPath)) {
            let content = fs.readFileSync(evalPyPath, 'utf8');
            if (content.includes('sys.exit(main())') && !content.includes("if __name__ == '__main__':")) {
                outputChannel.appendLine("[Chatsito] Patching evaluate_functional_correctness.py for Windows multiprocessing compatibility...");
                content = content.replace(
                    /sys\.exit\(main\(\)\)/g,
                    "if __name__ == '__main__':\n    sys.exit(main())"
                );
                fs.writeFileSync(evalPyPath, content, 'utf8');
            }
        }

        // 2. Patch execution.py to prevent Windows signal/setitimer crash
        const execPyPath = path.join(moduleDir, 'execution.py');
        if (fs.existsSync(execPyPath)) {
            let content = fs.readFileSync(execPyPath, 'utf8');
            if (content.includes("signal.setitimer(signal.ITIMER_REAL, seconds)") && !content.includes("if hasattr(signal, 'setitimer'):")) {
                outputChannel.appendLine("[Chatsito] Patching execution.py for Windows signals compatibility...");
                const oldTimeLimit = `def time_limit(seconds: float):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")

    signal.setitimer(signal.ITIMER_REAL, seconds)
    signal.signal(signal.SIGALRM, signal_handler)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)`;

                const newTimeLimit = `def time_limit(seconds: float):
    if hasattr(signal, 'setitimer'):
        def signal_handler(signum, frame):
            raise TimeoutException("Timed out!")
        signal.setitimer(signal.ITIMER_REAL, seconds)
        signal.signal(signal.SIGALRM, signal_handler)
        try:
            yield
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
    else:
        try:
            yield
        finally:
            pass`;

                content = content.replace(/\r\n/g, '\n');
                const normalizedOld = oldTimeLimit.replace(/\r\n/g, '\n');
                const normalizedNew = newTimeLimit.replace(/\r\n/g, '\n');
                if (content.includes(normalizedOld)) {
                    content = content.replace(normalizedOld, normalizedNew);
                    fs.writeFileSync(execPyPath, content, 'utf8');
                } else {
                    // Fallback replacement of raw lines
                    content = content.replace(
                        /signal\.setitimer\(signal\.ITIMER_REAL, seconds\)/g,
                        "if hasattr(signal, 'setitimer'): signal.setitimer(signal.ITIMER_REAL, seconds)"
                    );
                    content = content.replace(
                        /signal\.signal\(signal\.SIGALRM, signal_handler\)/g,
                        "if hasattr(signal, 'SIGALRM'): signal.signal(signal.SIGALRM, signal_handler)"
                    );
                    content = content.replace(
                        /signal\.setitimer\(signal\.ITIMER_REAL, 0\)/g,
                        "if hasattr(signal, 'setitimer'): signal.setitimer(signal.ITIMER_REAL, 0)"
                    );
                    fs.writeFileSync(execPyPath, content, 'utf8');
                }
            }
        }
        return true;
    } catch (e) {
        outputChannel.appendLine(`[Chatsito] Failed to patch installed files: ${e.message}`);
        return false;
    }
}

module.exports = evaluateHumanEval;
