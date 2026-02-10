from datetime import datetime, timedelta
import json
from db import DBsqlstatements
from tv3clock import clockactions
from tv3clock import cache_windows
from core import astromath_cache
from core import formatters


SCHEMA_VERSION = 1
ASTRODATA_REQUEST_LIST = ['sun', 'moon', 'planets', 'stars']
DEFAULT_STARS_MAG_RANK_ALL_MAX = 350


# ----- Location Selection -----
def split_locations_for_nightly_cache():
    location_rows = DBsqlstatements.get_cache_locations_with_photo_counts()

    town_square_without_photos = []
    represented_in_photos = []
    for row in location_rows:
        location = {
            'loc_id': int(row['loc_id']),
            'LocationName': row['LocationName'],
            'LocationType': row['LocationType'],
            'latitude': float(row['CenterLatitude']),
            'longitude': float(row['CenterLongitude']),
            'photo_count': int(row['PhotoCount']),
        }
        if location['LocationType'] == 'town_square' and location['photo_count'] == 0:
            town_square_without_photos.append(location)
        if location['photo_count'] > 0:
            represented_in_photos.append(location)

    return town_square_without_photos, represented_in_photos


# ----- Daily Events -----
def _moment_key(value):
    if isinstance(value, datetime):
        return value.replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
    return str(value).replace('T', ' ')[:19]


def _parse_db_datetime(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace(' ', 'T'))


def get_daily_event_extension_window(location_id, now_utc, target_days=400, min_days_remaining=366):
    max_moment = DBsqlstatements.get_daily_events_max_moment(location_id)
    target_end_day = (now_utc + timedelta(days=target_days)).date()

    if max_moment is None:
        return now_utc.date(), target_end_day

    max_moment_dt = _parse_db_datetime(max_moment)
    days_remaining = (max_moment_dt - now_utc).total_seconds() / 86400.0
    if days_remaining >= min_days_remaining:
        return None, None

    start_day = (max_moment_dt + timedelta(days=1)).date()
    end_day = target_end_day
    if end_day <= start_day:
        end_day = start_day + timedelta(days=30)

    return start_day, end_day


def cache_daily_events_for_location(location, now_utc, logger=None):
    start_day, end_day = get_daily_event_extension_window(location['loc_id'], now_utc)
    if start_day is None:
        return {'rows_inserted': 0, 'start_day': None, 'end_day': None}

    event_rows = astromath_cache.generate_daily_event_rows(
        location_id=location['loc_id'],
        location_latlng=[location['latitude'], location['longitude']],
        start_day_utc=start_day,
        end_day_utc=end_day,
        elevation_msl=0,
        gridpts=150,
    )

    existing_rows = DBsqlstatements.get_existing_daily_event_keys(
        location['loc_id'],
        f'{start_day} 00:00:00',
        f'{end_day} 00:00:00',
    )
    existing_keys = {(row[0], _moment_key(row[1])) for row in existing_rows}
    staged_keys = set()
    rows_to_insert = []
    for row in event_rows:
        key = (row[1], _moment_key(row[2]))
        if key in existing_keys or key in staged_keys:
            continue
        staged_keys.add(key)
        rows_to_insert.append(row)

    DBsqlstatements.insert_cache_daily_events(rows_to_insert)

    if logger:
        logger.log(
            'daily_events_cached',
            location_id=location['loc_id'],
            rows_inserted=len(rows_to_insert),
            start_day=str(start_day),
            end_day=str(end_day),
        )

    return {'rows_inserted': len(rows_to_insert), 'start_day': start_day, 'end_day': end_day}


# ----- Astrodata Chunks -----
def cache_sunmoon_details_for_location(location, window_start_utc, window_end_utc, logger=None):
    moments = cache_windows.build_moments_iso_utc(window_start_utc, window_end_utc, step_seconds=1)
    details = clockactions.get_sunmoon_details(
        [location['latitude'], location['longitude']],
        elevation_msl=0,
        nowmoments_clockstrings=moments,
    )
    payload = json.dumps(details, separators=(',', ':'))
    DBsqlstatements.upsert_cache_astrodata(
        schema_version=SCHEMA_VERSION,
        location_id=location['loc_id'],
        cache_type='sunmoon_details',
        chunk_start_utc=formatters.format_datetime(window_start_utc, 'to string for mysql'),
        step_seconds=1,
        moments_count=len(moments),
        cached_data_json=payload,
    )

    if logger:
        logger.log('sunmoon_details_cached', location_id=location['loc_id'], moments_count=len(moments))

    return {'moments_count': len(moments)}


def cache_astrodata_for_location(location, window_start_utc, window_end_utc, logger=None):
    moments = cache_windows.build_moments_iso_utc(window_start_utc, window_end_utc, step_seconds=180)
    _, astro_dict_lists = clockactions.get_astrodata(
        [location['latitude'], location['longitude']],
        momentsarray=moments,
        requestlist=ASTRODATA_REQUEST_LIST,
        MagRankAllMax=DEFAULT_STARS_MAG_RANK_ALL_MAX,
        LatDec_filter=location['latitude'],
    )
    payload = json.dumps(astro_dict_lists, separators=(',', ':'))
    DBsqlstatements.upsert_cache_astrodata(
        schema_version=SCHEMA_VERSION,
        location_id=location['loc_id'],
        cache_type='astrodata',
        chunk_start_utc=formatters.format_datetime(window_start_utc, 'to string for mysql'),
        step_seconds=180,
        moments_count=len(moments),
        cached_data_json=payload,
    )

    if logger:
        logger.log('astrodata_cached', location_id=location['loc_id'], moments_count=len(moments))

    return {'moments_count': len(moments)}
