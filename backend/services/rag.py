from flask import current_app

from services import embedder, llm, vector_store


def answer_question(report: dict, question: str):
    cfg = current_app.config
    qvec = embedder.embed([question])[0]
    hits = vector_store.search(cfg["INDEX_DIR"], str(report["_id"]), qvec, cfg["TOP_K"])
    chunks = report["chunks"]
    contexts = [chunks[i] for i, _ in hits]
    sources = [{"chunk": i, "score": round(s, 3), "text": chunks[i]} for i, s in hits]

    answer = llm.generate(question, contexts)
    if answer is None:
        answer = ("LLM is not configured (set GROQ_API_KEY in backend/.env). "
                  "Here are the most relevant passages from the report:\n\n" + "\n\n".join(contexts))
    return answer, sources
