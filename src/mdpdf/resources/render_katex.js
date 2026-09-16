/**
 * High-performance batch LaTeX to KaTeX HTML renderer
 */
const fs = require('fs');
const path = require('path');

// Locate local KaTeX distribution bundled with mdpdf
const katexPath = path.join(__dirname, 'katex', 'katex.min.js');
let katex;
try {
    katex = require(katexPath);
} catch (e) {
    try {
        katex = require(path.join(__dirname, 'katex', 'katex.js'));
    } catch (err) {
        katex = require('katex');
    }
}

function processBatch(inputData) {
    if (!inputData || !inputData.trim()) {
        console.log(JSON.stringify([]));
        return;
    }

    let items;
    try {
        items = JSON.parse(inputData);
    } catch (e) {
        console.error('Failed to parse JSON input:', e.message);
        console.log(JSON.stringify([]));
        return;
    }

    const results = items.map(item => {
        try {
            const html = katex.renderToString(item.latex || '', {
                output: 'html',
                displayMode: Boolean(item.display),
                throwOnError: false,
                strict: false
            });
            return {
                id: item.id,
                html: html,
                success: true
            };
        } catch (err) {
            return {
                id: item.id,
                error: err.message,
                success: false
            };
        }
    });

    console.log(JSON.stringify(results));
}

async function main() {
    if (process.argv[2]) {
        const inputData = fs.readFileSync(process.argv[2], 'utf8');
        processBatch(inputData);
        return;
    }

    let chunks = [];
    process.stdin.setEncoding('utf8');

    process.stdin.on('data', chunk => {
        chunks.push(chunk);
    });

    process.stdin.on('end', () => {
        const inputData = chunks.join('');
        processBatch(inputData);
    });
}

main().catch(err => {
    console.error(err);
    process.exit(1);
});
