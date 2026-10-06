from flask import current_app

SYSTEM_PROMPT = (
    "You are a careful medical-report assistant. Answer ONLY from the provided report excerpts. "
    "If the answer is not in the excerpts, say you cannot find it in the report. "
    "Use plain language, and remind the user to confirm medical decisions with their doctor."
)


def generate(question: str, contexts):
    key = current_app.config["GROQ_API_KEY"]
    if not key:
        return None
    from groq import Groq

    context_block = "\n\n".join(f"[{i + 1}] {c}" for i, c in enumerate(contexts))
    resp = Groq(api_key=key).chat.completions.create(
        model=current_app.config["GROQ_MODEL"],
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Report excerpts:\n{context_block}\n\nQuestion: {question}"},
        ],
    )
    return resp.choices[0].message.content.strip()
