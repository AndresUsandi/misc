import https from 'https';
import querystring from 'querystring';

async function webSearch(query) {
    if (!query) {
        return "Error: Query parameter is required.";
    }

    return new Promise((resolve) => {
        const postData = querystring.stringify({
            'q': query
        });

        const options = {
            hostname: 'lite.duckduckgo.com',
            port: 443,
            path: '/lite/',
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Length': Buffer.byteLength(postData),
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        };

        const req = https.request(options, (res) => {
            let data = '';

            res.on('data', (chunk) => {
                data += chunk;
            });

            res.on('end', () => {
                try {
                    const results = [];
                    const titleRegex = /<a rel="nofollow" href="([^"]+)" class='result-link'>([^<]+)<\/a>/g;
                    const snippetRegex = /<td class='result-snippet'>([\s\S]*?)<\/td>/g;
                    
                    const titles = [];
                    let match;
                    while ((match = titleRegex.exec(data)) !== null) {
                        titles.push({ url: match[1], title: match[2] });
                    }

                    const snippets = [];
                    while ((match = snippetRegex.exec(data)) !== null) {
                        snippets.push(match[1]);
                    }

                    const count = Math.min(3, Math.min(snippets.length, titles.length));
                    for (let i = 0; i < count; i++) {
                        const url = titles[i].url;
                        const title = titles[i].title.trim();
                        const snippet = snippets[i].replace(/<[^>]+>/g, '').trim();
                        results.push(`${i + 1}. ${title}\nURL: ${url}\nSnippet: ${snippet}`);
                    }

                    if (results.length === 0) {
                        const ahrefsRegex = /<a class="result-snippet"[^>]*href="([^"]+)"[^>]*>(.*?)<\/a>/gs;
                        let fallbackCount = 0;
                        while ((match = ahrefsRegex.exec(data)) !== null && fallbackCount < 3) {
                            const url = match[1];
                            const title = match[2].replace(/<[^>]+>/g, '').trim();
                            results.push(`${++fallbackCount}. ${title}\nURL: ${url}`);
                        }
                    }

                    if (results.length === 0) {
                        resolve("No results found or unable to parse search engine results.");
                    } else {
                        resolve(results.join('\n\n'));
                    }
                } catch (e) {
                    resolve(`Error parsing search results: ${e.message}`);
                }
            });
        });

        req.on('error', (e) => {
            resolve(`Error executing web search: ${e.message}`);
        });

        req.write(postData);
        req.end();
    });
}

export default webSearch;
