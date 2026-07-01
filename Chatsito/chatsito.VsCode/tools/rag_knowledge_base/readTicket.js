const getKnowledgeBase = require('./getKnowledgeBase');

async function readTicket(ticketId) {
    if (!ticketId || ticketId.trim() === '') {
        return "Error: No ticket ID provided.";
    }

    try {
        const kb = getKnowledgeBase();
        const ticket = (kb.tickets || []).find(t => t.id === ticketId);

        if (!ticket) {
            return `Error: Ticket not found with ID: ${ticketId}`;
        }

        let output = `=== Ticket: ${ticket.title} (${ticket.id}) ===\n\n`;
        output += `Status: ${ticket.status}\n`;
        output += `Assignee: ${ticket.assignee || 'Unassigned'}\n`;
        if (ticket.labels && ticket.labels.length > 0) {
            output += `Labels: ${ticket.labels.join(', ')}\n`;
        }
        if (ticket.linkedItems && ticket.linkedItems.length > 0) {
            output += `Linked Items: ${ticket.linkedItems.join(', ')}\n`;
        }
        output += `\nDescription:\n${ticket.description}\n`;

        if (ticket.comments && ticket.comments.length > 0) {
            output += `\nComments:\n`;
            for (const c of ticket.comments) {
                output += `- [${c.author}]: ${c.text}\n`;
            }
        }

        return output.trim();
    } catch (error) {
        return `Error reading ticket: ${error.message}`;
    }
}

module.exports = readTicket;
