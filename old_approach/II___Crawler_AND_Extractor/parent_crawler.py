import subprocess
import os

# Constants
CRAWLER_SCRIPT = "crawler.py"
MAX_CONCURRENT_CRAWLERS = 10
STATE_FILE = "crawler_state.txt"
START_URLS_FILE = "start_urls.txt"

def launch_crawler(url):
    try:
        subprocess.run(["start", "cmd", "/k", f"python {CRAWLER_SCRIPT} {url}"], check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error launching crawler for {url}: {e}")

def save_state(visited_urls):
    with open(STATE_FILE, "w") as state_file:
        state_file.write("\n".join(visited_urls))

def load_state():
    visited_urls = set()
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as state_file:
            visited_urls.update(line.strip() for line in state_file)
    return visited_urls

def main():
    visited_urls = load_state()

    # Read start URLs from the file
    try:
        with open(START_URLS_FILE, 'r') as file:
            start_urls = [line.strip() for line in file]
    except FileNotFoundError:
        print(f"Error: Start URLs file '{START_URLS_FILE}' not found.")
        return

    # Launch crawlers for each URL
    for url in start_urls:
        if url not in visited_urls:
            launch_crawler(url)
            visited_urls.add(url)
            if len(visited_urls) >= MAX_CONCURRENT_CRAWLERS:
                save_state(visited_urls)
                break

    # Save the final state
    save_state(visited_urls)

if __name__ == "__main__":
    main()
