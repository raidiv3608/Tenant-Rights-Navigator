import re


def chunk_pages(pages, chunk_size=800, overlap=120):

    chunks = []

    # The actual Karnataka Rent Act begins on PDF page 8.
    # Pages 1-7 contain the arrangement of sections,
    # statement of objects and reasons, and introductory material.
    ACT_START_PAGE = 8

    current_section = "Unknown"

    for page in pages:

        page_number = page["page"]
        text = page["text"].strip()

        # -------------------------------------------------------
        # IGNORE FRONT MATTER
        # -------------------------------------------------------

        if page_number < ACT_START_PAGE:
            continue

        # -------------------------------------------------------
        # DETECT ACT SECTIONS
        #
        # Examples:
        # 1.Short title...
        # 2.Application of the Act...
        # 3.Definitions...
        # -------------------------------------------------------

        section_pattern = (
            r"(?m)^\s*(\d+)\s*\.\s*"
            r"([A-Z][^\n]*)"
        )

        matches = list(
            re.finditer(
                section_pattern,
                text
            )
        )

        # -------------------------------------------------------
        # PAGE CONTAINS ONE OR MORE SECTION HEADINGS
        # -------------------------------------------------------

        if matches:

            for i, match in enumerate(matches):

                section_number = match.group(1)

                section_name = (
                    f"Section {section_number}"
                )

                # Remember the current section.
                current_section = section_name

                start = match.start()

                if i + 1 < len(matches):

                    end = matches[i + 1].start()

                else:

                    end = len(text)

                section_text = (
                    text[start:end].strip()
                )

                # ------------------------------------------------
                # SMALL SECTION
                # ------------------------------------------------

                if len(section_text) <= chunk_size:

                    chunks.append(
                        {
                            "text": section_text,
                            "page": page_number,
                            "section": section_name
                        }
                    )

                # ------------------------------------------------
                # LARGE SECTION
                # ------------------------------------------------

                else:

                    start_position = 0

                    while (
                        start_position
                        < len(section_text)
                    ):

                        end_position = (
                            start_position
                            + chunk_size
                        )

                        chunk_text = (
                            section_text[
                                start_position:end_position
                            ].strip()
                        )

                        if chunk_text:

                            chunks.append(
                                {
                                    "text": chunk_text,
                                    "page": page_number,
                                    "section": section_name
                                }
                            )

                        start_position += (
                            chunk_size - overlap
                        )

        # -------------------------------------------------------
        # PAGE CONTINUES A PREVIOUS SECTION
        # -------------------------------------------------------

        else:

            if not text:
                continue

            if len(text) <= chunk_size:

                chunks.append(
                    {
                        "text": text,
                        "page": page_number,
                        "section": current_section
                    }
                )

            else:

                start_position = 0

                while (
                    start_position
                    < len(text)
                ):

                    end_position = (
                        start_position
                        + chunk_size
                    )

                    chunk_text = (
                        text[
                            start_position:end_position
                        ].strip()
                    )

                    if chunk_text:

                        chunks.append(
                            {
                                "text": chunk_text,
                                "page": page_number,
                                "section": current_section
                            }
                        )

                    start_position += (
                        chunk_size - overlap
                    )

    return chunks