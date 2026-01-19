import re


def parse_vtt(transcription_path: str, audio_path: str | None):
    results: list[tuple[str, str, str]] = []
    timestamp_re = re.compile(r"(\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}\.\d{3})")

    with open(transcription_path, encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        match = timestamp_re.match(lines[i].strip())
        if match:
            start, end = match.groups()
            i += 1
            text_lines = []
            while (
                i < len(lines)
                and lines[i].strip()
                and not timestamp_re.match(lines[i].strip())
            ):
                text_lines.append(lines[i].strip())
                i += 1
            text = " ".join(text_lines)
            if text:
                results.append((text, start, end))
        else:
            i += 1

    return results
