import requests
import html2text
from bs4 import BeautifulSoup
import json
import datetime

url = "https://ai-data-base.com/archives/77445"

def parse_date(date_str):
    # Try different formats
    formats = ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y.%m.%d"]
    for fmt in formats:
        try:
            return datetime.datetime.strptime(date_str, fmt).strftime("%Y.%m.%d")
        except:
            continue
    return date_str

try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8' # Force UTF-8
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract Metadata via Meta Tags (More reliable)
    meta = {}
    
    # Title
    og_title = soup.find('meta', property='og:title')
    title = og_title['content'] if og_title else (soup.find('h1').get_text().strip() if soup.find('h1') else "No Title")
    
    # Date
    pub_time = soup.find('meta', property='article:published_time')
    date_str = pub_time['content'] if pub_time else ""
    if not date_str:
         # Fallback to selectors
        date_el = soup.select_one('.p-article__date, .entry-date, .date')
        date_str = date_el.get_text().strip() if date_el else "0000.00.00"
    
    formatted_date = parse_date(date_str)

    # Tags
    tags = []
    # Try meta tags? Often tags are not in meta.
    # Try common tag selectors
    tag_els = soup.select('a[href*="/archives/type-tag/"], a[href*="/archives/tech-tag/"], a[href*="/archives/app-tag/"], .post_tag a')
    tags = list(set([t.get_text().strip() for t in tag_els]))
    
    # Content
    content_el = soup.select_one('.p-entry__content, .c-entry__content, article, .l-main')
    html_content = ""
    if content_el:
        # Remove unwanted, but keep headers
        for bad in content_el.select('script, style, .sharedaddy, .related-posts, nav, .wpp-list'):
            bad.decompose()
        html_content = str(content_el)
    
    # Convert
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.body_width = 0 # No wrapping
    markdown = h.handle(html_content)
    
    result = {
        "title": title,
        "date": formatted_date,
        "tags": tags,
        "length": len(markdown),
        "markdown_snippet": markdown[:500]
    }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Save to verify encoding
    with open("test_output.md", "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n{markdown}")

except Exception as e:
    print(f"Error: {e}")
