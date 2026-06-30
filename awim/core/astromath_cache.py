from datetime import timezone
import math
import numpy as np
import astropy.units as u
from astropy.time import Time
import astroplan

DAILY_EVENT_DUPLICATE_TOLERANCE_SECONDS = 240
NO_EVENT_SEED_ADVANCE_DAYS = 1
AFTER_EVENT_SEED_ADVANCE_HOURS = 12
MAX_ITERATION_PADDING_DAYS = 8
NEWFULL_SEED_STEP_DAYS = 7

EVENT_SPECS = (
    {'event_type': 'midnight', 'event_body': 'sun', 'method_name': 'midnight'},
    {'event_type': 'noon', 'event_body': 'sun', 'method_name': 'noon'},
    {'event_type': 'sunrise', 'event_body': 'sun', 'method_name': 'sun_rise_time', 'horizon': -0.833 * u.deg},
    {'event_type': 'sunset', 'event_body': 'sun', 'method_name': 'sun_set_time', 'horizon': -0.833 * u.deg},
    {'event_type': 'bmat', 'event_body': 'sun', 'method_name': 'sun_rise_time', 'horizon': -18 * u.deg},
    {'event_type': 'bmnt', 'event_body': 'sun', 'method_name': 'sun_rise_time', 'horizon': -12 * u.deg},
    {'event_type': 'bmct', 'event_body': 'sun', 'method_name': 'sun_rise_time', 'horizon': -6 * u.deg},
    {'event_type': 'eect', 'event_body': 'sun', 'method_name': 'sun_set_time', 'horizon': -6 * u.deg},
    {'event_type': 'eent', 'event_body': 'sun', 'method_name': 'sun_set_time', 'horizon': -12 * u.deg},
    {'event_type': 'eeat', 'event_body': 'sun', 'method_name': 'sun_set_time', 'horizon': -18 * u.deg},
    {'event_type': 'riseplus6deg', 'event_body': 'sun', 'method_name': 'sun_rise_time', 'horizon': 6 * u.deg},
    {'event_type': 'setminus6deg', 'event_body': 'sun', 'method_name': 'sun_set_time', 'horizon': 6 * u.deg},
    {'event_type': 'moonrise', 'event_body': 'moon', 'method_name': 'moon_rise_time', 'horizon': 0 * u.deg},
    {'event_type': 'moonset', 'event_body': 'moon', 'method_name': 'moon_set_time', 'horizon': 0 * u.deg},
)


# ----- Observer -----
def _build_observer(location_latlng, elevation_msl=0):
    return astroplan.Observer(
        longitude=float(location_latlng[1]) * u.deg,
        latitude=float(location_latlng[0]) * u.deg,
        elevation=float(elevation_msl) * u.m,
        name='Time v3 Cache',
        timezone=timezone.utc,
    )


# ----- Helpers -----
def _safe_time64(event_time):
    if event_time is None:
        return None
    try:
        value = np.datetime64(event_time.datetime64, 's')
        if np.isnat(value):
            return None
        return value
    except Exception:
        return None


def _to_mysql_datetime(moment64):
    return np.datetime_as_string(moment64.astype('datetime64[s]'), unit='s').replace('T', ' ')


def _append_row(rows, location_id, event_type, moment64, event_body):
    location_id_value = None if location_id is None else int(location_id)
    rows.append((
        location_id_value,
        event_type,
        _to_mysql_datetime(moment64),
        event_body,
        None,
        None,
        None,
    ))


def _append_row_with_phase(rows, location_id, event_type, moment64, event_body, event_moon_phase_angle):
    location_id_value = None if location_id is None else int(location_id)
    rows.append((
        location_id_value,
        event_type,
        _to_mysql_datetime(moment64),
        event_body,
        None,
        None,
        float(event_moon_phase_angle),
    ))


def _get_event_time64(observer, method_name, seed64, gridpts, which='next', horizon=None):
    method = getattr(observer, method_name)
    kwargs = {
        'time': Time(seed64),
        'which': which,
        'n_grid_points': gridpts,
    }
    if horizon is not None:
        kwargs['horizon'] = horizon
    try:
        return _safe_time64(method(**kwargs))
    except Exception:
        return None


def _append_moonphase_event_if_unique(
    rows,
    location_id,
    event_type,
    moment64,
    angle_deg,
    window_start64,
    window_end64,
    seen_moments,
    dedupe_tolerance_seconds,
):
    if moment64 is None:
        return
    if angle_deg is None:
        return
    if not (window_start64 <= moment64 < window_end64):
        return
    tolerance64 = np.timedelta64(max(int(dedupe_tolerance_seconds), 0), 's')
    for seen in seen_moments:
        if np.abs(moment64 - seen) <= tolerance64:
            return
    seen_moments.append(moment64)
    _append_row_with_phase(
        rows=rows,
        location_id=location_id,
        event_type=event_type,
        moment64=moment64,
        event_body='moon',
        event_moon_phase_angle=angle_deg,
    )


