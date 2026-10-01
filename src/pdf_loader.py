from pypdf import PdfReader
import re


def decode_glyph_text(text):
    """
    Convert PDF glyph references such as:
    /G82/G101/G102/G117/G110/G100
    into:
    Refund
    """

    def replace_glyph(match):
        code = int(match.group(1))

        if 0 <= code <= 255:
            return chr(code)

        return ""

    return re.sub(r"/G(\d+)", replace_glyph, text)


def extract_pages_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text()

        if raw_text:
            decoded_text = decode_glyph_text(raw_text)

            pages.append({
                "page": page_number,
                "text": decoded_text
            })

    return pages


def extract_text_from_pdf(pdf_path):
    pages = extract_pages_from_pdf(pdf_path)

    return "\n".join(page["text"] for page in pages)