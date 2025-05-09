import requests
import xml.etree.ElementTree as ET
from newsplease import NewsPlease # type: ignore
import json
import time
import random
from bs4 import BeautifulSoup
import logging
import os
import hashlib
from fake_useragent import UserAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("reuters_scraper.log"),
        logging.StreamHandler()
    ]
)

# Generate a random user agent for each request (not just session)
def get_random_user_agent():
    try:
        ua = UserAgent()
        return ua.random
    except:
        # Fallback user agents if fake_useragent fails
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        return random.choice(user_agents)

# Enhanced headers to better mimic a browser
def get_headers():
    random_user_agent = get_random_user_agent()
    return {
        'User-Agent': random_user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://www.google.com/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'DNT': '1',
    }

def fetch_with_retry(url, max_retries=3, session=None):
    """Fetch URL with retry logic and proper headers"""
    if session is None:
        session = requests.Session()
    
    headers = get_headers()
    for attempt in range(max_retries):
        try:
            # Add increasing delays between retries
            if attempt > 0:
                delay = 2 + attempt + random.random() * 3
                logging.info(f"Waiting {delay:.2f} seconds before retry...")
                time.sleep(delay)
            
            # Add random delay variation to appear more human-like
            if random.random() < 0.2:  # 20% chance of a slightly longer delay
                time.sleep(random.random() * 1.5)
                
            response = session.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                return response
            elif response.status_code == 403 or response.status_code == 401:
                logging.warning(f"Attempt {attempt+1}/{max_retries}: Access denied (status {response.status_code}) for {url}")
                # Longer delay for access denied errors
                time.sleep(5 + random.random() * 5)
            else:
                logging.warning(f"Attempt {attempt+1}/{max_retries}: Got status {response.status_code} for {url}")
        except Exception as e:
            logging.error(f"Attempt {attempt+1}/{max_retries}: Error fetching {url}: {e}")
    
    return None

def extract_article_fallback(url, session=None):
    """Extract article content using direct requests and BeautifulSoup when NewsPlease fails"""
    response = fetch_with_retry(url, max_retries=4, session=session)
    if not response:
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract title - multiple possible selectors based on Reuters HTML structure
    title_elem = (soup.select_one('h1.article-header__title') or 
                 soup.select_one('.article-header h1') or 
                 soup.select_one('h1.text__heading_level_1') or
                 soup.select_one('.title') or
                 soup.select_one('h1'))
    title = title_elem.get_text().strip() if title_elem else "Unknown Title"
    
    # Extract date - multiple possible selectors
    date_elem = (soup.select_one('time.article-header__date') or 
                soup.select_one('time') or
                soup.select_one('meta[property="article:published_time"]') or
                soup.select_one('.article-info__published-datetime'))
    
    date_publish = None
    if date_elem:
        if date_elem.get('datetime'):
            date_publish = date_elem.get('datetime')
        elif date_elem.get('content'):
            date_publish = date_elem.get('content')
    if not date_publish:
        date_publish = "Unknown Date"
    
    # Extract article text - multiple possible selectors
    article_paragraphs = (soup.select('.article-body__content p') or 
                         soup.select('.article-body p') or
                         soup.select('article p') or 
                         soup.select('.ArticleBody-article-body p') or
                         soup.select('.paywall-article p') or
                         soup.select('.articleBody p'))
    
    # Fallback to any paragraph if specific selectors fail
    if not article_paragraphs:
        article_paragraphs = soup.select('p')
    
    maintext = "\n".join([p.get_text().strip() for p in article_paragraphs if p.get_text().strip()])
    
    # Try to get author
    author_elem = (soup.select_one('.author-name') or 
                  soup.select_one('.byline') or
                  soup.select_one('[data-testid="author-byline"]'))
    author = author_elem.get_text().strip() if author_elem else "Unknown Author"
    
    return {
        "title": title,
        "date_publish": date_publish,
        "text": maintext,
        "url": url,
        "author": author
    }

def get_cache_filename(url):
    """Generate a cache filename based on URL hash to avoid long filenames"""
    # Create a hash of the URL
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return f"article_{url_hash}.json"

