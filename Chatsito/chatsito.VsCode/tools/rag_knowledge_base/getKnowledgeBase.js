const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

function getKnowledgeBase() {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    const root = workspaceFolders && workspaceFolders.length > 0 ? workspaceFolders[0].uri.fsPath : null;
    let kbPath = null;
    if (root) {
        kbPath = path.resolve(root, '.chatsito', 'knowledge_base.json');
    }

    if (kbPath && fs.existsSync(kbPath)) {
        try {
            return JSON.parse(fs.readFileSync(kbPath, 'utf8'));
        } catch (e) {
            // fallback if parse fails
        }
    }

    // Default mock database if file is missing
    return {
        knowledgeItems: [
            {
                id: "KB-001",
                title: "Onboarding Guide",
                content: "Welcome to Chatsito! This is the developer onboarding guide. Build the project using `npm run build`, and run tests with `npm run test`.",
                tags: ["onboarding", "setup"]
            },
            {
                id: "KB-002",
                title: "RAG Knowledge Base Structure",
                content: "This toolset uses local mock databases stored under .chatsito/knowledge_base.json to simulate Confluence, Jira, and GitHub search features.",
                tags: ["architecture", "rag"]
            }
        ],
        tickets: [
            {
                id: "TASK-101",
                title: "Fix memory leak in extension host",
                description: "We are seeing high memory usage during long sessions, especially when calling hierarchy providers.",
                status: "In Progress",
                assignee: "Alice Smith",
                labels: ["bug", "performance"],
                comments: [
                    { author: "Bob", text: "I checked the heapsnapshots, it seems to be in the registered event listeners." }
                ],
                linkedItems: ["PR-201"]
            },
            {
                id: "TASK-102",
                title: "Implement RAG Knowledge Base tools",
                description: "Write stub implementation and tests for Confluence, Jira, and GitHub tools.",
                status: "Completed",
                assignee: "Antigravity Agent",
                labels: ["feature", "rag"],
                comments: [],
                linkedItems: []
            }
        ],
        pullRequests: [
            {
                id: "PR-201",
                title: "Fix memory leaks from registered event listeners",
                author: "Alice Smith",
                description: "This PR disposes event listeners correctly on extension deactivation.",
                status: "Open",
                changedFiles: ["extension.js", "utils.js"],
                reviews: [
                    { author: "Charlie", state: "Approved", text: "Looks solid, tests pass." }
                ],
                statusChecks: "Passed"
            }
        ],
        designDocs: [
            {
                id: "ARCH-001",
                title: "Extension Command Architecture",
                content: "This document outlines the command registration patterns used in chatsito. All command registrations are pushed to subscriptions."
            }
        ],
        decisions: [
            {
                id: "ADR-001",
                title: "Use Local JSON Mocks for RAG Tools",
                content: "Context: VS Code does not provide native RAG/Jira/GitHub APIs. Decision: We use local JSON files in .chatsito/ to mock external knowledge bases for offline development and local LLM agents."
            }
        ]
    };
}

module.exports = getKnowledgeBase;
