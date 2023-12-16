import fitz  # PyMuPDF
from nltk.tokenize import word_tokenize
import re

# Function to check if a word consists only of Urdu letters
def is_urdu_word(word):
    return any(0x600 <= ord(char) <= 0x6FF for char in word)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text += page.get_text()
    return text


# Function to get unique non-grammatical Urdu words
def get_unique_urdu_words(text):
    # Remove non-alphabetic characters and tokenize
    words = word_tokenize(re.sub(r'[^A-Za-z؀-ۿ]', ' ', text))
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

if __name__ == "__main__":
    pdf_path = "./2.pdf"
    output_filename = "unique_urdu_words_from_pdf.txt"

    pdf_text = extract_text_from_pdf(pdf_path)
    urdu_words = get_unique_urdu_words(pdf_text)
    save_urdu_to_file(urdu_words, output_filename)

    print("Extraction and processing completed.")
