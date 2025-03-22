import fitz  # PyMuPDF
import os
from PIL import Image

pdf_path = r'C:\Users\josep\ocr-likitha\Invoices.pdf'
output_folder = r'C:\Users\josep\ocr-likitha\uploaded_images'

# Create the folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

pdf = fitz.open(pdf_path)

for i, page in enumerate(pdf):
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # Define the image path
    image_path = os.path.join(output_folder, f'{i + 1}.png')
    
    # Save the image
    img.save(image_path)

print("PDF pages have been converted and saved as images.")
