from src.pdf_loader import extract_text_from_pdf
from src.chunker import chunk_text


pdf_path = "data/Tenant Rights Navigator.pdf"    

# Extract text from PDF
text = extract_text_from_pdf(pdf_path)

# Split text into chunks
chunks = chunk_text(text)

print("PDF TEXT EXTRACTED SUCCESSFULLY!")
print(f"Total characters: {len(text)}")
print(f"Total chunks: {len(chunks)}")

print("\n--- FIRST CHUNK ---")
print(chunks[0])