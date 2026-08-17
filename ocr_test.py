"""
Standalone OCR test - run this by itself first, before connecting it to
anything else in the pipeline. The goal here is just to confirm Tesseract
is installed correctly and see how clean the extracted text is.

Usage:
    python ocr_test.py sample_docs/invoice1.jpg
"""
import sys
import pytesseract
from PIL import Image

# If Tesseract isn't on your PATH, uncomment and set the path below:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text(image_path: str) -> str:
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ocr_test.py <path_to_image>")
        sys.exit(1)

    path = sys.argv[1]
    result = extract_text(path)
    print("----- RAW OCR OUTPUT -----")
    print(result)
    print("---------------------------")