const fs = require('fs');
const https = require('https');
const path = require('path');
const os = require('os');

// 1. Extract API Key from MCP Config
function getNotionHeaders() {
    const configPath = path.join(os.homedir(), '.gemini', 'config', 'mcp_config.json');
    if (!fs.existsSync(configPath)) {
        throw new Error(`MCP config not found at ${configPath}`);
    }
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    const notionConfig = config.mcpServers?.['notion-mcp-server'];
    if (!notionConfig || !notionConfig.env || !notionConfig.env.OPENAPI_MCP_HEADERS) {
        throw new Error('Notion MCP headers not found in mcp_config.json');
    }
    return JSON.parse(notionConfig.env.OPENAPI_MCP_HEADERS);
}

// 2. Fix invalid URLs recursively
function fixLinks(obj) {
    if (Array.isArray(obj)) {
        for (let item of obj) fixLinks(item);
    } else if (typeof obj === 'object' && obj !== null) {
        if (obj.url && typeof obj.url === 'string') {
            if (!obj.url.startsWith('http://') && !obj.url.startsWith('https://')) {
                obj.url = 'https://local.file'; // Placeholder for invalid Notion links
            }
        }
        for (let key in obj) {
            fixLinks(obj[key]);
        }
    }
}

// 3. Push a single chunk to Notion
async function pushChunk(blockId, headers, children) {
    return new Promise((resolve, reject) => {
        const payload = JSON.stringify({ children });
        const options = {
            hostname: 'api.notion.com',
            path: `/v1/blocks/${blockId}/children`,
            method: 'PATCH',
            headers: {
                ...headers,
                'Content-Type': 'application/json'
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    resolve(JSON.parse(data));
                } else {
                    reject(new Error(`HTTP ${res.statusCode}: ${data}`));
                }
            });
        });

        req.on('error', reject);
        req.write(payload);
        req.end();
    });
}

// 4. Main process
async function main() {
    const args = process.argv.slice(2);
    if (args.length < 2) {
        console.error('Usage: node push_chunks.js <page_id> <chunks_directory>');
        process.exit(1);
    }
    
    const blockId = args[0];
    const dir = args[1];

    if (!fs.existsSync(dir)) {
        console.error(`Directory not found: ${dir}`);
        process.exit(1);
    }

    const headers = getNotionHeaders();
    
    const files = fs.readdirSync(dir)
        .filter(f => f.startsWith('chunk_') && f.endsWith('.json'))
        .sort((a, b) => {
            const numA = parseInt(a.match(/\d+/)?.[0] || '0', 10);
            const numB = parseInt(b.match(/\d+/)?.[0] || '0', 10);
            return numA - numB;
        });

    console.log(`Found ${files.length} chunks in ${dir}`);

    for (const file of files) {
        console.log(`Pushing ${file}...`);
        const filePath = path.join(dir, file);
        const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        
        // Split 100-block chunks into safer 25-block chunks to avoid size limits
        for (let i = 0; i < data.length; i += 25) {
            const slice = data.slice(i, i + 25);
            fixLinks(slice); // Fix invalid URLs inline
            
            try {
                await pushChunk(blockId, headers, slice);
            } catch (e) {
                console.error(`Failed on ${file} (slice ${i}): ${e.message}`);
                process.exit(1);
            }
            // Rate limit sleep
            await new Promise(r => setTimeout(r, 600));
        }
        
        console.log(`Success: ${file}`);
        // Clean up uploaded chunk
        fs.unlinkSync(filePath);
    }
    
    // Clean up directory
    try {
        fs.rmdirSync(dir);
        console.log(`Cleaned up directory: ${dir}`);
    } catch (e) {
        console.log(`Note: Could not remove directory ${dir} (might not be empty).`);
    }

    console.log("Done uploading all chunks.");
}

main().catch(console.error);
