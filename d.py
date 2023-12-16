import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import threading
import pickle


# Headers to mimic a web browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_links(url, base_domain):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]
        
        # Filter links to include only those within the specified base domain
        links = [link for link in links if urlparse(link).netloc == base_domain]
        
        return links
    except requests.RequestException as e:
        print(f"Error getting links from {url}: {e}")
        return []

def is_downloadable(url):
    try:
        response = requests.head(url, headers=headers)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Error checking download status for {url}: {e}")
        return False



def crawl_and_save_wrapper(url, visited_urls, download_urls, base_domain, output_file, thread_states):
    try:
        crawl_and_save(url, visited_urls, download_urls, base_domain, output_file, thread_states)
    except Exception as e:
        print(f"Error crawling {url}: {e}")

def crawl_and_save(url, visited_urls, download_urls, base_domain, output_file, thread_states):
    visited_urls.add(url)
    print(f"Crawling: {url}")

    links = get_links(url, base_domain)
    for link in links:
        if link not in visited_urls:
            download_urls.add(link)

    if is_downloadable(url):
        with open(output_file, 'r') as file:
            if url not in file.read():
                with open(output_file, 'a') as append_file:
                    append_file.write(url + '\n')

    thread_states[url].set()  # Mark thread as completed

def crawl_website(start_urls_file, output_file):
    visited_urls = set()

    # Load existing URLs from the output file
    try:
        with open(output_file, 'r') as file:
            visited_urls.update(line.strip() for line in file)
    except FileNotFoundError:
        pass

    # Read start_urls and base_domain from a file
    try:
        with open(start_urls_file, 'r') as file:
            start_urls = [line.strip() for line in file if not line.startswith('#')]
            if start_urls:
                base_domain = urlparse(start_urls[0]).netloc  # Assuming the first URL determines the base domain
            else:
                print(f"Error: Start URLs file '{start_urls_file}' is empty.")
                return
    except FileNotFoundError:
        print(f"Error: Start URLs file '{start_urls_file}' not found.")
        return


    download_urls = set(start_urls)

    thread_states = {}
    for url in download_urls:
        thread_states[url] = threading.Event()

    threads = []
    for url in download_urls:
        thread = threading.Thread(
            target=crawl_and_save_wrapper,
            args=(url, visited_urls, download_urls, base_domain, output_file, thread_states)
        )
        threads.append(thread)

    for thread in threads:
        thread.start()

    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("Script interrupted. Saving thread states...")
        for url, event in thread_states.items():
            thread_states[url] = event.is_set()
        save_thread_states(thread_states)
        print("Thread states saved. Exiting.")

    print("Crawling and saving completed.")

    visited_urls = set()

    # Load existing URLs from the output file
    try:
        with open(output_file, 'r') as file:
            visited_urls.update(line.strip() for line in file)
    except FileNotFoundError:
        pass

    # Read start_urls and base_domain from a file
    try:
        with open(start_urls_file, 'r') as file:
            start_urls = [line.strip() for line in file]
            if start_urls:
                base_domain = urlparse(start_urls[0]).netloc  # Assuming the first URL determines the base domain
            else:
                print(f"Error: Start URLs file '{start_urls_file}' is empty.")
                return
    except FileNotFoundError:
        print(f"Error: Start URLs file '{start_urls_file}' not found.")
        return

    download_urls = set(start_urls)

    while download_urls:
        current_url = download_urls.pop()

        visited_urls.add(current_url)
        print(f"Crawling: {current_url}")

        links = get_links(current_url, base_domain)
        for link in links:
            # Check if sub-page is visited before adding to download_urls
            if link not in visited_urls:
                download_urls.add(link)

        if is_downloadable(current_url):
            # Check if URL is already in the file before adding
            with open(output_file, 'r') as file:
                if current_url not in file.read():
                    with open(output_file, 'a') as append_file:
                        append_file.write(current_url + '\n')

def save_thread_states(thread_states):
    with open("thread_states_crawler.pkl", 'wb') as file:
        pickle.dump(thread_states, file)

if __name__ == "__main__":
    start_urls_file = "start_urls.txt"
    output_file = "downloadable_urls.txt"
    crawl_website(start_urls_file, output_file)
    print(f"Downloadable URLs stored in: {output_file}")
