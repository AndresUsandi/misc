import { exec } from 'child_process';
import { promisify } from 'util';
import ChatsitoApiClient from './ChatsitoApiClient.js';
import ChatSessionManager from './ChatSessionManager.js';

const execAsync = promisify(exec);

const webviewClient = {
  sendProgress(msg) {
    console.log(`[PROGRESS] ${msg}`);
  },
  sendStateUpdate() {
    // No-op for CLI
  },
  sendError(err) {
    console.error(`[CLIENT ERROR] ${err}`);
  },
  sendCycleFinished() {
    console.log('[CLIENT CYCLE FINISHED]');
  }
};

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.error('Error: No arguments provided.');
    console.log('Usage:');
    console.log('  node index.js "git diff"');
    console.log('  node index.js "git show <commit-hash>"');
    process.exit(1);
  }

  // Find and strip --url option if present
  let url = 'http://localhost:5257';
  const urlArgIndex = args.indexOf('--url');
  if (urlArgIndex !== -1 && urlArgIndex + 1 < args.length) {
    url = args[urlArgIndex + 1];
    args.splice(urlArgIndex, 2);
  }

  const inputCommand = args.join(' ').trim();
  console.log(`Received input command: "${inputCommand}"`);

  console.log(`Connecting to Chatsito server at ${url}...`);
  try {
    const client = new ChatsitoApiClient(url);
    await client.initialize();
    console.log('--- CHATSITO CONFIG ---');
    console.log(`Active Model: ${client.activeModel}`);
    console.log(`Timeout: ${client.timeoutMins} mins`);
    console.log(`Max Tool Iterations: ${client.maxToolIterations}`);
    console.log('--- AVAILABLE MODELS ---');
    console.log(JSON.stringify(client.availableModels, null, 2));
    client.contin

  } catch (err) {
    console.error(`Failed to connect or retrieve config: ${err.message}`);
    process.exit(1);
  }

  let gitCommandResult = '';
  let gitCommand = '';
  if (inputCommand === 'git diff') {
    gitCommand = 'git diff';
  } else {
    const match = inputCommand.match(/^git show\s+(\S+)$/);
    if (match) {
      const commitHash = match[1];
      if (/^[a-zA-Z0-9~^_\-\.]+$/.test(commitHash)) {
        gitCommand = `git show ${commitHash}`;
      } else {
        console.error(`Error: Invalid commit hash/reference format: "${commitHash}"`);
        process.exit(1);
      }
    } else {
      console.error(`Error: Unsupported command. Must be "git diff" or "git show <commit-hash>".`);
      process.exit(1);
    }
  }

  console.log(`Executing: ${gitCommand}`);
  try {
    const { stdout, stderr } = await execAsync(gitCommand, {
      maxBuffer: 10 * 1024 * 1024
    });

    if (stderr && stderr.trim()) {
      console.warn(`Git Stderr: ${stderr}`);
    }

    gitCommandResult = stdout;
    console.log('--- GIT OUTPUT START ---');
    console.log(gitCommandResult);
    console.log('--- GIT OUTPUT END ---');

  } catch (error) {
    console.error(`Execution failed: ${error.message}`);
    process.exit(1);
  }

  // Chatsito session and chat call execution
  console.log('\n--- STARTING CHATSITO SESSION ---');
  try {
    const sessionManager = new ChatSessionManager();
    // Inject custom CLI url
    sessionManager.chatsitoApiClient.baseUrl = url;
    await sessionManager.initializeApiClient();

    // Select a standard free/local model if available to prevent subscription errors
    const preferedModels = ['qwen3.6:35b'];
    const selectedModel = preferedModels.find(m => sessionManager.availableModels.includes(m));
    if (selectedModel) {
      console.log(`Selecting model "${selectedModel}" for this session...`);
      sessionManager.activeModel = selectedModel;
    }

    sessionManager.startNewSession();
    console.log(`Sending diff to chatsito for review. ${gitCommandResult}`);

    await sessionManager.continueSession(`Please identify any and all issues that you see with the code changes in this diff. ${gitCommandResult}`, webviewClient);

    console.log('\n--- CONVERSATION HISTORY ---');
    for (const msg of sessionManager.conversationHistory) {
      console.log(`[${msg.role.toUpperCase()}] ${msg.content || '(no content)'}`);
    }
  } catch (err) {
    console.error(`Error running chat session: ${err.message}`);
    process.exit(1);
  }
}

main();
