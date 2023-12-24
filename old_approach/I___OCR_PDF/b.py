import requests
from bs4 import BeautifulSoup
from PIL import Image
from urllib.parse import urljoin  # Add this import statement
from pytesseract import pytesseract
from langid.langid import LanguageIdentifier, model

def extract_text_from_image(image_url):
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        # Save the image locally
        with open('temp_image.png', 'wb') as file:
            file.write(response.content)

        # Use Tesseract OCR to extract text from the image
        extracted_text = pytesseract.image_to_string(Image.open('temp_image.png'), lang='eng+urd')
        return extracted_text

    else:
        print(f"Failed to retrieve image. Status code: {response.status_code}")
        return None

def scrape_urdu_words(url, max_words=5000000):
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        images = soup.find_all('img', src=True)

        identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)

        urdu_words = []
        word_count = 0

        for image in images:
            image_url = urljoin(url, image['src'])
            extracted_text = extract_text_from_image(image_url)

            if extracted_text:
                # Check if the text is in Urdu
                language, confidence = identifier.classify(extracted_text)
                if language == 'urdu' and confidence > 0.5:
                    words = extracted_text.split()
                    urdu_words.extend(words)
                    word_count += len(words)

                    if word_count >= max_words:
                        break

        return urdu_words

    else:
        print(f"Failed to retrieve content. Status code: {response.status_code}")
        return []
if __name__ == "__main__":
    target_url = "https://ur.wikipedia.org/wiki/صفحہ_اول"
    extracted_words = scrape_urdu_words(target_url, max_words=5000000)

    print(f"Total Urdu Words Extracted: {len(extracted_words)}")