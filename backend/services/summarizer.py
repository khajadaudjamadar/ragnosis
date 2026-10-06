from flask import current_app

_pipe = None


def summarize(text: str) -> str:
    """BART summary of the report (optional, lazy-loaded)."""
    global _pipe
    if not current_app.config["ENABLE_SUMMARY"]:
        return ""
    if _pipe is None:
        from transformers import pipeline

        _pipe = pipeline("summarization", model=current_app.config["SUMMARY_MODEL"])
    result = _pipe(text[:3500], max_length=150, min_length=30, truncation=True, do_sample=False)
    return result[0]["summary_text"]
