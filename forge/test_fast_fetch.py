import requests
import html2text
from bs4 import BeautifulSoup

url = "https://ai-data-base.com/archives/77445"

try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract Title
    title = soup.find('h1').get_text().strip() if soup.find('h1') else "No Title"
    
    # Extract Date
    date_el = soup.select_one('.p-article__date, .entry-date, .date')
    date = date_el.get_text().strip() if date_el else "0000.00.00"
    
    # Extract Content
    content_el = soup.select_one('.p-entry__content, .c-entry__content, article, .l-main')
    if content_el:
        # Remove unwanted elements
        for bad in content_el.select('script, style, .sharedaddy, .related-posts, nav'):
            bad.decompose()
        html_content = str(content_el)
    else:
        html_content = "No Content Found"
        
    # Convert to Markdown
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    markdown = h.handle(html_content)
    
    print(f"Title: {title}")
    print(f"Date: {date}")
    print(f"Markdown Length: {len(markdown)}")
    print("--- HEAD ---")
    print(markdown[:200])
    
except Exception as e:
    print(f"Error: {e}")
