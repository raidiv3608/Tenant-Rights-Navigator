import re


def chunk_pages(pages, chunk_size=800, overlap=120):
    chunks = []

    for page in pages:
        text = page["text"]
        page_number = page["page"]

        # Try to split around numbered legal sections.
        sections = re.split(
            r'(?=\n?\s*\d+\.\s+[A-Z][^\n]*?(?:-|—))',
            text
        )

        for section in sections:
            section = section.strip()

            if not section:
                continue

            # If a section is small enough, keep it together.
            if len(section) <= chunk_size:
                chunks.append({
                    "text": section,
                    "page": page_number
                })

            # If a section is large, split it with overlap.
            else:
                start = 0

                while start < len(section):
                    end = start + chunk_size
                    chunk_text = section[start:end].strip()

                    if chunk_text:
                        chunks.append({
                            "text": chunk_text,
                            "page": page_number
                        })

                    start += chunk_size - overlap

    return chunks