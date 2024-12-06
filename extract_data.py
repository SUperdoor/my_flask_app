from PIL import Image  # Import PIL to handle image files
from pytesseract import image_to_string
import pytesseract
import re
from typing import Dict, List

# Configure pytesseract to point to the Tesseract executable
# Update this path to match your Tesseract installation directory
# Example for Windows:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# For Linux/macOS, if Tesseract is installed via package manager:
# pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'


def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from a JPG image using OCR.

    Args:
        image_path (str): Path to the JPG image file.

    Returns:
        str: Text extracted from the image.
    """
    full_text = ""
    try:
        # Open the image file
        image = Image.open(image_path)
        print(f"Performing OCR on image: {image_path}...")
        full_text = image_to_string(image)
        print(f"Extracted text:\n{full_text}\n{'-' * 40}")  # Log extracted text
    except Exception as e:
        print(f"Error extracting text from image: {e}")
    return full_text


def extract_invoice_data(image_path: str) -> Dict:
    """
    Extract structured invoice data from a JPG image using OCR.

    Args:
        image_path (str): Path to the JPG image file.

    Returns:
        dict: Extracted data including vendor, items, and totals.
    """
    data = {"vendor": "", "items": [], "subtotal": 0.0, "total": 0.0}

    # Step 1: Extract text from image using OCR
    full_text = extract_text_from_image(image_path)

    # Debugging: Print full text extracted from the image
    print("Full Text Extracted:")
    print(full_text)
    print("-" * 40)

    # Step 2: Parse the text to extract structured data
    # Extract vendor information
    vendor_match = re.search(r"Vendor:\s*(.+)", full_text)
    if vendor_match:
        data["vendor"] = vendor_match.group(1).strip()

    # Extract items (quantity, item description, amount)
    # Adjust regex based on the structure of your invoice
    item_pattern = r"(\d+)\s+(.+?)\s+AUD\s([\d\.]+)"
    items_matches = re.findall(item_pattern, full_text)
    for match in items_matches:
        if len(match) == 3:
            data["items"].append({
                "quantity": int(match[0]),
                "item": match[1].strip(),
                "amount": float(match[2])
            })

    # Extract subtotal
    subtotal_match = re.search(r"Subtotal AUD\s*([\d\.]+)", full_text)
    if subtotal_match:
        data["subtotal"] = float(subtotal_match.group(1))

    # Extract total
    total_match = re.search(r"Total AUD\s*([\d\.]+)", full_text)
    if total_match:
        data["total"] = float(total_match.group(1))

    return data
