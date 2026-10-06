from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from routes.reports import current_user, load_report
from services.rag import answer_question

bp = Blueprint("chat", __name__)


@bp.post("/<report_id>/ask")
@jwt_required()
def ask(report_id):
    user = current_user()
    report, err = load_report(report_id, user)
    if err:
        return err
    question = ((request.get_json(silent=True) or {}).get("question") or "").strip()
    if not question:
        return jsonify(error="Question is required"), 400

    answer, sources = answer_question(report, question)
    current_app.db.chats.insert_one({
        "report_id": report["_id"], "user_id": user["_id"], "question": question,
        "answer": answer, "sources": sources, "created_at": datetime.now(timezone.utc),
    })
    return jsonify(answer=answer, sources=sources)


@bp.get("/<report_id>/history")
@jwt_required()
def history(report_id):
    user = current_user()
    report, err = load_report(report_id, user)
    if err:
        return err
    rows = current_app.db.chats.find(
        {"report_id": report["_id"], "user_id": user["_id"]}).sort("created_at", 1)
    return jsonify(messages=[
        {"question": r["question"], "answer": r["answer"], "sources": r["sources"]} for r in rows])
