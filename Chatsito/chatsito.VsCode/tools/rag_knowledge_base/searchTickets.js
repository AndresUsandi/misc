const getKnowledgeBase = require('./getKnowledgeBase');

async function searchTickets(query) {
    if (!query || query.trim() === '') {
        return "Error: No query provided.";
    }

    try {
        const kb = getKnowledgeBase();
        const tickets = kb.tickets || [];
        const lowerQuery = query.toLowerCase();

        const matches = tickets.filter(t => 
            t.id.toLowerCase().includes(lowerQuery) || 
            t.title.toLowerCase().includes(lowerQuery) ||
            t.description.toLowerCase().includes(lowerQuery) ||
            (t.labels && t.labels.some(lbl => lbl.toLowerCase().includes(lowerQuery))) ||
            (t.assignee && t.assignee.toLowerCase().includes(lowerQuery))
        );

        if (matches.length === 0) {
            return `No tickets found matching: ${query}`;
        }

        let output = `=== Ticket Search Results (${matches.length} matches) ===\n\n`;
        for (const t of matches) {
            output += `ID: ${t.id} | Title: ${t.title}\n`;
            output += `  Status: ${t.status} | Assignee: ${t.assignee || 'Unassigned'}\n`;
            if (t.labels && t.labels.length > 0) {
                output += `  Labels: ${t.labels.join(', ')}\n`;
            }
            output += `  Summary: ${t.description.substring(0, 100)}...\n\n`;
        }

        return output.trim();
    } catch (error) {
        return `Error searching tickets: ${error.message}`;
    }
}

module.exports = searchTickets;
