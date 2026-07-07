async function executeHttpRequest(url, method = 'GET', body = null) {
    try {
        method = method.toUpperCase();
        const options = {
            method: method,
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        };

        if (method === 'POST' && body) {
            options.body = body;
            try {
                JSON.parse(body);
                options.headers['Content-Type'] = 'application/json';
            } catch (e) {
                options.headers['Content-Type'] = 'text/plain';
            }
        }

        const response = await fetch(url, options);
        const text = await response.text();
        
        if (!response.ok) {
            return `HTTP Error: ${response.status} ${response.statusText}\n${text}`;
        }
        
        return text;
        
    } catch (error) {
        return `Error executing HTTP request: ${error.message}`;
    }
}

export default executeHttpRequest;
