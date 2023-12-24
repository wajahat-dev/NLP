from bs4 import BeautifulSoup
import re
from itertools import islice

def extract_urdu_words_from_file(file_path, output_file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read the file in chunks of 1000 lines at a time
            chunk_size = 1000
            while True:
                chunk = list(islice(file, chunk_size))
                if not chunk:
                    break
                
                # Join the lines in the chunk and pass to BeautifulSoup
                soup = BeautifulSoup(''.join(chunk), 'html.parser')

                # Extract Urdu words using regular expression from the text within the HTML body
                body_text = soup.get_text()
                urdu_pattern = re.compile('[\u0600-\u06FF]+')
                matches = re.findall(urdu_pattern, body_text)
                
                # Add unique Urdu words to the set
                urdu_words = set(matches)

                # Write each word to the output file on a new line
                with open(output_file_path, 'a', encoding='utf-8') as output_file:
                    output_file.write('      '.join(urdu_words) + '\n')

        print(f"Unique Urdu words extracted from '{file_path}' and saved to '{output_file_path}'.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    input_file_path = 'raw_content.txt'  
    output_file_path = 'unique_urdu_words_list.txt'

    try:
        extract_urdu_words_from_file(input_file_path, output_file_path)
    except KeyboardInterrupt:
        print("Interrupted. Content saved up to this point.")
