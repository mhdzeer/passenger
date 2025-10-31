import frappe
import pytesseract
from PIL import Image
import io
import re
import base64

def extract_data_from_cpr(doc, method):
    if not doc.cpr_image:
        return

    try:
        # Get image file
        file_doc = frappe.get_doc("File", {"file_url": doc.cpr_image})
        image_data = base64.b64decode(file_doc.get_content())
        image = Image.open(io.BytesIO(image_data))

        text = pytesseract.image_to_string(image)

        # Try to extract fields using regex patterns
        name_match = re.search(r"Name[:\s]+([A-Za-z ]+)", text)
        cpr_match = re.search(r"\b[0-9]{9}\b", text)
        dob_match = re.search(r"(\d{2}/\d{2}/\d{4})", text)
        nationality_match = re.search(r"Nationality[:\s]+([A-Za-z ]+)", text)

        if name_match:
            doc.full_name = name_match.group(1).strip()
        if cpr_match:
            doc.cpr_number = cpr_match.group(0)
        if dob_match:
            doc.date_of_birth = dob_match.group(1)
        if nationality_match:
            doc.nationality = nationality_match.group(1).strip()

    except Exception as e:
        frappe.log_error(f"Error extracting CPR data: {{str(e)}}", "Passenger OCR Error")
