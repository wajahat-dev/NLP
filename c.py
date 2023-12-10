import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from urllib.parse import urlparse

# Download NLTK resources
nltk.download('punkt', quiet=True)

# Function to check if a word consists only of Urdu letters
def is_urdu_word(word):
    return any(0x600 <= ord(char) <= 0x6FF for char in word)

# Function to extract text from HTML and replace new lines with spaces
def extract_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=' ')
    # Replace new lines with spaces
    text = text.replace('\n', ' ')
    return text

# Function to get unique non-grammatical Urdu words
def get_unique_urdu_words(text):
    words = word_tokenize(text)
    filtered_words = [word for word in words if word.isalpha() and is_urdu_word(word)]
    return set(filtered_words)

# Function to save unique Urdu words to a file
def save_urdu_to_file(unique_urdu_words, filename):
    with open(filename, 'a', encoding='utf-8') as file:
        existing_words = set()
        try:
            with open(filename, 'r', encoding='utf-8') as existing_file:
                existing_words = set(existing_file.read().split())
        except FileNotFoundError:
            pass

        unique_urdu_words = [word for word in unique_urdu_words if word not in existing_words]

        # Write each unique Urdu word on a new line
        for word in unique_urdu_words:
            file.write(word + '\n')

        print(f"{len(unique_urdu_words)} unique Urdu words saved to {filename}")

# Function to save crawled URLs to a file
def save_crawled_url(url, filename):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(url + '\n')

# Function to check if a URL has been crawled
def is_url_crawled(url, filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            crawled_urls = set(line.strip() for line in file if line.strip())
        return url in crawled_urls
    except FileNotFoundError:
        return False

# Function to scrape a single blog and extract unique Urdu words directly
def scrape_blog_and_save(url, output_filename, crawled_urls_file, exclude_common=True):
    if not url:
        print("Error: Empty URL provided.")
        return

    if is_url_crawled(url, crawled_urls_file):
        print(f"URL already crawled: {url}")
        return

    try:
        response = requests.get(url)
        response.raise_for_status()
        html = response.text
        text = extract_text(html)
        urdu_words = get_unique_urdu_words(text)

        save_urdu_to_file(urdu_words, output_filename)
        save_crawled_url(url, crawled_urls_file)

        print(f"{len(urdu_words)} unique Urdu words extracted and saved from {url}")
    except requests.RequestException as e:
        print(f"Error processing {url}: {e}")

if __name__ == "__main__":
    output_filename = "unique_urdu_words.txt"
    crawled_urls_file = "crawled_urls.txt"
    downloadable_urls_file = "downloadable_urls.txt"

    try:
        with open(downloadable_urls_file, 'r') as file:
            blog_urls = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: {downloadable_urls_file} not found.")
        blog_urls = []

    print("Running the Urdu scraping tool...")
    for url in blog_urls:
        scrape_blog_and_save(url, output_filename, crawled_urls_file, exclude_common=True)

    print("Urdu scraping completed.")
