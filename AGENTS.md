Awim code lives in `/home/nate/code/awim` (separate repo in the multi-root workspace). Look there for `tv3clock_api.py` and other awim services.

General:
- Keep changes scoped to the requested repo root (`/home/nate/code/time-v3-astroclock4`) unless explicitly asked.
- Prefer public URLs with `clock` (GroupSlug). `group_id` is fallback-only.
- Tags are legacy; do not add new tag-based queries.
- `groups` table uses `group_id` as PK; `GroupSlug` is for public URLs.
