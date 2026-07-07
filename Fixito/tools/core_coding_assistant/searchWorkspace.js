import vscode from '../../vscode.js';

async function searchWorkspace(query, fileGlob) {
    if (!query) return "Error: No query provided for search.";
    const results = [];
    const pattern = fileGlob || '**/*';
    
    try {
        let regex;
        try {
            regex = new RegExp(query, 'i');
        } catch (e) {
            regex = query;
        }

        const uris = await vscode.workspace.findFiles(pattern, '**/node_modules/**|**/.git/**|**/bin/**|**/obj/**|**/.vs/**');
        for (const uri of uris) {
            const document = await vscode.workspace.openTextDocument(uri);
            const text = document.getText();
            const lines = text.split(/\r?\n/);
            for (let i = 0; i < lines.length; i++) {
                const matched = (regex instanceof RegExp) ? regex.test(lines[i]) : lines[i].includes(query);
                if (matched) {
                    const relPath = vscode.workspace.asRelativePath(uri);
                    results.push({
                        file: relPath,
                        line: i + 1,
                        text: lines[i].trim()
                    });
                    if (results.length >= 100) {
                        break;
                    }
                }
            }
            if (results.length >= 100) {
                break;
            }
        }
    } catch (e) {
        return `Error during search: ${e.message}`;
    }

    if (results.length === 0) {
        return `No matches found for query: "${query}"`;
    }

    let output = `=== Search Results for: "${query}" ===\n\n`;
    for (const match of results) {
        output += `${match.file}:${match.line}: ${match.text}\n`;
    }
    if (results.length >= 100) {
        output += `\n(Truncated to first 100 matches)`;
    }
    return output;
}

export default searchWorkspace;
