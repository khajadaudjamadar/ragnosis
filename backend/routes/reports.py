import uuid
from datetime import datetime, timezone
from pathlib import Path

from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename

from services import chunker, embedder, ner, summarizer, vector_store
from services.pdf_utils import extract_text

bp = Blueprint("reports", __name__)
ALLOWED = {".pdf", ".txt", ".md"}


def current_user():
    return current_app.db.users.find_one({"_id": ObjectId(get_jwt_identity())})


def public_report(r, full=False):
    out = {
        "id": str(r["_id"]),
        "title": r["title"],
        "filename": r["filename"],
        "owner_id": str(r["owner_id"]),
        "owner_name": r.get("owner_name", ""),
        "uploaded_by": r.get("uploaded_by", ""),
        "created_at": r["created_at"].isoformat(),
        "num_chunks": len(r["chunks"]),
        "summary": r.get("summary", ""),
    }
    if full:
        out["entities"] = r.get("entities", [])
        out["preview"] = r["text"][:1500]
    return out


def load_report(report_id, user):
    """Return a report the user may access, or (None, error_response)."""
    try:
        oid = ObjectId(report_id)
    except InvalidId:
        return None, (jsonify(error="Invalid report id"), 400)
    report = current_app.db.reports.find_one({"_id": oid})
    if not report:
        return None, (jsonify(error="Report not found"), 404)
    if user["role"] != "doctor" and report["owner_id"] != user["_id"]:
        return None, (jsonify(error="Not allowed"), 403)
    return report, None


@bp.post("")
@jwt_required()
def upload():
    user = current_user()
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify(error="No file uploaded"), 400
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED:
        return jsonify(error="Only PDF or TXT files are allowed"), 400

    db = current_app.db
    owner = user
    patient_email = (request.form.get("patient_email") or "").strip().lower()
    if user["role"] == "doctor" and patient_email:
        owner = db.users.find_one({"email": patient_email, "role": "patient"})
        if not owner:
            return jsonify(error="No patient found with that email"), 404

    cfg = current_app.config
    saved = cfg["UPLOAD_DIR"] / f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    file.save(saved)
    try:
        text = extract_text(saved)
    except ValueError as e:
        saved.unlink(missing_ok=True)
        return jsonify(error=str(e)), 422

    chunks = chunker.chunk_text(text, cfg["CHUNK_WORDS"], cfg["CHUNK_OVERLAP"])
    vectors = embedder.embed(chunks)

    report = {
        "title": (request.form.get("title") or Path(file.filename).stem).strip(),
        "filename": file.filename,
        "stored_path": str(saved),
        "owner_id": owner["_id"],
        "owner_name": owner["name"],
        "uploaded_by": user["name"],
        "created_at": datetime.now(timezone.utc),
        "text": text,
        "chunks": chunks,
        "entities": ner.extract_entities(chunks),
        "summary": summarizer.summarize(text),
    }
    report["_id"] = db.reports.insert_one(report).inserted_id
    vector_store.build_index(cfg["INDEX_DIR"], str(report["_id"]), vectors)
    return jsonify(report=public_report(report, full=True)), 201


@bp.get("")
@jwt_required()
def list_reports():
    user = current_user()
    query = {} if user["role"] == "doctor" else {"owner_id": user["_id"]}
    rows = current_app.db.reports.find(query).sort("created_at", -1)
    return jsonify(reports=[public_report(r) for r in rows])


@bp.get("/<report_id>")
@jwt_required()
def get_report(report_id):
    report, err = load_report(report_id, current_user())
    if err:
        return err
    return jsonify(report=public_report(report, full=True))


@bp.delete("/<report_id>")
@jwt_required()
def delete_report(report_id):
    report, err = load_report(report_id, current_user())
    if err:
        return err
    current_app.db.reports.delete_one({"_id": report["_id"]})
    current_app.db.chats.delete_many({"report_id": report["_id"]})
    vector_store.delete_index(current_app.config["INDEX_DIR"], str(report["_id"]))
    Path(report["stored_path"]).unlink(missing_ok=True)
    return jsonify(ok=True)
