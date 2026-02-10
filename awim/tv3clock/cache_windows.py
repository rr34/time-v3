from datetime import datetime, timedelta, timezone
import numpy as np


# ----- Window Boundaries -----
def get_nightly_window_utc(now_utc=None, utc_offset_hours=-8, duration_hours=24, overlap_hours=2):
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)
    elif now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)
    else:
        now_utc = now_utc.astimezone(timezone.utc)

    local_now = now_utc + timedelta(hours=utc_offset_hours)
    local_midnight = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_utc = local_midnight - timedelta(hours=utc_offset_hours)
    end_utc = start_utc + timedelta(hours=duration_hours + overlap_hours)

    return start_utc.replace(tzinfo=None), end_utc.replace(tzinfo=None)


# ----- Moment Arrays -----
def build_moments_iso_utc(window_start_utc, window_end_utc, step_seconds):
    start64 = np.datetime64(window_start_utc, 's')
    end64 = np.datetime64(window_end_utc, 's')
    step64 = np.timedelta64(step_seconds, 's')
    moments64 = np.arange(start64, end64, step64, dtype='datetime64[s]')
    return np.datetime_as_string(moments64, unit='s', timezone='UTC').tolist()


def build_day_range(start_day_utc, end_day_utc):
    start_day64 = np.datetime64(start_day_utc, 'D')
    end_day64 = np.datetime64(end_day_utc, 'D')
    return np.arange(start_day64, end_day64, np.timedelta64(1, 'D'), dtype='datetime64[D]')
