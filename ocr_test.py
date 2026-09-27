"""
OCR agent - extracts raw text from an invoice/document image.

Applies preprocessing (grayscale, upscaling, contrast enhancement,
sharpening) before OCR by default. This makes a real difference on
lower-resolution or web-sourced images (e.g. an image pulled from
Google during a live demo/exam) without hurting already-clean, high-
resolution images - tested against both.

Usage:
    python ocr_test.py sample_docs/invoice1.jpg
    python ocr_test.py sample_docs/invoice1.jpg --raw   (skip preprocessing, for comparison)
"""
import sys
import pytesseract
from PIL import Image, ImageOps, ImageFilter

# If Tesseract isn't on your PATH, uncomment and set the path below:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

UPSCALE_FACTOR = 3


def preprocess_image(img: Image.Image) -> Image.Image:
    """Grayscale + upscale + autocontrast + sharpen - helps OCR read
    smaller or lower-quality text without needing per-image tuning."""
    processed = img.convert("L")  # grayscale
    processed = processed.resize(
        (processed.width * UPSCALE_FACTOR, processed.height * UPSCALE_FACTOR),
        Image.LANCZOS,
    )
    processed = ImageOps.autocontrast(processed)
    processed = processed.filter(ImageFilter.SHARPEN)
    return processed


def extract_text(image_path: str, raw: bool = False) -> str:
    img = Image.open(image_path)
    if not raw:
        img = preprocess_image(img)
    return pytesseract.image_to_string(img)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ocr_test.py <path_to_image> [--raw]")
        sys.exit(1)

    path = sys.argv[1]
    raw = "--raw" in sys.argv
    result = extract_text(path, raw=raw)
    print(f"----- RAW OCR OUTPUT ({'no preprocessing' if raw else 'preprocessed'}) -----")
    print(result)
    print("---------------------------")