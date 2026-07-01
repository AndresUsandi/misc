const axios = require('axios');

async function executeHttpRequest(url, method = 'GET', body = null) {
    try {
        method = method.toUpperCase();
        const config = {
            method: method,
            url: url,
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        };

        if (method === 'POST' && body) {
            config.data = body;
        }

        const response = await axios(config);
        
        // Return raw data as string (if it's an object, JSON stringify it)
        if (typeof response.data === 'object') {
            return JSON.stringify(response.data, null, 2);
        }
        return String(response.data);
        
    } catch (error) {
        let errorMsg = `Error executing HTTP request: ${error.message}`;
        if (error.response) {
            errorMsg = `HTTP Error: ${error.response.status} ${error.response.statusText}\n`;
            if (typeof error.response.data === 'object') {
                errorMsg += JSON.stringify(error.response.data, null, 2);
            } else {
                errorMsg += String(error.response.data);
            }
        }
        return errorMsg;
    }
}

module.exports = executeHttpRequest;
