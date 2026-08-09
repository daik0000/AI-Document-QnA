from app.services.text_extraction_service import extract_text

text = extract_text("storage/1/e69194f60df646089c158d792bd9fc37.pdf", "pdf")

print("[DEBUG] Extracted text (first 50 characters):")
print(text[:50])