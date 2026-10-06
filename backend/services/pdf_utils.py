from pathlib import Path

from pypdf import PdfReader


def extract_text(path: Path) -> str:
    """Extract text from a PDF or plain-text file."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        text = "\n".join((p.extract_text() or "") for p in reader.pages)
    elif suffix in (".txt", ".md"):
        text = path.read_text(encoding="utf-8", errors="ignore")
    else:
        raise ValueError("Unsupported file type. Upload a PDF or TXT file.")
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if len(text) < 20:
        raise ValueError("No readable text found (scanned PDFs need OCR, which is not included).")
    return text
