import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter

# Download NLTK stopwords and punkt resources
nltk.download('stopwords')
nltk.download('punkt')

# Function to check if a word consists only of English letters
def is_english_word(word):
    return all(ord(char) < 128 for char in word)

# Function to extract text from HTML and replace new lines with spaces
def extract_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=' ')
    # Replace new lines with spaces
    text = text.replace('\n', ' ')
    return text

# Function to get unique non-grammatical English words
def get_unique_words(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    filtered_words = [word for word in words if word.isalpha() and word not in stop_words and is_english_word(word)]
    return set(filtered_words)

# Function to save unique words to a file
def save_to_file(unique_words, filename):
    with open(filename, 'a', encoding='utf-8') as file:
        # Check for duplicates before writing
        existing_words = set()
        try:
            with open(filename, 'r', encoding='utf-8') as existing_file:
                existing_words = set(existing_file.read().split())
        except FileNotFoundError:
            pass

        unique_words = [word for word in unique_words if word not in existing_words]
        
        # Write unique words to the file
        file.write(' '.join(unique_words))
        print(f"{len(unique_words)} unique words saved to {filename}")

# Function to scrape a single blog
def scrape_blog(url):
    if not url:
        print("Error: Empty URL provided.")
        return []

    try:
        response = requests.get(url)
        response.raise_for_status()
        html = response.text
        text = extract_text(html)
        words = get_unique_words(text)
        return words
    except requests.RequestException as e:
        print(f"Error processing {url}: {e}")
        return []

# Main function to scrape blogs, extract, and process words
def scrape_blogs(output_filename, exclude_common=True):
    all_words = []

    # Read blog URLs from 'downloadable_urls.txt'
    try:
        with open('downloadable_urls.txt', 'r') as file:
            blog_urls = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print("Error: 'downloadable_urls.txt' not found.")
        return

    for url in blog_urls:
        words = scrape_blog(url)
        all_words.extend(words)

    # Count word occurrences and get only unique words
    word_counts = Counter(all_words)
    unique_words = [word for word, count in word_counts.items() if count == 1]

    # Optionally exclude common words
    if exclude_common:
        common_words = set(stopwords.words('english'))
        unique_words = [word for word in unique_words if word not in common_words]

    # Save unique words to a file
    save_to_file(unique_words, output_filename)


if __name__ == "__main__":
    # Output filename for unique words
    output_filename = "unique_words.txt"

    # Run the scraping tool
    scrape_blogs(output_filename, exclude_common=True)
