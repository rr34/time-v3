Awim code lives in `/home/nate/code/awim` (separate repo in the multi-root workspace). Look there for `tv3clock_api.py` and other awim services.

General:
- Keep changes scoped to the requested repo root (`/home/nate/code/time-v3-astroclock4`) unless explicitly asked.
- Prefer public URLs with `clock` (GroupSlug). `group_id` is fallback-only.
- Tags are legacy; do not add new tag-based queries.
- `groups` table uses `group_id` as PK; `GroupSlug` is for public URLs.

Cache Generation Notes (awim):
- Cache code is currently being added under `/home/nate/code/awim/tv3clock/` (e.g., `cache_runner.py`, `cache_jobs.py`, `cache_windows.py`, `cache_logging.py`).
- Generate cache first; do not switch read paths to consume cache yet.
- Use `LocationType='town_square'` (not `town_center`).
- Nightly run target is midnight at UTC-8; compute a 24-hour cache window with overlap (26 hours total processing window).
- Run `locations_cluster` first each nightly cycle.
- `locations_cluster` should check existing location rows first and only create new `auto_cluster` rows when needed:
  - outside 1 km of existing `auto_cluster`, and
  - outside 10 km of existing `town_square`.
- Prefer fewer files with clear text section headers in each file.
- Keep one log file per nightly cache run.
- Keep SQL centralized in `DBsqlstatements` where practical.
- Do not edit `astromath.py` for cache work; duplicate/modify logic in `astromath_cache.py`.
- Cache logging should write performance/run details to the `cache_logs` directory.

- artifae is the angular distance above / below the horizon throughout this project. Artifae is an arabic word for angle, like azimuth.