const getKnowledgeBase = require('./getKnowledgeBase');

async function searchPullRequests(query) {
    if (!query || query.trim() === '') {
        return "Error: No query provided.";
    }

    try {
        const kb = getKnowledgeBase();
        const prs = kb.pullRequests || [];
        const lowerQuery = query.toLowerCase();

        const matches = prs.filter(pr => 
            pr.id.toLowerCase().includes(lowerQuery) || 
            pr.title.toLowerCase().includes(lowerQuery) ||
            pr.author.toLowerCase().includes(lowerQuery) ||
            pr.description.toLowerCase().includes(lowerQuery) ||
            (pr.changedFiles && pr.changedFiles.some(f => f.toLowerCase().includes(lowerQuery)))
        );

        if (matches.length === 0) {
            return `No pull requests found matching: ${query}`;
        }

        let output = `=== Pull Request Search Results (${matches.length} matches) ===\n\n`;
        for (const pr of matches) {
            output += `ID: ${pr.id} | Title: ${pr.title}\n`;
            output += `  Author: ${pr.author} | Status: ${pr.status}\n`;
            if (pr.changedFiles && pr.changedFiles.length > 0) {
                output += `  Changed Files: ${pr.changedFiles.join(', ')}\n`;
            }
            output += `  Summary: ${pr.description.substring(0, 100)}...\n\n`;
        }

        return output.trim();
    } catch (error) {
        return `Error searching pull requests: ${error.message}`;
    }
}

module.exports = searchPullRequests;
