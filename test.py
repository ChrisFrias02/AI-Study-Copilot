from dotenv import load_dotenv
load_dotenv()

from pdf_processor import extract_text_from_pdf


with open(r"C:\Users\chris\Downloads\CSE_4820_Final_Study_Guide (2).pdf", "rb") as f:
    try:
        text = extract_text_from_pdf(f)
        print("Success! Characters extracted:", len(text))
        print(text[:300])
    except ValueError as e:
        print("Error:", e)