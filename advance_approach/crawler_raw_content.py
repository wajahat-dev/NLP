import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Headers to mimic a web browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def download_and_save_html(url, output_file, visited_urls, base_domain):
    try:
        # Check if the URL has already been visited
        if url in visited_urls:
            print(f"URL {url} already visited. Skipping.")
            return

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Save raw content to file
        with open(output_file, 'a', encoding='utf-8') as raw_file:
            raw_file.write(f"URL: {url}\n\n")
            raw_file.write(response.text + '\n\n\n')

        # Add the current URL to the set of visited URLs
        visited_urls.add(url)

        # Extract links from the HTML content and crawl them
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [link.get('href') for link in soup.find_all('a', href=True)]
        for link in links:
            subpage_url = urljoin(url, link)
            # Check if the subpage URL is within the base domain
            if urlparse(subpage_url).netloc == base_domain:
                download_and_save_html(subpage_url, output_file, visited_urls, base_domain)

    except requests.RequestException as e:
        print(f"Error downloading content from {url}: {e}")

def crawl_website(start_url, output_file):
    try:
        visited_urls = set()  # Set to keep track of visited URLs
        base_domain = urlparse(start_url).netloc
        # Download HTML content from the start URL and crawl subpages
        download_and_save_html(start_url, output_file, visited_urls, base_domain)
        print(f"HTML content from {start_url} and its subpages saved to {output_file}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python crawler.py <start_url>")
        sys.exit(1)

    start_url = sys.argv[1]
    output_file = "raw_content.txt"
    crawl_website(start_url, output_file)
