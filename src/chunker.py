import re


def chunk_pages(pages, chunk_size=800, overlap=120):
    chunks = []

    ACT_START_PAGE = 8
    SCHEDULE_START_PAGE = 73

    current_section = "Unknown"
    current_schedule = None
    current_schedule_part = None

    section_pattern = re.compile(
        r"(?m)^\s*(\d+)\s*\.\s*([A-Z][^\n]*)"
    )

    schedule_pattern = re.compile(
        r"(?im)^\s*(FIRST|SECOND|THIRD|FOURTH|FIFTH)\s+SCHEDULE\s*$"
    )
    def add_chunk(text, page, label):
        text = re.sub(r"[ \t]+", " ", text).strip()

        if not text:
            return

        start = 0

        while start < len(text):

            max_end = min(start + chunk_size, len(text))

            if max_end == len(text):
                end = max_end

            else:
                search_start = start + chunk_size // 2
                boundary_text = text[search_start:max_end]

                boundaries = list(
                    re.finditer(r"[.!?;:]\s+|\n", boundary_text)
                )

                if boundaries:
                    end = search_start + boundaries[-1].end()

                else:
                    whitespace = [
                        match.start()
                        for match in re.finditer(r"\s+", text[start:max_end])
                    ]

                    if whitespace:
                        end = start + whitespace[-1]
                    else:
                        end = max_end

            part = text[start:end].strip()

            if part:
                chunks.append({
                    "text": part,
                    "page": page,
                    "section": label
                })

            if end >= len(text):
                break

            next_start = max(start + 1, end - overlap)

            while next_start < end and not text[next_start].isspace():
                next_start += 1

            start = next_start
    for item in pages:
        page = item["page"]
        text = item["text"].strip()

        # Handle Fifth Schedule Part B explicitly.
        if (
            page >= 73
            and re.search(
                r"(?im)^\s*B\.\s*Day to day repairs",
                text
            )
        ):
            chunks.append({
                "text": text,
                "page": page,
                "section": "Fifth Schedule, Part B"
            })
            current_schedule = "Fifth Schedule"
            current_schedule_part = "B"
            continue

        if page < ACT_START_PAGE or not text:
            continue

        # --------------------------------------------------
        # ORDINARY ACT SECTIONS: PDF pages 8-72
        # --------------------------------------------------
        if page < SCHEDULE_START_PAGE:
            current_schedule = None
            current_schedule_part = None

            matches = list(section_pattern.finditer(text))

            if not matches:
                add_chunk(text, page, current_section)
                continue

            for i, match in enumerate(matches):
                end = (
                    matches[i + 1].start()
                    if i + 1 < len(matches)
                    else len(text)
                )

                current_section = f"Section {match.group(1)}"

                add_chunk(
                    text[match.start():end],
                    page,
                    current_section
                )

            continue

        # --------------------------------------------------
        # SCHEDULES: PDF page 73 onwards
        # --------------------------------------------------
        matches = list(schedule_pattern.finditer(text))
        segments = []
        position = 0

        for match in matches:
            if match.start() > position:
                segments.append((text[position:match.start()], None))

            segments.append((match.group(0), match.group(1).title()))
            position = match.end()

        if position < len(text):
            segments.append((text[position:], None))

        if not segments:
            segments = [(text, None)]

        for segment_text, heading in segments:
            segment_text = segment_text.strip()

            if not segment_text:
                continue

            if heading:
                current_schedule = f"{heading} Schedule"
                current_schedule_part = None

                add_chunk(segment_text, page, current_schedule)
                continue

            if re.search(
                r"(?i)above translation of|published in the official gazette",
                segment_text
            ):
                continue

            if current_schedule == "Fifth Schedule":
                part_matches = list(re.finditer(
                    r"(?im)^\s*([AB])\.\s*(.+)$",
                    segment_text
                ))

                if part_matches:
                    for i, match in enumerate(part_matches):
                        current_schedule_part = match.group(1)

                        end = (
                            part_matches[i + 1].start()
                            if i + 1 < len(part_matches)
                            else len(segment_text)
                        )

                        add_chunk(
                            segment_text[match.start():end],
                            page,
                            f"Fifth Schedule, Part {current_schedule_part}"
                        )
                else:
                    label = (
                        f"Fifth Schedule, Part {current_schedule_part}"
                        if current_schedule_part
                        else "Fifth Schedule"
                    )

                    add_chunk(segment_text, page, label)

            elif current_schedule:
                add_chunk(segment_text, page, current_schedule)

    return chunks