from pathlib import Path

import faiss
import numpy as np


def _path(index_dir, report_id) -> str:
    return str(Path(index_dir) / f"{report_id}.faiss")


def build_index(index_dir, report_id, vectors: np.ndarray):
    index = faiss.IndexFlatIP(vectors.shape[1])  # cosine similarity (vectors are normalized)
    index.add(vectors)
    faiss.write_index(index, _path(index_dir, report_id))


def search(index_dir, report_id, query_vec: np.ndarray, k: int):
    index = faiss.read_index(_path(index_dir, report_id))
    k = min(k, index.ntotal)
    scores, ids = index.search(query_vec.reshape(1, -1), k)
    return [(int(i), float(s)) for i, s in zip(ids[0], scores[0]) if i >= 0]


def delete_index(index_dir, report_id):
    Path(_path(index_dir, report_id)).unlink(missing_ok=True)