# Duplicated from astromath.py for cache generation use.
def calculate_astro_newfullmoon(moment_now, discretize=150):
    moment_now = np.datetime64(moment_now)
    check_period = np.timedelta64(31 * 24 * 60 * 60 * 1000, 'ms')
    step_size = check_period / discretize
    moments_check_array = np.arange(moment_now - check_period / 2, moment_now + check_period / 2, step_size)
    moments_check_astropy = Time(moments_check_array)
    moon_phase_check = astroplan.moon_phase_angle(moments_check_astropy).to_value()
    maxmin = np.diff(np.sign(np.diff(moon_phase_check)))
    newmoon = np.where(maxmin == -2, True, False)
    fullmoon = np.where(maxmin == 2, True, False)

    if newmoon.sum() == 2:
        newmoon1 = np.where(newmoon == True)[0][0] + 1
        newmoon2 = np.where(newmoon == True)[0][1] + 1
        if np.abs(moments_check_array[newmoon1] - moment_now) < np.abs(moments_check_array[newmoon2] - moment_now):
            newmoon[newmoon2 - 1] = False
        elif np.abs(moments_check_array[newmoon2] - moment_now) < np.abs(moments_check_array[newmoon1] - moment_now):
            newmoon[newmoon1 - 1] = False
    if newmoon.sum() == 1:
        newmoon = np.where(newmoon == True)[0][0] + 1
        step_size_new = step_size / (discretize / 2)
        moments_check_array_new = np.arange(
            moments_check_array[newmoon - 1] - step_size_new,
            moments_check_array[newmoon + 1] + step_size_new,
            step_size_new,
        )
        moments_check_astropy = Time(moments_check_array_new)
        moon_phase_check = astroplan.moon_phase_angle(moments_check_astropy).to_value()
        maxmin = np.diff(np.sign(np.diff(moon_phase_check)))
        newmoon = np.where(maxmin <= -1, True, False)
    else:
        newmoon_time = None
        newmoon_angle = None

    if newmoon.sum() == 1:
        newmoon = np.where(newmoon == True)[0][0] + 1
        step_size_new = step_size_new / (discretize / 2)
        moments_check_array_new = np.arange(
            moments_check_array_new[newmoon - 1] - step_size_new,
            moments_check_array_new[newmoon + 1] + step_size_new,
            step_size_new,
        )
        moments_check_astropy = Time(moments_check_array_new)
        moon_phase_check = astroplan.moon_phase_angle(moments_check_astropy).to_value()
        maxmin = np.diff(np.sign(np.diff(moon_phase_check)))
        newmoon = np.where(maxmin <= -1, True, False)
    else:
        newmoon_time = None
        newmoon_angle = None

    if newmoon.sum() == 1:
        newmoon = np.where(newmoon == True)[0][0] + 1
        newmoon_time = np.datetime64(moments_check_array_new[newmoon], 's')
        newmoon_angle = float(moon_phase_check[newmoon] * 180 / math.pi)
    else:
        newmoon_time = None
        newmoon_angle = None

    if fullmoon.sum() == 2:
        fullmoon1 = np.where(fullmoon == True)[0][0] + 1
        fullmoon2 = np.where(fullmoon == True)[0][1] + 1
        if np.abs(moments_check_array[fullmoon1] - moment_now) < np.abs(moments_check_array[fullmoon2] - moment_now):
            fullmoon[fullmoon2 - 1] = False
        elif np.abs(moments_check_array[fullmoon2] - moment_now) < np.abs(moments_check_array[fullmoon1] - moment_now):
            fullmoon[fullmoon1 - 1] = False
    if fullmoon.sum() == 1:
        fullmoon = np.where(fullmoon == True)[0][0] + 1
        step_size_full = step_size / (discretize / 2)
        moments_check_array_full = np.arange(
            moments_check_array[fullmoon - 1] - step_size_full,
            moments_check_array[fullmoon + 1] + step_size_full,
            step_size_full,
        )
        moments_check_astropy = Time(moments_check_array_full)
        moon_phase_check = astroplan.moon_phase_angle(moments_check_astropy).to_value()
        maxmin = np.diff(np.sign(np.diff(moon_phase_check)))
        fullmoon = np.where(maxmin >= 1, True, False)
    else:
        fullmoon_time = None
        fullmoon_angle = None

    if fullmoon.sum() == 1:
        fullmoon = np.where(fullmoon == True)[0][0] + 1
        step_size_full = step_size_full / (discretize / 2)
        moments_check_array_full = np.arange(
            moments_check_array_full[fullmoon - 1] - step_size_full,
            moments_check_array_full[fullmoon + 1] + step_size_full,
            step_size_full,
        )
        moments_check_astropy = Time(moments_check_array_full)
        moon_phase_check = astroplan.moon_phase_angle(moments_check_astropy).to_value()
        maxmin = np.diff(np.sign(np.diff(moon_phase_check)))
        fullmoon = np.where(maxmin >= 1, True, False)
    else:
        fullmoon_time = None
        fullmoon_angle = None

    if fullmoon.sum() == 1:
        fullmoon = np.where(fullmoon == True)[0][0] + 1
        fullmoon_time = np.datetime64(moments_check_array_full[fullmoon], 's')
        fullmoon_angle = float(moon_phase_check[fullmoon] * 180 / math.pi)
    else:
        fullmoon_time = None
        fullmoon_angle = None

    return newmoon_time, newmoon_angle, fullmoon_time, fullmoon_angle


