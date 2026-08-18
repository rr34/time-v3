# AWIM Recipes (Task Runner)

This file is the canonical list of CLI tasks for AWIM. Each task operates on files under `working/` by default.

Command pattern:
`python -m awim <task> [--root PATH] [--group-id ID]`

Note:
- The simplest way to run these is from the AWIM directory itself (so the package is on the Python path).
- Example: `cd /home/nate/code/awim` then `python -m awim list`.

Common commands:
- `python -m awim list` prints the task list.
- `python -m awim recipes` prints the path to this file.

Tasks:
- `lightroom-timelapse-xmp-process` — Process XMP files in `working/`, add sun/moon tags, write CSV snapshots, and update XMPs.
- `generate-metatext-files` — Generate JSON metadata files for every file in `working/`.
- `cam-calibration` — Generate `cam_awim.json` from `working/calimage.jpg` and `working/calspreadsheet.xlsx`.
- `add-camfilenames-todb` — Insert camera file basenames from `working/` into the database.
- `generate-image-tags` — Build AWIM tag JSONs and copy images for a batch group ID. Requires `--group-id`.
- `parse-brightstar-text` — Parse `working/V_50.txt` into CSV outputs.
- `db-update` — Run database constellation name updates.

Notes:
- `--root` changes the working directory used by file-based tasks. Default is the AWIM repo directory.
- All tasks run synchronously in-process and assume local files are prepared.
