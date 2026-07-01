const getKnowledgeBase = require('./getKnowledgeBase');

async function readPullRequest(prId) {
    if (!prId || prId.trim() === '') {
        return "Error: No PR ID provided.";
    }

    try {
        const kb = getKnowledgeBase();
        const pr = (kb.pullRequests || []).find(x => x.id === prId);

        if (!pr) {
            return `Error: Pull request not found with ID: ${prId}`;
        }

        let output = `=== Pull Request: ${pr.title} (${pr.id}) ===\n\n`;
        output += `Author: ${pr.author}\n`;
        output += `Status: ${pr.status}\n`;
        output += `Status Checks: ${pr.statusChecks || 'N/A'}\n`;
        if (pr.changedFiles && pr.changedFiles.length > 0) {
            output += `Changed Files: ${pr.changedFiles.join(', ')}\n`;
        }
        output += `\nDescription:\n${pr.description}\n`;

        if (pr.reviews && pr.reviews.length > 0) {
            output += `\nReviews:\n`;
            for (const r of pr.reviews) {
                output += `- [${r.author}]: ${r.state}${r.text ? ' - ' + r.text : ''}\n`;
            }
        }

        return output.trim();
    } catch (error) {
        return `Error reading pull request: ${error.message}`;
    }
}

module.exports = readPullRequest;
