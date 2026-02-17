# Continuum

Continuum library server: upload, search, and view documents with location and type-specific metadata. Uses **USC** (unified-semantic-compressor; Python package name `unified_semantic_archiver`) for the continuum DB and schema.

## Getting started (full stack)

1. **Install USC** (unified-semantic-compressor): `pip install -e /path/to/unified-semantic-compressor`
2. **Install continuum deps:** from this repo, `pip install -r requirements.txt`
3. **Init DB:** `python -m unified_semantic_archiver init --db ./continuum.db`
4. **Run continuum server:** `python serve_library.py` → http://localhost:5050
5. **(Optional) Unity (Drawer 2):** Open the project, go to Window → Continuum → Continuum Library, set Base URL to http://localhost:5050 (and DB path for Explorer). See your Drawer 2 repo’s `Scripts/CONTINUUM_AND_COMPRESSOR.md`.
6. **(Optional) Cave (log-view-machine):** Set `CONTINUUM_LIBRARY_URL=http://localhost:5050` so the Cave server proxies `/api/continuum/library/*` to continuum.

## Install

```bash
# From continuum repo root; install the compressor first (sibling or clone)
pip install -e ../unified-semantic-compressor
pip install -r requirements.txt
```

If the compressor is elsewhere, install it and ensure `unified_semantic_archiver` is on your Python path, then `pip install -r requirements.txt`. See [DEPENDENCIES.md](DEPENDENCIES.md) for version expectations.

## Run

```bash
python serve_library.py
```

Open http://localhost:5050. Optional env:

- `PORT` — default 5050
- `CONTINUUM_DB_PATH` — path to continuum.db (default: ./continuum.db in repo root)
- `CONTINUUM_LIBRARY_UPLOADS` — uploads directory (default: ./library_uploads)
- `FLASK_DEBUG=1` — enable debug mode

## Schema

Continuum does not define its own schema. All tables (including `library_documents`) live in **USC** (`unified_semantic_archiver/db/schema.sql`). The continuum app uses USC’s `ContinuumDb` and the same DB file. To add or change tables, extend USC’s schema and migrations; see the USC repo’s `unified_semantic_archiver/db/SCHEMA_OWNERSHIP.md`.

## First run

Initialize the continuum DB (creates schema including library_documents):

```bash
python -m unified_semantic_archiver init --db ./continuum.db
```

## Unity

Point the Continuum Library window (Window → Continuum → Continuum Library) Base URL to this server (e.g. http://localhost:5050). The Continuum Explorer can use the same continuum.db path with the Python CLI.
