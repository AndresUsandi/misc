const vscode = require('vscode');
const https = require('https');
const zlib = require('zlib');
const fs = require('fs');
const path = require('path');
const os = require('os');

function downloadAndExtractHumanEval() {
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
        "This will run 164 tasks against the local LLM. It may take a long time. Do you want to proceed?",
        "Yes", "No"
    );

    if (confirmation !== "Yes") return;

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "Chatsito: HumanEval",
        cancellable: true
    }, async (progress, token) => {
        progress.report({ message: 'Downloading HumanEval dataset...' });

        let tasks;
        try {
            tasks = await downloadAndExtractHumanEval();
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to download HumanEval: ${error.message}`);
            return;
        }

        const samples = [];
        const apiClient = sessionManager.chatsitoApiClient;
        const total = tasks.length;
        
        let outputFile = '';
        if (vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0) {
            outputFile = path.join(vscode.workspace.workspaceFolders[0].uri.fsPath, 'samples.jsonl');
        } else {
            outputFile = path.join(os.tmpdir(), 'samples.jsonl');
        }

        // Clear or create the file
        fs.writeFileSync(outputFile, '');

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

            const systemPrompt = `You are an expert Python developer. Complete the following Python code exactly as requested. Output ONLY the raw Python code required to complete the function. Do not wrap it in markdown blocks. Do not add explanations.`;
            const userPrompt = task.prompt;

            const messages = [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: userPrompt }
            ];

            try {
                // Pass empty tools to prevent tool calling, forcing raw output
                const result = await apiClient.sendChat(messages, 2000, []);
                
                if (result.success && result.message && result.message.content) {
                    const completionCode = extractCodeCompletion(result.message.content);
                    const sample = {
                        task_id: task.task_id,
                        completion: completionCode
                    };
                    
                    // Append to file immediately in case of crash
                    fs.appendFileSync(outputFile, JSON.stringify(sample) + '\n');
                    samples.push(sample);
                } else {
                    console.error(`Task ${task.task_id} failed: No content returned.`);
                }
            } catch (error) {
                console.error(`Error processing task ${task.task_id}: ${error.message}`);
            }
        }

        vscode.window.showInformationMessage(`HumanEval generation complete! Wrote ${samples.length} samples to ${outputFile}. Run 'evaluate_functional_correctness samples.jsonl' to score!`);
    });
}

module.exports = evaluateHumanEval;
