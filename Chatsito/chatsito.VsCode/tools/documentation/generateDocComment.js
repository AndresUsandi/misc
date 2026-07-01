async function generateDocComment(signature) {
    if (!signature) return "Error: Missing signature parameter.";

    try {
        const sig = String(signature).trim();
        let comment = '';

        // Very basic parsing for parameter names inside parentheses
        const paramsMatch = sig.match(/\((.*?)\)/);
        let params = [];
        if (paramsMatch && paramsMatch[1]) {
            // Split by comma, then get the last word (usually the param name in C# or just the name in JS)
            const paramParts = paramsMatch[1].split(',');
            params = paramParts.map(p => {
                const tokens = p.trim().split(/\s+/);
                return tokens[tokens.length - 1].replace(/[^a-zA-Z0-9_]/g, '');
            }).filter(p => p.length > 0);
        }

        // Detect if it looks like C# or Java (public, private, int, etc before the name)
        const isCSharp = sig.includes('public ') || sig.includes('private ') || sig.includes('protected ');

        if (isCSharp) {
            comment += '/// <summary>\n';
            comment += '/// Description for the function.\n';
            comment += '/// </summary>\n';
            params.forEach(p => {
                comment += `/// <param name="${p}">Description for ${p}.</param>\n`;
            });
            if (sig.includes(' ') && !sig.startsWith('void ') && !sig.includes(' void ')) {
                comment += '/// <returns>Description of the return value.</returns>\n';
            }
        } else {
            // JSDoc style for JS/TS
            comment += '/**\n';
            comment += ' * Description for the function.\n';
            params.forEach(p => {
                comment += ` * @param {any} ${p} - Description for ${p}.\n`;
            });
            comment += ' * @returns {any} Description of the return value.\n';
            comment += ' */\n';
        }

        return `=== Generated Doc Comment ===\n\n${comment}\nSignature: ${sig}`;

    } catch (e) {
        return `Error generating doc comment: ${e.message}`;
    }
}

module.exports = generateDocComment;
