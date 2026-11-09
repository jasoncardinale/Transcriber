import re


def find_matches(texts: list[str], query: str) -> list[tuple[int, int, int]]:
    if not query.strip():
        return []

    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return [(i, match.start(), match.end()) for i, text in enumerate(texts) for match in pattern.finditer(text)]
