import fitz  # PyMuPDF
import os

primary_dir = r"D:\MootCourt\supreme_court_judgments"

# Consumer case identifying keywords
consumer_keywords = [
    "Consumer Protection Act",
    "consumer dispute",
    "consumer complaint",
    "NCDRC",  # National Consumer Disputes Redressal Commission
    "SCDRC",  # State Consumer Disputes Redressal Commission
    "DCDRC",  # District Consumer Disputes Redressal Commission
    "consumer forum",
    "consumer court",
    "consumer redressal",
    "CPA, 1986",  # Consumer Protection Act, year reference
    "CPA 1986",
    "CPA, 2019",
    "CPA 2019",
    "consumer grievance",
    "consumer rights",
    "product liability",
    "deficiency in service",
    "unfair trade practice",
    "compensation to consumer",
    "consumer claim",
    "consumer dispute act",
    "consumer affairs",
    "faulty product",
    "e-jagriti",  # government portal for consumer affairs
    "district commission",
    "state commission",
    "goods or services",
    "contract of sale",
    "consumer awareness",
    "caveat consumer",
    "redressal agency",
    "deceptive practices",
    "Section 12 of CPA",
    "Section 21 of CPA",
    "Section 17 of CPA"
]

def is_consumer_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        for keyword in consumer_keywords:
            if keyword.lower() in text.lower():
                return True
        return False
    except Exception as e:
        print(f"Could not process {pdf_path}. Error: {e}")
        return False

pdf_count = 0
consumer_count = 0
deleted_count = 0

for root, dirs, files in os.walk(primary_dir):
    for filename in files:
        if filename.endswith(".pdf") or filename.endswith(".PDF"):
            pdf_count += 1
            file_path = os.path.join(root, filename)
            print(f"Processing: {file_path}")
            if is_consumer_pdf(file_path):
                consumer_count += 1
                print(f"  -> Consumer case (keeping)")
            else:
                deleted_count += 1
                print(f"  -> Non-consumer case (deleting)")
                os.remove(file_path)

print(f"\n=== Summary ===")
print(f"Total PDFs found: {pdf_count}")
print(f"Consumer cases kept: {consumer_count}")
print(f"Non-consumer cases deleted: {deleted_count}")
