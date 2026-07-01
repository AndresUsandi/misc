const getKnowledgeBase = require('./getKnowledgeBase');

async function searchDesignDocs(query) {
    if (!query || query.trim() === '') {
        return "Error: No query provided.";
    }

    try {
        const kb = getKnowledgeBase();
        const docs = kb.designDocs || [];
        const lowerQuery = query.toLowerCase();

        const matches = docs.filter(d => 
            d.id.toLowerCase().includes(lowerQuery) || 
            d.title.toLowerCase().includes(lowerQuery) ||
            d.content.toLowerCase().includes(lowerQuery)
        );

        if (matches.length === 0) {
            return `No design documents found matching: ${query}`;
        }

        let output = `=== Design Documents Search Results (${matches.length} matches) ===\n\n`;
        for (const d of matches) {
            output += `ID: ${d.id} | Title: ${d.title}\n`;
            output += `  Snippet: ${d.content.substring(0, 150)}...\n\n`;
        }

        return output.trim();
    } catch (error) {
        return `Error searching design documents: ${error.message}`;
    }
}

module.exports = searchDesignDocs;
