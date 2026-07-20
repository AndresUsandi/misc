const vscode = require('vscode');
const logger = require('../logger');
const fs = require('fs');
const path = require('path');
const os = require('os');
const cp = require('child_process');

function runCommandWithLogging(command, outputChannel = null, timeoutMs = 300000, cwd = null, token = null, logFilePath = null) {
    return new Promise((resolve) => {
        logger.logDebug(`[SWE-bench] Running: ${command}${cwd ? ` (cwd: ${cwd})` : ''}`);
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
                    logger.logCritical(`[SWE-bench] Command cancelled by user: ${command}`);
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
                logger.logCritical(`[SWE-bench] Command timed out after ${timeoutMs}ms: ${command}`);
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
            logger.logDebug(`[SWE-bench stdout] ${str.trim()}`);
            if (outputChannel) {
                outputChannel.append(str);
            } else if (logFilePath) {
                fs.appendFileSync(logFilePath, str);
            }
        });

        child.stderr.on('data', (data) => {
            const str = data.toString();
            stderr += str;
            logger.logDebug(`[SWE-bench stderr] ${str.trim()}`);
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
                logger.logDebug(`[SWE-bench] Finished with code ${code}`);
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
                logger.logCritical(`[SWE-bench] Process execution failed: ${err.message}`);
                resolve({
                    error: err,
                    stdout,
                    stderr
                });
            }
        });
    });
}

function extractPatch(rawOutput) {
    let code = rawOutput.trim();
    const markdownRegex = /```(?:diff)?\s*([\s\S]*?)```/;
    const match = code.match(markdownRegex);
    if (match) {
        code = match[1].trim();
    }
    return code;
}

