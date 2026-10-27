"""Heading-aware chunking: one chunk per H2 section, split further only when long."""
import re
from dataclasses import dataclass

MAX_WORDS = 250


@dataclass
class Chunk:
    doc: str
    doc_title: str
    heading: str
    text: str
    part: int = 0


def _split_long(body: str, max_words: int) -> list[str]:
    """Pack paragraphs/bullets into pieces of at most max_words, never cutting mid-line."""
    pieces, current, count = [], [], 0
    for block in re.split(r"\n\s*\n", body.strip()):
        words = len(block.split())
        if current and count + words > max_words:
            pieces.append("\n\n".join(current))
            current, count = [], 0
        current.append(block)
        count += words
    if current:
        pieces.append("\n\n".join(current))
    return pieces


def chunk_markdown(doc: str, markdown: str, max_words: int = MAX_WORDS) -> list[Chunk]:
    lines = markdown.splitlines()
    title = doc
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        lines = lines[1:]

    sections: list[tuple[str, list[str]]] = [("Overview", [])]
    for line in lines:
        if line.startswith("## "):
            sections.append((line[3:].strip(), []))
        else:
            sections[-1][1].append(line)

    chunks = []
    for heading, body_lines in sections:
        body = "\n".join(body_lines).strip()
        if not body:
            continue
        for part, piece in enumerate(_split_long(body, max_words)):
            # Title and heading go into the text so the embedding sees the context.
            text = f"{title} > {heading}\n\n{piece}"
            chunks.append(Chunk(doc, title, heading, text, part))
    return chunks
