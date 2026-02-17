# Dependencies

## USC (unified-semantic-compressor)

Continuum depends on the **unified-semantic-compressor** package (import name: `unified_semantic_archiver`). Install it from source before installing continuum:

```bash
pip install -e /path/to/unified-semantic-compressor
pip install -r requirements.txt
```

If the repos are siblings:

```bash
pip install -e ../unified-semantic-compressor
pip install -r requirements.txt
```

### Version expectations

- Continuum expects USC to provide:
  - `unified_semantic_archiver.db.ContinuumDb` with `library_document_insert`, `library_document_get`, `library_document_list`, `library_document_search` accepting a `tenant_id` parameter (default `"default"`).
  - Schema including `library_documents` with a `tenant_id` column (see USC `db/schema.sql` and `db/MIGRATION_tenant_id.md` for existing DBs).
- There is no pinned version; use a USC commit or release that includes the tenant-aware library_documents API and schema. If you need a version contract, pin the USC install to a specific commit or tag when installing, e.g. `pip install -e git+https://...@<commit>#egg=unified_semantic_archiver` or install from a local clone at a known commit.
