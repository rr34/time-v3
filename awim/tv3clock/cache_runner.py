from datetime import datetime, timezone
from pathlib import Path
import os
import time
from workflows.awimactions import locations_cluster
from tv3clock import cache_jobs
from tv3clock import cache_windows
from tv3clock.cache_logging import CacheRunLogger


LOCK_FILE_PATH = Path('/tmp/awim_nightly_cache.lock')


# ----- Locking -----
def _acquire_lock(lock_path=LOCK_FILE_PATH):
    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode('utf-8'))
        return fd
    except FileExistsError:
        return None


def _release_lock(lock_fd, lock_path=LOCK_FILE_PATH):
    if lock_fd is None:
        return
    os.close(lock_fd)
    try:
        lock_path.unlink(missing_ok=True)
    except Exception:
        pass


# ----- Nightly Orchestration -----
def run_nightly_cache(utc_offset_hours=-8, throttle_seconds=0.15):
    repo_root = Path(__file__).resolve().parents[1]
    logger = CacheRunLogger(repo_root=repo_root, run_name='nightly_cache')
    lock_fd = _acquire_lock()
    if lock_fd is None:
        logger.log('run_skipped', reason='lock_exists')
        logger.close(success=False)
        return False

    success = False
    try:
        now_utc = datetime.now(timezone.utc)
        window_start_utc, window_end_utc = cache_windows.get_nightly_window_utc(
            now_utc=now_utc,
            utc_offset_hours=utc_offset_hours,
            duration_hours=24,
            overlap_hours=2,
        )
        logger.log(
            'window_ready',
            window_start_utc=window_start_utc.isoformat(sep=' '),
            window_end_utc=window_end_utc.isoformat(sep=' '),
            utc_offset_hours=utc_offset_hours,
        )

        locations_cluster()
        logger.log('locations_cluster_completed')

        town_square_without_photos, represented_in_photos = cache_jobs.split_locations_for_nightly_cache()
        logger.log(
            'locations_selected',
            town_square_without_photos=len(town_square_without_photos),
            represented_in_photos=len(represented_in_photos),
        )

        now_utc_naive = now_utc.replace(tzinfo=None)
        cache_jobs.cache_global_newfullmoon_events(now_utc_naive, logger=logger)
        cache_jobs.cache_global_newfullmoon_details(logger=logger)

        for location in town_square_without_photos:
            cache_jobs.cache_daily_events_for_location(location, now_utc_naive, logger=logger)
            cache_jobs.cache_location_newfullmoon_events_for_location(location, now_utc_naive, logger=logger)
            cache_jobs.cache_sunmoon_details_for_location(location, window_start_utc, window_end_utc, logger=logger)
            cache_jobs.cache_daily_event_azart_for_location(location, logger=logger)
            if throttle_seconds > 0:
                time.sleep(throttle_seconds)

        for location in represented_in_photos:
            cache_jobs.cache_daily_events_for_location(location, now_utc_naive, logger=logger)
            cache_jobs.cache_location_newfullmoon_events_for_location(location, now_utc_naive, logger=logger)
            cache_jobs.cache_sunmoon_details_for_location(location, window_start_utc, window_end_utc, logger=logger)
            cache_jobs.cache_astrodata_for_location(location, window_start_utc, window_end_utc, logger=logger)
            cache_jobs.cache_daily_event_azart_for_location(location, logger=logger)
            if throttle_seconds > 0:
                time.sleep(throttle_seconds)

        success = True
        return True
    except Exception as exc:
        logger.log('run_error', error=str(exc))
        raise
    finally:
        _release_lock(lock_fd)
        logger.close(success=success)


if __name__ == '__main__':
    run_nightly_cache()