async function evaluateSWEBench(sessionManager, extensionPath) {
    const selection = await vscode.window.showQuickPick(
        ["Run 1 task (Quick Test)", "Run 5 tasks (Small Test)", "Run all 300 tasks (Full Evaluation)", "Cancel"],
        { placeHolder: "Select the number of SWE-bench Lite tasks to evaluate" }
    );

    if (!selection || selection === "Cancel") return;

    let limit = 0;
    if (selection.startsWith("Run 1 ")) limit = 1;
    else if (selection.startsWith("Run 5 ")) limit = 5;
    else if (selection.startsWith("Run all")) limit = -1;

    if (!sessionManager.webviewClient) {
        await vscode.commands.executeCommand('chatsito.openChat');
        await new Promise(resolve => setTimeout(resolve, 1500));
    }

    const webviewClient = sessionManager.webviewClient;
    if (!webviewClient) {
        vscode.window.showErrorMessage("Failed to open Chatsito chat panel.");
        return;
    }

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
    sessionManager.selectedMode = 'ai';

    function restoreHooks() {
        webviewClient.sendCycleFinished = originalSendCycleFinished;
        webviewClient.sendError = originalSendError;
        sessionManager.selectedMode = originalMode;
    }

    const sweEvalDir = 'd:\\Temp\\swe_eval';
    if (!fs.existsSync(sweEvalDir)) {
        try {
            fs.mkdirSync(sweEvalDir, { recursive: true });
        } catch (e) {
            logger.logDebug(`[SWE-bench] Unable to create d:\\Temp\\swe_eval: ${e.message}. Using OS temp dir instead.`);
        }
    }

    const targetDir = fs.existsSync(sweEvalDir) ? sweEvalDir : path.join(os.tmpdir(), 'swe_eval');
    if (!fs.existsSync(targetDir)) {
        fs.mkdirSync(targetDir, { recursive: true });
    }

    const logFilePath = path.join(targetDir, 'chatsito_swe_eval.log');
    fs.writeFileSync(logFilePath, `--- Started SWE-bench evaluation at ${new Date().toISOString()} ---\n`);

    const outputChannel = vscode.window.createOutputChannel("SWE-bench Results");
    
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
    outputChannel.appendLine("[Chatsito] Starting SWE-bench evaluation flow...");

    try {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Chatsito: SWE-bench",
            cancellable: true
        }, async (progress, token) => {
            const datasetPath = path.join(targetDir, 'swe_problems.jsonl');
            const predictionsPath = path.join(targetDir, 'swe_predictions.jsonl');

            if (fs.existsSync(datasetPath)) {
                progress.report({ message: 'Using cached SWE-bench dataset...' });
                outputChannel.appendLine(`[Chatsito] Found cached dataset at ${datasetPath}, skipping download.`);
            } else {
                progress.report({ message: 'Fetching SWE-bench dataset via datasets library...' });
                outputChannel.appendLine("[Chatsito] Downloading SWE-bench_Lite via python datasets library...");

                const downloadCmd = `python -c "from datasets import load_dataset; ds = load_dataset('princeton-nlp/SWE-bench_Lite', split='test'); ds.to_json('${datasetPath.replace(/\\/g, '\\\\')}')"`;
                const dl = await runCommandWithLogging(downloadCmd, outputChannel, 300000, targetDir, token, logFilePath);
                
                if (dl.error) {
                    throw new Error(`Failed to download SWE-bench dataset. Make sure you have the 'datasets' python module installed. ${dl.stderr}`);
                }
                outputChannel.appendLine("[Chatsito] Dataset downloaded successfully.");
            }

            if (token.isCancellationRequested) throw new Error("Cancelled by user.");

            let lines = fs.readFileSync(datasetPath, 'utf8').split('\n').filter(l => l.trim().length > 0);
            let allTasks = lines.map(l => JSON.parse(l));
            
            let total = limit === -1 ? allTasks.length : Math.min(limit, allTasks.length);
            let predictions = [];

            outputChannel.appendLine(`[Chatsito] Evaluating ${total} tasks...`);

            for (let i = 0; i < total; i++) {
                if (token.isCancellationRequested) throw new Error("Cancelled by user.");

                const t = allTasks[i];
                progress.report({
                    message: `Evaluating task ${i + 1}/${total} (${t.instance_id})...`,
                    increment: (1 / total) * 50
                });
                outputChannel.appendLine(`[Chatsito] Running SWE-bench task ${i + 1}/${total}: ${t.instance_id}`);

                const prompt = `You are a software engineer. Solve the following GitHub issue for the repository ${t.repo}:
${t.problem_statement}

Please provide a unified diff block that fixes this issue. Provide only the patch inside a markdown diff block.`;
                webviewClient.sendNewMessage(prompt);

                const rawOutput = await new Promise((resolve, reject) => {
                    const checkCancel = setInterval(() => {
                        if (token.isCancellationRequested) {
                            clearInterval(checkCancel);
                            reject(new Error("Cancelled by user."));
                        }
                    }, 500);

                    onCycleFinished = () => {
                        clearInterval(checkCancel);
                        let finalMsg = '';
                        if (sessionManager.chatSession && sessionManager.chatSession.messages.length > 0) {
                            const lastMsg = sessionManager.chatSession.messages[sessionManager.chatSession.messages.length - 1];
                            if (lastMsg.role === 'model') {
                                finalMsg = lastMsg.parts.map(p => p.text || '').join('');
                            }
                        }
                        resolve(finalMsg);
                    };

                    onCycleError = (err) => {
                        clearInterval(checkCancel);
                        reject(err);
                    };
                });

                const patchCode = extractPatch(rawOutput);
                
                // SWE-Bench expects JSONL predictions: instance_id, model_name_or_path, model_patch
                predictions.push({
                    instance_id: t.instance_id,
                    model_name_or_path: "chatsito",
                    model_patch: patchCode
                });
            }

            restoreHooks();

            // Write predictions to JSONL
            outputChannel.appendLine(`[Chatsito] Saving ${predictions.length} predictions to ${predictionsPath}...`);
            const jsonlContent = predictions.map(p => JSON.stringify(p)).join('\n') + '\n';
            fs.writeFileSync(predictionsPath, jsonlContent, 'utf8');

            vscode.window.showInformationMessage(`SWE-bench generation complete! Prepared ${predictions.length} patches for evaluation. Running evaluation...`);

            if (predictions.length === 0) {
                outputChannel.appendLine("[Chatsito] No tasks completed, skipping evaluation.");
                return;
            }

            const repositoryPath = path.join(targetDir, 'SWE-bench');
            if (!fs.existsSync(repositoryPath)) {
                outputChannel.appendLine(`[Chatsito] SWE-bench repository not found. Cloning to: ${repositoryPath}`);
                const cloneCmd = `git clone https://github.com/princeton-nlp/SWE-bench.git "${repositoryPath}"`;
                const clone = await runCommandWithLogging(cloneCmd, outputChannel, 180000, null, token);
                if (clone.error) {
                    throw new Error(`Failed to clone SWE-bench repository: ${clone.stderr}`);
                }
            } else {
                outputChannel.appendLine(`[Chatsito] Using existing SWE-bench repository at: ${repositoryPath}`);
            }

            const checkSweCmd = 'python -c "import swebench"';
            outputChannel.appendLine(`[Chatsito] Checking package: ${checkSweCmd}`);
            const checkSwe = await runCommandWithLogging(checkSweCmd, null, 30000, null, token);

            if (checkSwe.error) {
                outputChannel.appendLine("[Chatsito] swebench package not found. Installing from cloned source...");
                const installCmd = `python -m pip install --user -e .`;
                const install = await runCommandWithLogging(installCmd, outputChannel, 180000, repositoryPath, token);
                if (install.error) {
                    throw new Error(`Failed to install swebench: ${install.stderr}`);
                }
                outputChannel.appendLine("[Chatsito] swebench installed successfully!");
            } else {
                outputChannel.appendLine("[Chatsito] swebench is already installed.");
            }

            const runId = `chatsito_eval_${Date.now()}`;
            // SWE-Bench can take a long time, increasing timeout to 2 hours
            const evalCmd = `python -m swebench.harness.run_evaluation --dataset_name princeton-nlp/SWE-bench_Lite --predictions_path "${predictionsPath}" --max_workers 4 --run_id ${runId}`;
            outputChannel.appendLine(`[Chatsito] Running evaluation (requires Docker!): ${evalCmd}`);

            const evaluation = await runCommandWithLogging(evalCmd, outputChannel, 3600000, repositoryPath, token, logFilePath);
            outputChannel.appendLine("\n=== SWE-bench Output ===");
            outputChannel.appendLine(evaluation.stdout);
            if (evaluation.stderr) {
                outputChannel.appendLine("\n=== Errors / Warnings ===");
                outputChannel.appendLine(evaluation.stderr);
                logger.logCritical(`SWE-bench python execution produced errors/warnings:\n${evaluation.stderr}`);
            }

            vscode.window.showInformationMessage("SWE-bench evaluation completed! See the 'SWE-bench Results' output channel for details.");
        });
    } catch (err) {
        restoreHooks();
        logger.logCritical(`SWE-bench evaluation failed: ${err.message}\n${err.stack || ''}`);
        outputChannel.appendLine(`\n[Chatsito] CRITICAL ERROR: ${err.message}`);
        vscode.window.showErrorMessage(`SWE-bench execution failed: ${err.message}`);
    }
}

module.exports = evaluateSWEBench;
