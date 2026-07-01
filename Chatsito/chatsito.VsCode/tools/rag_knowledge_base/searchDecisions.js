const getKnowledgeBase = require('./getKnowledgeBase');

async function searchDecisions(query) {
    if (!query || query.trim() === '') {
        return "Error: No query provided.";
    }

    try {
        const kb = getKnowledgeBase();
        const decisions = kb.decisions || [];
        const lowerQuery = query.toLowerCase();

        const matches = decisions.filter(d => 
            d.id.toLowerCase().includes(lowerQuery) || 
            d.title.toLowerCase().includes(lowerQuery) ||
            d.content.toLowerCase().includes(lowerQuery)
        );

        if (matches.length === 0) {
            return `No architecture decisions found matching: ${query}`;
        }

        let output = `=== Architecture Decisions (ADR) Search Results (${matches.length} matches) ===\n\n`;
        for (const d of matches) {
            output += `ID: ${d.id} | Title: ${d.title}\n`;
            output += `  Content: ${d.content.substring(0, 200)}...\n\n`;
        }

        return output.trim();
    } catch (error) {
        return `Error searching architecture decisions: ${error.message}`;
    }
}

module.exports = searchDecisions;
