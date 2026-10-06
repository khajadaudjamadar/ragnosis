import numpy as np
from flask import current_app

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(current_app.config["EMBED_MODEL"])
    return _model


def embed(texts):
    vecs = _get_model().encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(vecs, dtype="float32")
