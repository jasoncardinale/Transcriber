import re
from dataclasses import dataclass


@dataclass
class ParseResult:
    line: int
    text: str
    start: str
    end: str


def parse_vtt(transcription_path: str):
    results: list[ParseResult] = []
    timestamp_re = re.compile(r"(\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}\.\d{3})")

    with open(transcription_path, encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        match = timestamp_re.match(lines[i].strip())
        if match:
            start, end = match.groups()
            i += 1
            text_lines: list[str] = []
            while i < len(lines) and lines[i].strip() and not timestamp_re.match(lines[i].strip()):
                text_lines.append(lines[i].strip())
                i += 1
            text = " ".join(text_lines)
            if text:
                results.append(ParseResult(line=i, text=text, start=start, end=end))
        else:
            i += 1

    return results


def edit_vtt(transcription_path: str, existing: ParseResult, text: str):
    with open(transcription_path, "r+", encoding="utf-8") as f:
        lines = f.readlines()
        lines[existing.line] = f"{existing.start} --> {existing.end}\n{text}\n\n"
        f.seek(0)
        f.writelines(lines)
