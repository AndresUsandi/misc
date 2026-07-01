const getKnowledgeBase = require('./getKnowledgeBase');

async function searchKnowledge(query) {
    if (!query || query.trim() === '') {
        return "Error: No query provided.";
    }

    try {
        const kb = getKnowledgeBase();
        const items = kb.knowledgeItems || [];
        const lowerQuery = query.toLowerCase();

        const matches = items.filter(item => 
            item.title.toLowerCase().includes(lowerQuery) || 
            item.content.toLowerCase().includes(lowerQuery) ||
            (item.tags && item.tags.some(tag => tag.toLowerCase().includes(lowerQuery)))
        );

        if (matches.length === 0) {
            return `No knowledge items found matching: ${query}`;
        }

        let output = `=== Knowledge Base Search Results (${matches.length} matches) ===\n\n`;
        for (const item of matches) {
            output += `ID: ${item.id} | Title: ${item.title}\n`;
            if (item.tags && item.tags.length > 0) {
                output += `  Tags: ${item.tags.join(', ')}\n`;
            }
            output += `  Snippet: ${item.content.substring(0, 150)}...\n\n`;
        }

        return output.trim();
    } catch (error) {
        return `Error searching knowledge base: ${error.message}`;
    }
}

module.exports = searchKnowledge;
