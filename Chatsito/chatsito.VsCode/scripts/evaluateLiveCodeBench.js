const vscode = require('vscode');
const logger = require('../logger');
const fs = require('fs');
const path = require('path');
const os = require('os');
const cp = require('child_process');

function runCommandWithLogging(command, outputChannel = null, timeoutMs = 300000, cwd = null, token = null, logFilePath = null) {
    return new Promise((resolve) => {
        logger.logDebug(`[LiveCodeBench] Running: ${command}${cwd ? ` (cwd: ${cwd})` : ''}`);
        if (outputChannel) {
            outputChannel.appendLine(`[Chatsito] Running command: ${command}`);
        }

        const spawnOptions = { shell: true };
        if (cwd) {
            spawnOptions.cwd = cwd;
        }
        const child = cp.spawn(command, spawnOptions);
        let stdout = '';
        let stderr = '';
        let resolved = false;

        const killChild = () => {
            try {
                if (process.platform === 'win32') {
                    cp.execSync(`taskkill /pid ${child.pid} /T /F`);
                } else {
                    child.kill();
                }
            } catch (e) {
                try { child.kill(); } catch (err) { }
            }
        };

        let tokenListener = null;
        if (token) {
            tokenListener = token.onCancellationRequested(() => {
                if (!resolved) {
                    resolved = true;
                    logger.logCritical(`[LiveCodeBench] Command cancelled by user: ${command}`);
                    if (outputChannel) {
                        outputChannel.appendLine(`\n[Chatsito] WARNING: Command cancelled by user.`);
                    }
                    killChild();
                    resolve({
                        error: new Error(`Command cancelled by user: ${command}`),
                        stdout,
                        stderr
                    });
                }
            });
        }

        const timeoutId = setTimeout(() => {
            if (!resolved) {
                resolved = true;
                logger.logCritical(`[LiveCodeBench] Command timed out after ${timeoutMs}ms: ${command}`);
                if (outputChannel) {
                    outputChannel.appendLine(`\n[Chatsito] ERROR: Command timed out after ${timeoutMs / 1000}s.`);
                }
                killChild();
                resolve({
                    error: new Error(`Command timed out: ${command}`),
                    stdout,
                    stderr
                });
            }
        }, timeoutMs);

        child.stdout.on('data', (data) => {
            const str = data.toString();
            stdout += str;
            logger.logDebug(`[LiveCodeBench stdout] ${str.trim()}`);
            if (outputChannel) {
                outputChannel.append(str);
            } else if (logFilePath) {
                fs.appendFileSync(logFilePath, str);
            }
        });

        child.stderr.on('data', (data) => {
            const str = data.toString();
            stderr += str;
            logger.logDebug(`[LiveCodeBench stderr] ${str.trim()}`);
            if (outputChannel) {
                outputChannel.append(str);
            } else if (logFilePath) {
                fs.appendFileSync(logFilePath, str);
            }
        });

        child.on('close', (code) => {
            if (!resolved) {
                resolved = true;
                clearTimeout(timeoutId);
                if (tokenListener) tokenListener.dispose();
                logger.logDebug(`[LiveCodeBench] Finished with code ${code}`);
                resolve({
                    error: code !== 0 ? new Error(`Command exited with code ${code}`) : null,
                    stdout,
                    stderr
                });
            }
        });

        child.on('error', (err) => {
            if (!resolved) {
                resolved = true;
                clearTimeout(timeoutId);
                if (tokenListener) tokenListener.dispose();
                logger.logCritical(`[LiveCodeBench] Process execution failed: ${err.message}`);
                resolve({
                    error: err,
                    stdout,
                    stderr
                });
            }
        });
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

async function evaluateLiveCodeBench(sessionManager, extensionPath) {
    const selection = await vscode.window.showQuickPick(
        [
            "Run 20 tasks (Quick Test)",
            "Run 50 tasks (Medium)",
            "Run 100 tasks (Large)",
            "Run 250 tasks (Very Large)",
            "Run 500 tasks (Extended)",
            "Run all tasks (Full Evaluation)",
            "Cancel"
        ],
        { placeHolder: "Select the number of LiveCodeBench tasks to evaluate" }
    );

    if (!selection || selection === "Cancel") return;

    let limit = 0;
    if (selection.startsWith("Run 20")) limit = 20;
    else if (selection.startsWith("Run 50")) limit = 50;
    else if (selection.startsWith("Run 100")) limit = 100;
    else if (selection.startsWith("Run 250")) limit = 250;
    else if (selection.startsWith("Run 500")) limit = 500;
    else if (selection.startsWith("Run all")) limit = -1;

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

    const lcbEvalDir = 'd:\\Temp\\lcb_eval';
    if (!fs.existsSync(lcbEvalDir)) {
        try {
            fs.mkdirSync(lcbEvalDir, { recursive: true });
        } catch (e) {
            // Fallback to temp directory if D: drive is unavailable or read-only
            logger.logDebug(`[LiveCodeBench] Unable to create d:\\Temp\\lcb_eval: ${e.message}. Using OS temp dir instead.`);
        }
    }

    const targetDir = fs.existsSync(lcbEvalDir) ? lcbEvalDir : path.join(os.tmpdir(), 'lcb_eval');
    if (!fs.existsSync(targetDir)) {
        fs.mkdirSync(targetDir, { recursive: true });
    }

    const logFilePath = path.join(targetDir, 'chatsito_lcb_eval.log');
    fs.writeFileSync(logFilePath, `--- Started LiveCodeBench evaluation at ${new Date().toISOString()} ---\n`);

    const outputChannel = vscode.window.createOutputChannel("LiveCodeBench Results");
    
    // Mirror all output channel writes to the log file
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
    outputChannel.appendLine("[Chatsito] Starting LiveCodeBench evaluation flow...");

    try {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Chatsito: LiveCodeBench",
            cancellable: true
        }, async (progress, token) => {
            const getProblemsPy = path.join(targetDir, 'get_problems.py');
            const problemsJsonPath = path.join(targetDir, 'lcb_problems.json');

            if (fs.existsSync(problemsJsonPath)) {
                progress.report({ message: 'Using cached LiveCodeBench dataset...' });
                outputChannel.appendLine(`[Chatsito] Found cached dataset at ${problemsJsonPath}, skipping download.`);
            } else {
                progress.report({ message: 'Fetching LiveCodeBench dataset test splits from Hugging Face (this may take a moment)...' });
                outputChannel.appendLine("[Chatsito] Fetching LiveCodeBench dataset test splits from Hugging Face...");

                const https = require('https');
                const readline = require('readline');
                const problems = [];
                const testFiles = ["test.jsonl", "test2.jsonl", "test3.jsonl", "test4.jsonl", "test5.jsonl", "test6.jsonl"];

                for (const testFile of testFiles) {
                    if (token.isCancellationRequested) {
                        throw new Error("Cancelled by user.");
                    }
                    const url = `https://huggingface.co/datasets/livecodebench/code_generation_lite/resolve/main/${testFile}`;
                    outputChannel.appendLine(`[Chatsito] Downloading ${url}...`);

                    await new Promise((resolve, reject) => {
                        const fetchUrl = (currentUrl) => {
                            https.get(currentUrl, (res) => {
                                if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
                                    fetchUrl(res.headers.location);
                                    return;
                                }
                                if (res.statusCode !== 200) {
                                    if (res.statusCode === 404) {
                                        resolve(); // some test files might not exist, skip
                                        return;
                                    }
                                    reject(new Error(`Failed to fetch ${testFile}: HTTP ${res.statusCode}`));
                                    return;
                                }

                                const rl = readline.createInterface({
                                    input: res,
                                    crlfDelay: Infinity
                                });

                                rl.on('line', (line) => {
                                    if (!line.trim()) return;
                                    try {
                                        const row = JSON.parse(line);
                                        problems.push({
                                            question_id: row.question_id,
                                            question_title: row.question_title || "",
                                            question_content: row.question_content || "",
                                            starter_code: row.starter_code || ""
                                        });
                                    } catch (e) {
                                        // ignore parse errors
                                    }
                                });

                                rl.on('close', () => resolve());
                            }).on('error', err => reject(err));
                        };
                        fetchUrl(url);
                    });
                }

                if (problems.length === 0) {
                    throw new Error("Failed to retrieve LiveCodeBench problems. No valid data found.");
                }
                outputChannel.appendLine(`[Chatsito] Successfully fetched ${problems.length} tasks.`);

                // Write JSON in a streaming fashion to avoid V8 string length limits
                const tempJsonPath = problemsJsonPath + ".tmp";
                const fd = fs.openSync(tempJsonPath, 'w');
                fs.writeSync(fd, '[\n');
                for (let i = 0; i < problems.length; i++) {
                    fs.writeSync(fd, JSON.stringify(problems[i], null, 2));
                    if (i < problems.length - 1) fs.writeSync(fd, ',\n');
                    else fs.writeSync(fd, '\n');
                }
                fs.writeSync(fd, ']\n');
                fs.closeSync(fd);
                fs.renameSync(tempJsonPath, problemsJsonPath);
            }

            let allTasks = JSON.parse(fs.readFileSync(problemsJsonPath, 'utf8'));
            let tasks = allTasks;
            if (limit > 0) {
                tasks = allTasks.slice(0, limit);
            }

            const samples = [];
            const total = tasks.length;
            const outputFile = path.join(targetDir, 'samples.json');
            fs.writeFileSync(outputFile, '[]', 'utf8');

            const tempFilePath = (vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0)
                ? path.join(vscode.workspace.workspaceFolders[0].uri.fsPath, 'livecodebench_temp.py')
                : path.join(os.tmpdir(), 'livecodebench_temp.py');

            // Create temp file once and open the editor
            fs.writeFileSync(tempFilePath, "");
            const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(tempFilePath));
            let activeEditor = await vscode.window.showTextDocument(doc);

            for (let i = 0; i < total; i++) {
                if (token.isCancellationRequested) {
                    vscode.window.showWarningMessage('LiveCodeBench evaluation cancelled.');
                    break;
                }

                const task = tasks[i];
                progress.report({
                    message: `Task ${i + 1}/${total} (${task.question_id})...`,
                    increment: (1 / total) * 100
                });
                outputChannel.appendLine(`[Chatsito] Running LiveCodeBench task ${i + 1}/${total}: ${task.question_id}`);

                const starterCode = task.starter_code || "# Write your python solution here";

                // Ensure the document is visible
                const isVisible = vscode.window.visibleTextEditors.some(e => e.document.uri.fsPath === tempFilePath);
                if (!isVisible) {
                    await vscode.window.showTextDocument(doc);
                }

                // Replace entire document content using WorkspaceEdit instead of TextEditor.edit
                // This prevents "TextEditor#edit not possible on closed editors" if focus is lost
                const fullRange = new vscode.Range(
                    doc.positionAt(0),
                    doc.positionAt(doc.getText().length)
                );
                const workspaceEdit = new vscode.WorkspaceEdit();
                workspaceEdit.replace(doc.uri, fullRange, starterCode);
                await vscode.workspace.applyEdit(workspaceEdit);
                await doc.save();

                sessionManager.resetSession();
                webviewClient.sendStateUpdate();
                await new Promise(resolve => setTimeout(resolve, 500));

                const userPrompt = `[EVALUATION SYSTEM] You are executing a test case for the purpose of evaluating the LiveCodeBench benchmark.
Your active text editor has a partial function/stub in the file 'livecodebench_temp.py'.

Your instructions:
1. Below you will find the problem description and starter code. You need to implement the solution code.
2. Once you have decided what the code should be, you MUST use the 'replace_code' tool to edit 'livecodebench_temp.py' and replace the original stub with the completed code.
3. Ensure you DO NOT USE ANY OTHER TOOLS OTHER THAN 'replace_code'. Specifically, do not use 'run_command', do not run tests, and do not execute shell commands.
4. When you are done making the file replacement, send a simple textual reply back (e.g. "Done.") confirming that you have done what you have done.
5. DO NOT ATTEMPT TO EXECUTE run_code TO TEST ANYTHING OR INVOKE ANY COMMANDS. This task is to generate code, not validate it.
6. When invoking 'replace_code', you MUST provide all required parameters.

Problem Description:
${task.question_content}

Starter Code:
${starterCode}`;

                const cyclePromise = new Promise((resolve, reject) => {
                    onCycleFinished = resolve;
                    onCycleError = reject;
                });

                webviewClient.postMessage('simulate_prompt', { prompt: userPrompt });

                try {
                    await cyclePromise;

                    let completionCode = "";
                    const currentText = doc.getText();

                    if (currentText !== starterCode) {
                        completionCode = currentText;
                    } else {
                        const history = sessionManager.conversationHistory;
                        const lastMessage = history[history.length - 1];
                        if (lastMessage && lastMessage.role === 'assistant' && lastMessage.content) {
                            completionCode = extractCodeCompletion(lastMessage.content);
                        }
                    }

                    const sample = {
                        question_id: task.question_id,
                        code_list: [completionCode || ""]
                    };

                    samples.push(sample);
                    fs.writeFileSync(outputFile, JSON.stringify(samples, null, 2), 'utf8');
                } catch (error) {
                    const errMsg = `Error processing task ${task.question_id}: ${error.message}`;
                    console.error(errMsg);
                    logger.logCritical(errMsg);
                    outputChannel.appendLine(`[Chatsito] ERROR: ${errMsg}`);
                }
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

            // We no longer pad samples, to ensure LiveCodeBench only evaluates the tasks that were generated
            // This prevents unselected tasks from artificially lowering the final score.
            vscode.window.showInformationMessage(`LiveCodeBench generation complete! Prepared ${samples.length} samples for evaluation. Running evaluation...`);

            if (samples.length === 0) {
                outputChannel.appendLine("[Chatsito] Warning: No samples generated. Skipping evaluation.");
                vscode.window.showWarningMessage("No samples generated. Skipping evaluation.");
                return;
            }

            const repositoryPath = path.join(targetDir, 'LiveCodeBench');
            if (!fs.existsSync(repositoryPath)) {
                outputChannel.appendLine(`[Chatsito] LiveCodeBench repository not found. Cloning to: ${repositoryPath}`);
                const cloneCmd = `git clone --depth 1 https://github.com/LiveCodeBench/LiveCodeBench.git "${repositoryPath}"`;
                const clone = await runCommandWithLogging(cloneCmd, outputChannel, 180000, null, token, logFilePath);
                if (clone.error) {
                    throw new Error(`Failed to clone LiveCodeBench repository: ${clone.stderr}`);
                }
            } else {
                outputChannel.appendLine(`[Chatsito] Using existing LiveCodeBench repository at: ${repositoryPath}`);
            }

            // Patch LiveCodeBench to prevent Windows SIGALRM crash and limit memory/cpu exhaustion
            if (process.platform === 'win32') {
                const testingUtilPath = path.join(repositoryPath, 'lcb_runner', 'evaluation', 'testing_util.py');
                if (fs.existsSync(testingUtilPath)) {
                    let testingUtilCode = fs.readFileSync(testingUtilPath, 'utf8');
                    let patched = false;

                    const windowsTimeoutCode = `
import threading
import _thread
def win_timeout_handler():
    try:
        _thread.interrupt_main()
    except:
        pass

class WinTimeout:
    def __init__(self):
        self.timer = None
    def set_timeout(self, timeout):
        if self.timer:
            self.timer.cancel()
        if timeout > 0:
            self.timer = threading.Timer(timeout, win_timeout_handler)
            self.timer.start()

win_timeout = WinTimeout()
`.trim();

                    if (!testingUtilCode.includes('class WinTimeout')) {
                        testingUtilCode = testingUtilCode.replace('import signal', 'import signal\n\n' + windowsTimeoutCode);
                        patched = true;
                    }

                    if (testingUtilCode.includes('signal.signal(signal.SIGALRM')) {
                        testingUtilCode = testingUtilCode.replace(/signal\.signal\(signal\.SIGALRM, timeout_handler\)/g, 'pass # Patched for Windows');
                        patched = true;
                    }
                    if (testingUtilCode.includes('signal.alarm(')) {
                        testingUtilCode = testingUtilCode.replace(/signal\.alarm\(([^)]*)\)/g, 'win_timeout.set_timeout($1) # Patched for Windows');
                        patched = true;
                    }

                    const limitedStringIO = `
from io import StringIO
class LimitedStringIO(StringIO):
    def __init__(self, max_chars=1024 * 1024):
        super().__init__()
        self.max_chars = max_chars
    def write(self, s):
        if self.tell() < self.max_chars:
            super().write(s)
        return len(s)
`.trim();
                    if (!testingUtilCode.includes('class LimitedStringIO')) {
                        testingUtilCode = testingUtilCode.replace('class Capturing(list):', limitedStringIO + '\n\nclass Capturing(list):');
                        testingUtilCode = testingUtilCode.replace(/self\._stringio = StringIO\(\)/g, 'self._stringio = LimitedStringIO()');
                        patched = true;
                    }

                    if (!testingUtilCode.includes('except BaseException as e:')) {
                        testingUtilCode = testingUtilCode.replace(/except Exception as e:/g, 'except BaseException as e:');
                        patched = true;
                    }

                    if (!testingUtilCode.includes('"keyboardinterrupt" in repr(e).lower()')) {
                        testingUtilCode = testingUtilCode.replace(/if "timeoutexception" in repr\(e\)\.lower\(\):/g, 'if "timeoutexception" in repr(e).lower() or "keyboardinterrupt" in repr(e).lower():');
                        patched = true;
                    }

                    if (patched) {
                        fs.writeFileSync(testingUtilPath, testingUtilCode, 'utf8');
                        outputChannel.appendLine(`[Chatsito] Patched LiveCodeBench testing_util.py to bypass SIGALRM and limit memory on Windows.`);
                    }
                }
            }

            // Patch compute_code_generation_metrics.py to limit workers to 2 to prevent PC freeze
            const computeMetricsPath = path.join(repositoryPath, 'lcb_runner', 'evaluation', 'compute_code_generation_metrics.py');
            if (fs.existsSync(computeMetricsPath)) {
                let computeCode = fs.readFileSync(computeMetricsPath, 'utf8');
                if (computeCode.includes('max_workers=1 if debug else num_process_evaluate')) {
                    computeCode = computeCode.replace(/max_workers=1 if debug else num_process_evaluate/g, 'max_workers=1 if debug else 2');
                    fs.writeFileSync(computeMetricsPath, computeCode, 'utf8');
                    outputChannel.appendLine(`[Chatsito] Patched LiveCodeBench compute_code_generation_metrics.py to limit workers to 2.`);
                }
            }

            // Patch compute_code_execution_metrics.py
            const computeExecutionMetricsPath = path.join(repositoryPath, 'lcb_runner', 'evaluation', 'compute_code_execution_metrics.py');
            if (fs.existsSync(computeExecutionMetricsPath)) {
                let computeCode = fs.readFileSync(computeExecutionMetricsPath, 'utf8');
                if (computeCode.includes('ProcessPoolExecutor()')) {
                    computeCode = computeCode.replace(/ProcessPoolExecutor\(\)/g, 'ProcessPoolExecutor(max_workers=2)');
                    fs.writeFileSync(computeExecutionMetricsPath, computeCode, 'utf8');
                }
            }

            // Patch custom_evaluator to evaluate a subset of tasks without crashing
            const customEvaluatorPath = path.join(repositoryPath, 'lcb_runner', 'runner', 'custom_evaluator.py');
            if (fs.existsSync(customEvaluatorPath)) {
                let evalCode = fs.readFileSync(customEvaluatorPath, 'utf8');
                if (!evalCode.includes('benchmark = [b for b in benchmark')) {
                    const filterCode = `if isinstance(custom_outputs, list) and len(custom_outputs) > 0 and isinstance(custom_outputs[0], dict):
            valid_ids = set(str(x.get("question_id", x.get("id"))) for x in custom_outputs)
            benchmark = [b for b in benchmark if str(getattr(b, "question_id", getattr(b, "id", ""))) in valid_ids]
        assert len(custom_outputs) == len(benchmark), f"{len(custom_outputs)} != {len(benchmark)}"`;
                    evalCode = evalCode.replace('assert len(custom_outputs) == len(benchmark), f"{len(custom_outputs)} != {len(benchmark)}"', filterCode);
                    fs.writeFileSync(customEvaluatorPath, evalCode, 'utf8');
                    outputChannel.appendLine(`[Chatsito] Patched LiveCodeBench custom_evaluator.py to evaluate exact subset.`);
                }
            }

            const checkLcbCmd = 'python -c "import lcb_runner"';
            outputChannel.appendLine(`[Chatsito] Checking package: ${checkLcbCmd}`);
            const checkLcb = await runCommandWithLogging(checkLcbCmd, null, 30000, null, token, logFilePath);

            if (checkLcb.error) {
                outputChannel.appendLine("[Chatsito] lcb_runner package not found in Python path. Installing from cloned source in editable mode...");
                const installCmd = `python -m pip install --user -e .`;
                const install = await runCommandWithLogging(installCmd, outputChannel, 180000, repositoryPath, token, logFilePath);
                if (install.error) {
                    throw new Error(`Failed to install lcb_runner: ${install.stderr}`);
                }
                outputChannel.appendLine("[Chatsito] lcb_runner installed successfully!");
            } else {
                outputChannel.appendLine("[Chatsito] lcb_runner is already installed.");
            }

            const evalCmd = `python -m lcb_runner.runner.custom_evaluator --custom_output_file "${outputFile}"`;
            outputChannel.appendLine(`[Chatsito] Running evaluation: ${evalCmd}`);

            const evaluation = await runCommandWithLogging(evalCmd, outputChannel, 7200000, repositoryPath, token, logFilePath);
            outputChannel.appendLine("\n=== LiveCodeBench Output ===");
            outputChannel.appendLine(evaluation.stdout);
            if (evaluation.stderr) {
                outputChannel.appendLine("\n=== Errors / Warnings ===");
                outputChannel.appendLine(evaluation.stderr);
                logger.logCritical(`LiveCodeBench python execution produced errors/warnings:\n${evaluation.stderr}`);
            }

            vscode.window.showInformationMessage("LiveCodeBench evaluation completed! See the 'LiveCodeBench Results' output channel for the score.");
        });
    } catch (err) {
        restoreHooks();
        logger.logCritical(`LiveCodeBench evaluation failed: ${err.message}\n${err.stack || ''}`);
        outputChannel.appendLine(`\n[Chatsito] CRITICAL ERROR: ${err.message}`);
        vscode.window.showErrorMessage(`LiveCodeBench execution failed: ${err.message}`);
    }
}

module.exports = evaluateLiveCodeBench;
