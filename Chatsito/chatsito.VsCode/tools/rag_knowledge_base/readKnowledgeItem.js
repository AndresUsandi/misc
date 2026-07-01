const getKnowledgeBase = require('./getKnowledgeBase');

async function readKnowledgeItem(itemId) {
    if (!itemId || itemId.trim() === '') {
        return "Error: No item ID provided.";
    }

    try {
        const kb = getKnowledgeBase();
        
        let item = (kb.knowledgeItems || []).find(x => x.id === itemId);
        let category = 'Knowledge Item';
        
        if (!item) {
            item = (kb.designDocs || []).find(x => x.id === itemId);
            category = 'Design Document';
        }
        if (!item) {
            item = (kb.decisions || []).find(x => x.id === itemId);
            category = 'Architecture Decision Record';
        }

        if (!item) {
            return `Error: Knowledge item not found with ID: ${itemId}`;
        }

        let output = `=== ${category}: ${item.title} (${item.id}) ===\n\n`;
        if (item.tags && item.tags.length > 0) {
            output += `Tags: ${item.tags.join(', ')}\n\n`;
        }
        output += `${item.content}`;

        return output.trim();
    } catch (error) {
        return `Error reading knowledge item: ${error.message}`;
    }
}

module.exports = readKnowledgeItem;
