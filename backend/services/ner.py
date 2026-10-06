from flask import current_app

_pipe = None


def extract_entities(chunks, max_chunks=12, max_entities=40):
    """BioBERT-based medical entity extraction (optional, lazy-loaded)."""
    global _pipe
    if not current_app.config["ENABLE_NER"]:
        return []
    if _pipe is None:
        from transformers import pipeline

        _pipe = pipeline("token-classification", model=current_app.config["NER_MODEL"],
                         aggregation_strategy="simple")
    seen, out = set(), []
    for chunk in chunks[:max_chunks]:
        for ent in _pipe(chunk[:1500]):
            text = ent["word"].strip()
            key = text.lower()
            if len(text) > 2 and key not in seen:
                seen.add(key)
                out.append({"text": text, "label": ent["entity_group"]})
    return out[:max_entities]
