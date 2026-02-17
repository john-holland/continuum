"""
Continuum Library HTTP server (SPA + API).
Uses unified_semantic_archiver (unified-semantic-compressor package) for ContinuumDb.
Run: pip install -e ../unified-semantic-compressor && python serve_library.py
"""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.parse
from pathlib import Path

from flask import Flask, request, jsonify, send_file, redirect

from unified_semantic_archiver.db import ContinuumDb

_here = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=str(_here / "library"), static_url_path="")
LIBRARY_HTML = _here / "library" / "library.html"

DB_PATH = os.environ.get("CONTINUUM_DB_PATH") or str(_here / "continuum.db")
UPLOADS_DIR = Path(os.environ.get("CONTINUUM_LIBRARY_UPLOADS") or str(_here / "library_uploads"))
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

_db: ContinuumDb | None = None


def get_db() -> ContinuumDb:
    global _db
    if _db is None:
        _db = ContinuumDb(DB_PATH)
    return _db


def row_to_json(row: dict) -> dict:
    out = {}
    for k, v in row.items():
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat() if v else None
        else:
            out[k] = v
    return out


def get_tenant_from_request() -> str:
    """Tenant from X-Tenant-ID header or query param 'tenant'; default 'default'."""
    tenant = request.headers.get("X-Tenant-ID") or request.args.get("tenant")
    if tenant is not None:
        tenant = (tenant or "").strip()
    return tenant or "default"


@app.route("/")
@app.route("/library")
def index():
    if LIBRARY_HTML.exists():
        return send_file(str(LIBRARY_HTML))
    return "Library UI not found (missing library/library.html)", 404


@app.route("/api/library/search")
def search():
    try:
        tenant = get_tenant_from_request()
        document_type = request.args.get("document_type") or None
        q = request.args.get("q") or None
        lat = request.args.get("lat", type=float)
        lon = request.args.get("lon", type=float)
        distance_mi = request.args.get("distance_mi")
        limit = min(request.args.get("limit", default=100, type=int), 500)
        rows = get_db().library_document_search(
            document_type=document_type,
            q=q,
            lat=lat,
            lon=lon,
            distance_mi=distance_mi,
            tenant_id=tenant,
            limit=limit,
        )
        return jsonify([row_to_json(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/library/upload", methods=["POST"])
def upload():
    try:
        document_type = request.form.get("document_type", "").strip().lower()
        if document_type not in ("video", "document", "audio", "image", "program", "data"):
            return jsonify({"error": "Invalid document_type"}), 400
        lat = request.form.get("lat", type=float)
        lon = request.form.get("lon", type=float)
        altitude_m = request.form.get("altitude_m", type=float)
        url = (request.form.get("url") or "").strip() or None
        type_metadata_raw = request.form.get("type_metadata") or "{}"
        try:
            type_metadata = json.loads(type_metadata_raw)
        except json.JSONDecodeError:
            type_metadata = {}
        blob_ref = None
        if "file" in request.files and request.files["file"].filename:
            f = request.files["file"]
            safe_name = f"{hash(f.filename) % 2**32:08x}{Path(f.filename).suffix or '.bin'}"
            path = UPLOADS_DIR / safe_name
            f.save(str(path))
            blob_ref = safe_name
        tenant = get_tenant_from_request()
        doc_id = get_db().library_document_insert(
            document_type=document_type,
            blob_ref=blob_ref,
            url=url,
            type_metadata=type_metadata,
            owner_id=None,
            tenant_id=tenant,
            lat=lat,
            lon=lon,
            altitude_m=altitude_m,
        )
        return jsonify({"id": doc_id, "url": url or (f"/api/library/documents/{doc_id}/download" if doc_id else None)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/library/documents/<int:doc_id>")
def get_document(doc_id: int):
    try:
        tenant = get_tenant_from_request()
        row = get_db().library_document_get(doc_id, tenant_id=tenant)
        if not row:
            return jsonify({"error": "Not found"}), 404
        return jsonify(row_to_json(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/library/documents/<int:doc_id>/download")
def download_document(doc_id: int):
    try:
        tenant = get_tenant_from_request()
        row = get_db().library_document_get(doc_id, tenant_id=tenant)
        if not row:
            return jsonify({"error": "Not found"}), 404
        if row.get("url") and not row.get("blob_ref"):
            return redirect(row["url"], code=302)
        blob_ref = row.get("blob_ref")
        if not blob_ref:
            return jsonify({"error": "No file"}), 404
        path = UPLOADS_DIR / blob_ref
        if not path.is_file():
            return jsonify({"error": "File not found"}), 404
        return send_file(str(path), as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/geocode")
def geocode():
    address = (request.args.get("address") or "").strip()
    if not address:
        return jsonify({"error": "address query required"}), 400
    try:
        url = "https://nominatim.openstreetmap.org/search?q=" + urllib.parse.quote(address) + "&format=json&limit=1"
        req = urllib.request.Request(url, headers={"User-Agent": "ContinuumLibrary/1.0"})
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read().decode())
        if not data:
            return jsonify({"lat": None, "lon": None})
        return jsonify({"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"])})
    except Exception as e:
        return jsonify({"error": str(e)}), 502


def main():
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")


if __name__ == "__main__":
    main()
