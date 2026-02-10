from datetime import timezone
import numpy as np
import astropy.units as u
from astropy.time import Time
import astroplan


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


def _in_day(moment64, day_start64):
    day_end64 = day_start64 + np.timedelta64(1, 'D')
    return day_start64 <= moment64 < day_end64


def _to_mysql_datetime(moment64):
    return np.datetime_as_string(moment64.astype('datetime64[s]'), unit='s').replace('T', ' ')


def _append_row(rows, location_id, event_type, moment64, event_body):
    rows.append((
        int(location_id),
        event_type,
        _to_mysql_datetime(moment64),
        event_body,
        None,
        None,
        None,
    ))


# ----- Daily Event Generation -----
def generate_daily_event_rows(location_id, location_latlng, start_day_utc, end_day_utc, elevation_msl=0, gridpts=150):
    observer = _build_observer(location_latlng, elevation_msl=elevation_msl)
    day_start64 = np.datetime64(start_day_utc, 'D')
    day_end64 = np.datetime64(end_day_utc, 'D')
    days = np.arange(day_start64, day_end64, np.timedelta64(1, 'D'), dtype='datetime64[D]')
    rows = []

    for day64 in days:
        day_time = Time(day64)

        _append_row(rows, location_id, 'midnight', day64.astype('datetime64[s]'), 'sun')

        noon64 = _safe_time64(observer.noon(time=day_time, which='next', n_grid_points=gridpts))
        if noon64 is not None and _in_day(noon64, day64):
            _append_row(rows, location_id, 'noon', noon64, 'sun')

        sunrise64 = _safe_time64(observer.sun_rise_time(time=day_time, which='next', horizon=-0.833 * u.deg, n_grid_points=gridpts))
        if sunrise64 is not None and _in_day(sunrise64, day64):
            _append_row(rows, location_id, 'sunrise', sunrise64, 'sun')

        sunset64 = _safe_time64(observer.sun_set_time(time=day_time, which='next', horizon=-0.833 * u.deg, n_grid_points=gridpts))
        if sunset64 is not None and _in_day(sunset64, day64):
            _append_row(rows, location_id, 'sunset', sunset64, 'sun')

        bmat64 = _safe_time64(observer.sun_rise_time(time=day_time, which='next', horizon=-18 * u.deg, n_grid_points=gridpts))
        if bmat64 is not None and _in_day(bmat64, day64):
            _append_row(rows, location_id, 'bmat', bmat64, 'sun')

        bmnt64 = _safe_time64(observer.sun_rise_time(time=day_time, which='next', horizon=-12 * u.deg, n_grid_points=gridpts))
        if bmnt64 is not None and _in_day(bmnt64, day64):
            _append_row(rows, location_id, 'bmnt', bmnt64, 'sun')

        bmct64 = _safe_time64(observer.sun_rise_time(time=day_time, which='next', horizon=-6 * u.deg, n_grid_points=gridpts))
        if bmct64 is not None and _in_day(bmct64, day64):
            _append_row(rows, location_id, 'bmct', bmct64, 'sun')

        eect64 = _safe_time64(observer.sun_set_time(time=day_time, which='next', horizon=-6 * u.deg, n_grid_points=gridpts))
        if eect64 is not None and _in_day(eect64, day64):
            _append_row(rows, location_id, 'eect', eect64, 'sun')

        eent64 = _safe_time64(observer.sun_set_time(time=day_time, which='next', horizon=-12 * u.deg, n_grid_points=gridpts))
        if eent64 is not None and _in_day(eent64, day64):
            _append_row(rows, location_id, 'eent', eent64, 'sun')

        eeat64 = _safe_time64(observer.sun_set_time(time=day_time, which='next', horizon=-18 * u.deg, n_grid_points=gridpts))
        if eeat64 is not None and _in_day(eeat64, day64):
            _append_row(rows, location_id, 'eeat', eeat64, 'sun')

        riseplus6_64 = _safe_time64(observer.sun_rise_time(time=day_time, which='next', horizon=6 * u.deg, n_grid_points=gridpts))
        if riseplus6_64 is not None and _in_day(riseplus6_64, day64):
            _append_row(rows, location_id, 'riseplus6deg', riseplus6_64, 'sun')

        setminus6_64 = _safe_time64(observer.sun_set_time(time=day_time, which='next', horizon=6 * u.deg, n_grid_points=gridpts))
        if setminus6_64 is not None and _in_day(setminus6_64, day64):
            _append_row(rows, location_id, 'setminus6deg', setminus6_64, 'sun')

        moonrise64 = _safe_time64(observer.moon_rise_time(time=day_time, which='next', horizon=0 * u.deg, n_grid_points=gridpts))
        if moonrise64 is not None and _in_day(moonrise64, day64):
            _append_row(rows, location_id, 'moonrise', moonrise64, 'moon')

        moonset64 = _safe_time64(observer.moon_set_time(time=day_time, which='next', horizon=0 * u.deg, n_grid_points=gridpts))
        if moonset64 is not None and _in_day(moonset64, day64):
            _append_row(rows, location_id, 'moonset', moonset64, 'moon')

    return rows
