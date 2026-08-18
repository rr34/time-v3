"""AWIM CLI entrypoint.

Usage:
    python -m awim <task> [--root PATH] [--group-id ID]
"""
import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

AWIM_ROOT = Path(__file__).resolve().parent
if str(AWIM_ROOT) not in sys.path:
    sys.path.insert(0, str(AWIM_ROOT))

from workflows import awimactions  # noqa: E402


def _normalize_task(task: str) -> str:
    return task.strip().lower().replace('_', '-')


def _set_root(root_arg: str | None) -> Path:
    root = Path(root_arg).expanduser().resolve() if root_arg else AWIM_ROOT
    if not root.exists():
        raise FileNotFoundError(f"Root path does not exist: {root}")
    os.chdir(root)
    return root


def _load_env(root: Path) -> None:
    env_path = root / '.env'
    if env_path.exists():
        load_dotenv(env_path)


def _task_lightroom_timelapse_xmp_process(_args: argparse.Namespace) -> None:
    awimactions.lightroom_timelapse_XMP_process()


def _task_generate_metatext_files(_args: argparse.Namespace) -> None:
    awimactions.generate_metatext_files()


def _task_cam_calibration(_args: argparse.Namespace) -> None:
    awimactions.cam_calibration()


def _task_add_camfilenames_todb(_args: argparse.Namespace) -> None:
    awimactions.add_camfilenames_todb()


def _task_generate_image_tags(args: argparse.Namespace) -> None:
    if args.group_id is None:
        raise ValueError('generate-image-tags requires --group-id')
    awimactions.generate_image_tags(args.group_id)


def _task_parse_brightstar_text(_args: argparse.Namespace) -> None:
    awimactions.parse_brightstar_text()


def _task_db_update(_args: argparse.Namespace) -> None:
    awimactions.db_update()


TASKS: dict[str, tuple[callable, str]] = {
    'lightroom-timelapse-xmp-process': (
        _task_lightroom_timelapse_xmp_process,
        'Process XMP files and apply sun/moon tags and interpolation.',
    ),
    'generate-metatext-files': (
        _task_generate_metatext_files,
        'Generate JSON metadata files for files in working/.',
    ),
    'cam-calibration': (
        _task_cam_calibration,
        'Generate cam_awim.json from calibration inputs in working/.',
    ),
    'add-camfilenames-todb': (
        _task_add_camfilenames_todb,
        'Insert camera file basenames from working/ into the DB.',
    ),
    'generate-image-tags': (
        _task_generate_image_tags,
        'Create AWIM tags and image copies for a batch group ID.',
    ),
    'parse-brightstar-text': (
        _task_parse_brightstar_text,
        'Parse bright star text file into CSV outputs.',
    ),
    'db-update': (
        _task_db_update,
        'Run constellation update helper against the DB.',
    ),
}


def _print_tasks() -> None:
    print('Available tasks:')
    for name in sorted(TASKS.keys()):
        print(f'  {name}  - {TASKS[name][1]}')


def _print_recipes() -> None:
    print(AWIM_ROOT / 'docs' / 'recipes.md')


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='awim',
        description='AWIM task runner. Use "list" to see tasks or "recipes" for docs.',
    )
    parser.add_argument('task', help='Task name, or "list" / "recipes".')
    parser.add_argument(
        '--root',
        help='Root path for file-based tasks (default: AWIM repo directory).',
    )
    parser.add_argument(
        '--group-id',
        type=int,
        help='Batch group ID for generate-image-tags.',
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    task = _normalize_task(args.task)
    if task == 'list':
        _print_tasks()
        return 0
    if task == 'recipes':
        _print_recipes()
        return 0

    try:
        root = _set_root(args.root)
    except Exception as exc:
        parser.error(str(exc))
        return 2

    _load_env(root)

    if task not in TASKS:
        parser.error(f'Unknown task: {args.task}')
        return 2

    if task == 'generate-image-tags' and args.group_id is None:
        parser.error('--group-id is required for generate-image-tags')
        return 2

    handler = TASKS[task][0]
    handler(args)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
