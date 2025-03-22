import fitz  
from PIL import Image
import pytesseract
import io
import re
import psycopg2
from prettytable import PrettyTable  # Import PrettyTable for table formatting

# Provide the path to your Tesseract executable if it's not in your PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# PostgreSQL connection details
db_host = 'localhost'  # Replace with your database host
db_name = 'ocr'  # Replace with your database name
db_user = 'postgres'  # Replace with your database user
db_password = 'liki'  # Replace with your database password

# Establish the database connection
conn = psycopg2.connect(
    host=db_host,
    database=db_name,
    user=db_user,
    password=db_password
)
cursor = conn.cursor()

# Open the PDF
pdf_path = r'C:\Users\LIKHITHA\Downloads\Invoices (2).pdf'
pdf_document = fitz.open(pdf_path)

# Data to be inserted
data_to_insert = []

# Iterate over all pages in the PDF
for page_num in range(pdf_document.page_count):
    print(f"Processing page {page_num + 1}...")
    
    # Extract the page
    page = pdf_document.load_page(page_num)

    # Extract images from the page
    image_list = page.get_images(full=True)

    # Initialize variables to store extracted data
    ack_no = reference_no = bill_no = gstin = invoice_no = None
    special_check = None

    # Process each image (if available) on the page
    if image_list:
        for img_index, img in enumerate(image_list):
            xref = img[0]
            image_bytes = pdf_document.extract_image(xref)["image"]

            # Convert the image bytes to a PIL Image
            image = Image.open(io.BytesIO(image_bytes))

            # Perform OCR on the extracted image
            extracted_text = pytesseract.image_to_string(image)

            # Check for specific information based on the page number
            if page_num == 0:  # Page 1: Ack No
                ack_no = re.search(r'Ack No\.\s*:\s*(\d+)', extracted_text)
                if ack_no:
                    data_to_insert.append(('Ack No', ack_no.group(1)))
            elif page_num == 1:  # Page 2: Reference No
                reference_no = re.search(r'\bHE/NFC/LC/\d{3}/\d{2}-\d{2}\b', extracted_text)
                if reference_no:
                    data_to_insert.append(('Reference No', reference_no.group(0)))
            elif page_num == 2:  # Page 3: Bill No
                bill_no = re.search(r'BillNo\.\s*:\s*([A-Za-z0-9-]+)', extracted_text)
                if bill_no:
                    data_to_insert.append(('Bill No', bill_no.group(1)))
            elif page_num == 3:  # Page 4: GSTIN
                gstin = re.search(r'STIN\s*[:\s]*([A-Z0-9]{15})', extracted_text)
                if gstin:
                    data_to_insert.append(('GSTIN', gstin.group(1)))
            elif page_num == 4:  # Page 5: Acknowledgment No
                ack_no = re.search(r'Acknowledgement No\s*[:\s]*([0-9]+)', extracted_text)
                if ack_no:
                    data_to_insert.append(('Acknowledgement No', ack_no.group(1)))
            elif page_num == 5:  # Page 6: Special check for '552'
                special_check = '552' if '552' in extracted_text else None
                if special_check:
                    data_to_insert.append(('Special Check', '552'))
            elif page_num == 6:  # Page 7: Invoice No
                invoice_no = re.search(r'Invoice No\s*[:\s]*([A-Za-z0-9]+)', extracted_text)
                if invoice_no:
                    data_to_insert.append(('Invoice No', invoice_no.group(1)))

# Print data in a table format
table = PrettyTable()

# Define the column names
table.field_names = ["Data Type", "Data Value"]

# Add rows for each extracted data entry
for data_type, data_value in data_to_insert:
    table.add_row([data_type, data_value])

# Print the table in terminal
print("\nExtracted Data from PDF:")
print(table)

# Insert all data into the database
for data_type, data_value in data_to_insert:
    cursor.execute(
        "INSERT INTO extracted_invoice_data (data_type, data_value) VALUES (%s, %s)",
        (data_type, data_value)
    )

# Commit the transaction
conn.commit()

# Close the database connection
cursor.close()
conn.close()

print("Data insertion completed.")
