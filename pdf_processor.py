import fitz

MIN_CHARS_PER_PAGE = 50

def extract_text_from_pdf(file):
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    full_text = ""
    total_pages = len(pdf)

    for page in pdf:
        full_text += page.get_text()

    pdf.close()

    avg_chars = len(full_text) / total_pages if total_pages > 0 else 0

    if avg_chars < MIN_CHARS_PER_PAGE:
        raise ValueError("This PDF appears to be scanned or image-based. Please upload a typed PDF.")

    return full_text.strip()