# Main function to organize the code better
def main():
    # Create a cache directory to avoid refetching already processed URLs
    cache_dir = "data/reuters_cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    # Create output directory
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Get sitemap index XML
    SITEMAP_INDEX_URL = "https://www.reuters.com/arc/outboundfeeds/sitemap-index/?outputType=xml"
    session = requests.Session()
    sitemap_index = fetch_with_retry(SITEMAP_INDEX_URL, session=session)
    if not sitemap_index:
        logging.error("Failed to fetch sitemap index")
        return
    
    root = ET.fromstring(sitemap_index.content)
    
    # Step 2: Parse sitemap URLs
    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    sitemap_urls = [elem.text for elem in root.findall('ns:sitemap/ns:loc', ns)]
    
    # Take a more selective approach - choose news sitemaps
    news_sitemaps = [url for url in sitemap_urls if 'news' in url.lower() or 'articles' in url.lower()]
    if not news_sitemaps:
        news_sitemaps = sitemap_urls[:2]  # Fallback
    
    logging.info(f"Found {len(sitemap_urls)} sitemap files. Selected {len(news_sitemaps)} news sitemaps.")
    
    # Step 3: Fetch selected sitemaps
    article_urls = []
    for sitemap_url in news_sitemaps:
        logging.info(f"Fetching sitemap: {sitemap_url}")
        sm_response = fetch_with_retry(sitemap_url, session=session)
        if not sm_response:
            logging.error(f"Failed to fetch sitemap: {sitemap_url}")
            continue
        
        sm_root = ET.fromstring(sm_response.content)
        urls = [elem.text for elem in sm_root.findall('ns:url/ns:loc', ns)]
        article_urls.extend(urls)
        
        # Add a delay between sitemap requests
        time.sleep(2 + random.random())
    
    logging.info(f"Extracted {len(article_urls)} article URLs.")
    
    # Step 4: Extract articles with more resilient approach
    articles = []
    num_articles = min(10, len(article_urls))  # Process up to 50 articles
    
    for i, url in enumerate(article_urls[:num_articles]):
        cache_file = os.path.join(cache_dir, get_cache_filename(url))
        
        # Check if we already have this article cached
        if os.path.exists(cache_file):
            logging.info(f"Loading cached article {i+1}/{num_articles}: {url}")
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    article_data = json.load(f)
                    articles.append(article_data)
                    continue
            except Exception as e:
                logging.warning(f"Failed to load cached article, will refetch: {e}")
        
        logging.info(f"Processing article {i+1}/{num_articles}: {url}")
        
        # Add longer, variable delay to avoid triggering rate limits
        delay = 3 + random.random() * 4
        logging.info(f"Waiting {delay:.2f} seconds before next request...")
        time.sleep(delay)
        
        # Try direct extraction method first (since it's working better)
        try:
            article_data = extract_article_fallback(url, session=session)
            if article_data and article_data["text"]:
                articles.append(article_data)
                logging.info(f"Successfully extracted with fallback method")
                
                # Cache the successful result
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(article_data, f, ensure_ascii=False)
                
                continue
        except Exception as e2:
            logging.error(f"Fallback extraction failed for {url}: {e2}")
        
        # Only try NewsPlease as a last resort (rarely needed now)
        try:
            article = NewsPlease.from_url(url)
            if article and article.maintext:
                article_data = {
                    "title": article.title,
                    "date_publish": str(article.date_publish),
                    "text": article.maintext,
                    "url": url,
                    "author": article.authors[0] if article.authors else "Unknown Author"
                }
                articles.append(article_data)
                logging.info(f"Successfully extracted with NewsPlease")
                
                # Cache the successful result
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(article_data, f, ensure_ascii=False)
            else:
                logging.warning(f"Both extraction methods failed for {url}")
        except Exception as e:
            logging.error(f"Error with NewsPlease for {url}: {e}")
            logging.warning(f"Both extraction methods failed for {url}")
    
    # Step 5: Save to JSON
    output_path = os.path.join(output_dir, "articles_from_sitemap.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    logging.info(f"✅ Saved {len(articles)} articles to {output_path}")

if __name__ == "__main__":
    main()