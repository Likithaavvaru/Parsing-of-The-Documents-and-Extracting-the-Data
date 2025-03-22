import pytesseract
from pdf2image import convert_from_path
import re

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\josep\Downloads\tesseract-ocr-w64-setup-5.5.0.20241111.exe'  # Update for your system


# Path to the PDF
pdf_path = r'C:\Users\josep\ocr-likitha\Invoices.pdf'

# Convert PDF pages to images
pages = convert_from_path(pdf_path)

# Extraction patterns for each page
extraction_rules = {
    0: r'ACK\s*No[:\s]*([\w-]+)',       # Page 1 - ACK No
    1: r'Invoice\s*Number[:\s]*([\w-]+)',  # Page 2 - Invoice Number
    2: r'Bill\s*Number[:\s]*([\w-]+)',  # Page 3 - Bill Number
    3: r'ACK\s*No[:\s]*([\w-]+)',       # Page 4 - ACK No
    4: r'\b255\b',                      # Page 5 - Number 255
    5: r'\b552\b',                      # Page 6 - Number 552
    6: r'Invoice\s*Number[:\s]*([\w-]+)'  # Page 7 - Invoice Number
}

results = {}

# Process each page
for i, page in enumerate(pages):
    text = pytesseract.image_to_string(page)
    pattern = extraction_rules.get(i)
    if pattern:
        match = re.search(pattern, text, re.IGNORECASE)
        results[f'Page {i+1}'] = match.group(1) if match else 'Not Found'

# Print results
for page, data in results.items():
    print(f'{page}: {data}')