def _generate_newfullmoon_rows(
    rows,
    location_id,
    window_start64,
    window_end64,
    dedupe_tolerance_seconds,
):
    seed64 = window_start64
    newmoon_seen = []
    fullmoon_seen = []
    while seed64 < window_end64:
        newmoon_time, newmoon_angle, fullmoon_time, fullmoon_angle = calculate_astro_newfullmoon(seed64)
        _append_moonphase_event_if_unique(
            rows=rows,
            location_id=location_id,
            event_type='newmoon',
            moment64=newmoon_time,
            angle_deg=newmoon_angle,
            window_start64=window_start64,
            window_end64=window_end64,
            seen_moments=newmoon_seen,
            dedupe_tolerance_seconds=dedupe_tolerance_seconds,
        )
        _append_moonphase_event_if_unique(
            rows=rows,
            location_id=location_id,
            event_type='fullmoon',
            moment64=fullmoon_time,
            angle_deg=fullmoon_angle,
            window_start64=window_start64,
            window_end64=window_end64,
            seen_moments=fullmoon_seen,
            dedupe_tolerance_seconds=dedupe_tolerance_seconds,
        )
        seed64 = seed64 + np.timedelta64(NEWFULL_SEED_STEP_DAYS, 'D')


def _generate_event_type_rows(
    rows,
    observer,
    location_id,
    event_type,
    event_body,
    method_name,
    window_start64,
    window_end64,
    gridpts,
    dedupe_tolerance_seconds=DAILY_EVENT_DUPLICATE_TOLERANCE_SECONDS,
    horizon=None,
):
    tolerance_seconds = max(int(dedupe_tolerance_seconds), 0)
    tolerance64 = np.timedelta64(tolerance_seconds, 's')
    after_event_advance64 = np.timedelta64(AFTER_EVENT_SEED_ADVANCE_HOURS, 'h')
    seed64 = window_start64
    days_span = int((window_end64 - window_start64) / np.timedelta64(1, 'D')) + 1
    max_iterations = max(64, days_span * 3 + MAX_ITERATION_PADDING_DAYS)
    last_kept64 = None

    for _ in range(max_iterations):
        event64 = _get_event_time64(
            observer=observer,
            method_name=method_name,
            seed64=seed64,
            gridpts=gridpts,
            which='next',
            horizon=horizon,
        )

        if event64 is None:
            seed64 = seed64 + np.timedelta64(NO_EVENT_SEED_ADVANCE_DAYS, 'D')
            if seed64 >= window_end64:
                break
            continue

        if event64 >= window_end64:
            break
        if event64 < window_start64:
            seed64 = window_start64
            continue

        if last_kept64 is not None and tolerance_seconds > 0:
            if np.abs(event64 - last_kept64) <= tolerance64:
                seed64 = event64 + after_event_advance64
                continue

        if last_kept64 is not None and event64 <= last_kept64:
            seed64 = last_kept64 + after_event_advance64
            continue

        _append_row(rows, location_id, event_type, event64, event_body)
        last_kept64 = event64
        seed64 = event64 + after_event_advance64


# ----- Daily Event Generation -----
def generate_daily_event_rows(
    location_id,
    location_latlng,
    start_day_utc,
    end_day_utc,
    elevation_msl=0,
    gridpts=150,
    dedupe_tolerance_seconds=DAILY_EVENT_DUPLICATE_TOLERANCE_SECONDS,
):
    observer = _build_observer(location_latlng, elevation_msl=elevation_msl)
    window_start64 = np.datetime64(start_day_utc, 's')
    window_end64 = np.datetime64(end_day_utc, 's')
    rows = []

    for spec in EVENT_SPECS:
        _generate_event_type_rows(
            rows=rows,
            observer=observer,
            location_id=location_id,
            event_type=spec['event_type'],
            event_body=spec['event_body'],
            method_name=spec['method_name'],
            window_start64=window_start64,
            window_end64=window_end64,
            gridpts=gridpts,
            dedupe_tolerance_seconds=dedupe_tolerance_seconds,
            horizon=spec.get('horizon'),
        )

    rows.sort(key=lambda row: (row[2], row[1]))
    return rows


def generate_global_newfullmoon_rows(
    start_day_utc,
    end_day_utc,
    dedupe_tolerance_seconds=DAILY_EVENT_DUPLICATE_TOLERANCE_SECONDS,
):
    window_start64 = np.datetime64(start_day_utc, 's')
    window_end64 = np.datetime64(end_day_utc, 's')
    rows = []
    _generate_newfullmoon_rows(
        rows=rows,
        location_id=None,
        window_start64=window_start64,
        window_end64=window_end64,
        dedupe_tolerance_seconds=dedupe_tolerance_seconds,
    )
    rows.sort(key=lambda row: (row[2], row[1]))
    return rows
