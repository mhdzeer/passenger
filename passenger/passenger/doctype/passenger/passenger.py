import frappe
import pytesseract
from PIL import Image
import io
import re
import base64
from datetime import datetime

def extract_data_from_cpr(doc, method):
    if not doc.cpr_image:
        return

    try:
        file_doc = frappe.get_doc("File", {"file_url": doc.cpr_image})
        image_data = base64.b64decode(file_doc.get_content())
        image = Image.open(io.BytesIO(image_data))

        text = pytesseract.image_to_string(image)
        text = text.replace("\n", " ").replace("\r", " ")
        text = re.sub(r"\s+", " ", text).strip().upper()

        # Bahrain CPR-specific extraction
        cpr_match = re.search(r"\b(\d{9})\b", text)
        name_match = re.search(r"(?:NAME[:\s]*)([A-Z ]{3,})", text)
        nationality_match = re.search(r"(?:NATIONALITY[:\s]*)([A-Z ]+)", text)
        gender_match = re.search(r"\b(MALE|FEMALE|M|F)\b", text)

        if cpr_match:
            doc.cpr_number = cpr_match.group(1)
            # Try to infer DOB from first 8 digits if they look like YYYYMMDD
            possible_dob = cpr_match.group(1)[:8]
            try:
                dob = datetime.strptime(possible_dob, "%Y%m%d").date()
                doc.date_of_birth = dob
            except ValueError:
                pass

        if name_match:
            doc.full_name = name_match.group(1).title().strip()
        else:
            alt = re.search(r"([A-Z]{2,}(?: [A-Z]{2,}){1,})", text)
            if alt:
                doc.full_name = alt.group(1).title().strip()

        if nationality_match:
            doc.nationality = nationality_match.group(1).title().strip()

        if gender_match:
            gender = gender_match.group(1).upper()
            doc.gender = "Male" if gender in ["M", "MALE"] else "Female"

    except Exception as e:
        frappe.log_error(f"Error extracting CPR data: {str(e)}", "Passenger OCR Error")
