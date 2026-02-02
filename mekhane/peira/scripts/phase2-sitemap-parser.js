const fs = require('fs');
const path = require('path');

// Antigravity's read_url_content equivalent logic
// Since we cannot call tools from inside the script, we will assume the content 
// of sitemap.xml is available or we fetch it using standard node https if permitted.
// However, in Antigravity, we often use 'read_url_content' tool.
// But as I need to automate this for 254 chunks, I will use a simple fetch script.

const https = require('https');

const SITEMAP_URL = 'https://ai-data-base.com/post-sitemap.xml';
const OUTPUT_FILE = path.join('Raw', 'aidb', '_index', 'url_list.txt');
const OUTPUT_DIR = path.dirname(OUTPUT_FILE);

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

function fetchContent(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => resolve(data));
    }).on('error', (err) => reject(err));
  });
}

async function main() {
  console.log('Fetching sitemap...');
  try {
    const xmlContent = await fetchContent(SITEMAP_URL);
    
    // Extract URLs using Regex
    const urlRegex = /<loc><!\[CDATA\[(https:\/\/ai-data-base\.com\/archives\/\d+)\]\]><\/loc>/g;
    const urls = new Set();
    let match;

    while ((match = urlRegex.exec(xmlContent)) !== null) {
      urls.add(match[1]);
    }

    // Also try standard XML tags just in case CDATA is optional
    const simpleRegex = /<loc>(https:\/\/ai-data-base\.com\/archives\/\d+)<\/loc>/g;
    while ((match = simpleRegex.exec(xmlContent)) !== null) {
      urls.add(match[1]);
    }

    const urlList = Array.from(urls).sort((a, b) => {
      // Sort by ID descending (newest first)
      const idA = parseInt(a.split('/').pop());
      const idB = parseInt(b.split('/').pop());
      return idB - idA;
    });

    console.log(`Found ${urlList.length} unique article URLs.`);

    fs.writeFileSync(OUTPUT_FILE, urlList.join('\n'), 'utf8');
    console.log(`Saved to ${OUTPUT_FILE}`);

  } catch (error) {
    console.error('Error fetching sitemap:', error);
    process.exit(1);
  }
}

main();
