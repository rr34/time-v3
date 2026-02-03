# Time v3 Astronomical Clock Flow Maps

Clock-specific request/response flow maps for the tv3 clock integration.

## /getevents End-to-End Flow (Frontend → Express → AWIM)
1. Frontend `client/src/App.tsx` posts `/awim/getevents` with `location`, `elevation`, `currenttime`, and `nowmoments_clockstrings`.
2. Express `api/index.js` allowlists `getevents` and proxies to `AWIM_BASE_URL/getevents`.
3. AWIM `tv3clock_api.py` calls `tv3clock.clockactions.get_events` and `tv3clock.clockactions.get_sunmoon_details`.
4. `tv3clock.clockactions.get_events` computes daily sun/moon rise-set times and new/full moon times, then formats sun/moon astro data for those events.
5. `tv3clock.clockactions.get_sunmoon_details` computes detailed sun/moon positions for the provided `nowmoments_clockstrings`.
6. Response JSON includes `sundaily`, `sundailydata`, `moondaily`, `moondailydata`, `newmoon time`, `newmoon angle`, `fullmoon time`, `fullmoon angle`, and `sunmoon_details`.

## /celestialinphotos End-to-End Flow (Frontend → Express → AWIM)
1. Frontend `client/src/utils/useClockGalleryData.ts` requests `/getimageslist/query` and builds `awims_dict` keyed by `Basename`.
2. Frontend posts to `/awim/celestialinphotos` with `awims_dict`, `momentsarray`, `requestlist`, `MagRankAllMax`, `LatDecFilter`.
3. Express `api/index.js` allowlists `celestialinphotos` and proxies to `AWIM_BASE_URL/celestialinphotos`.
4. AWIM `tv3clock_api.py` reads the first `awimTag` for `location` (and elevation when available) and computes astro data via `tv3clock.clockactions.get_astrodata`.
5. For each image in `awims_dict`, AWIM computes bodies that appear in the image via `tv3clock.clockactions.get_celestialinphoto`.
6. Response JSON includes `"astro dict"` (time-based celestial data) and `"bodies in images dicts"` (per-image placements).


# Metadata Lists
