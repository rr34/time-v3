from datetime import datetime, timedelta
from bisect import bisect_left, insort
import json
from db import DBsqlstatements
from tv3clock import clockactions
from tv3clock import cache_windows
from core import astromath_cache
from core import formatters


SCHEMA_VERSION = 1
ASTRODATA_REQUEST_LIST = ['sun', 'moon', 'planets', 'stars']
DEFAULT_STARS_MAG_RANK_ALL_MAX = 350
DAILY_EVENT_TYPES = [spec['event_type'] for spec in astromath_cache.EVENT_SPECS]


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
def _parse_db_datetime(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace(' ', 'T'))


def _moment_mysql_seconds(value):
    moment_dt = _parse_db_datetime(value)
    if moment_dt is None:
        return None
    return moment_dt.replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S')


def _build_event_time_index(existing_rows):
    event_time_index = {}
    for event_type, moment in existing_rows:
        moment_dt = _parse_db_datetime(moment)
        if moment_dt is None:
            continue
        event_time_index.setdefault(event_type, []).append(moment_dt.replace(microsecond=0))

    for event_type in event_time_index:
        event_time_index[event_type].sort()

    return event_time_index


def _has_event_within_tolerance(sorted_event_times, moment_dt, tolerance_seconds):
    if not sorted_event_times:
        return False

    tolerance = timedelta(seconds=tolerance_seconds)
    pos = bisect_left(sorted_event_times, moment_dt)
    if pos < len(sorted_event_times):
        if abs(sorted_event_times[pos] - moment_dt) <= tolerance:
            return True
    if pos > 0:
        if abs(moment_dt - sorted_event_times[pos - 1]) <= tolerance:
            return True
    return False


def get_daily_event_extension_window(location_id, now_utc, target_days=400, min_days_remaining=366):
    target_end_day = (now_utc + timedelta(days=target_days)).date()
    backfill_start_day = now_utc.date() - timedelta(days=1)

    max_rows = DBsqlstatements.get_daily_events_max_moments_by_event_type(location_id, DAILY_EVENT_TYPES)
    max_by_event_type = {
        row['EventType']: _parse_db_datetime(row['MaxMomentEvent'])
        for row in max_rows
        if row.get('MaxMomentEvent') is not None
    }

    if len(max_by_event_type) < len(DAILY_EVENT_TYPES):
        return backfill_start_day, target_end_day

    earliest_max_moment = min(max_by_event_type.values())
    days_remaining = (earliest_max_moment - now_utc).total_seconds() / 86400.0
    if days_remaining >= min_days_remaining:
        return None, None

    start_day = (earliest_max_moment + timedelta(days=1)).date()
    if start_day > target_end_day:
        start_day = backfill_start_day
    end_day = target_end_day
    if end_day <= start_day:
        end_day = start_day + timedelta(days=30)

    return start_day, end_day


def get_global_newfullmoon_extension_window(now_utc, target_days=400, min_days_remaining=366):
    max_moment = DBsqlstatements.get_global_newfullmoon_max_moment()
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


def get_location_newfullmoon_extension_window(location_id, now_utc, target_days=400, min_days_remaining=366):
    max_moment = DBsqlstatements.get_location_newfullmoon_max_moment(location_id)
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


def cache_global_newfullmoon_events(now_utc, logger=None):
    start_day, end_day = get_global_newfullmoon_extension_window(now_utc)
    if start_day is None:
        return {'rows_inserted': 0, 'start_day': None, 'end_day': None}

    event_rows = astromath_cache.generate_global_newfullmoon_rows(
        start_day_utc=start_day,
        end_day_utc=end_day,
        dedupe_tolerance_seconds=astromath_cache.DAILY_EVENT_DUPLICATE_TOLERANCE_SECONDS,
    )

    existing_rows = DBsqlstatements.get_existing_global_newfullmoon_keys(
        f'{start_day} 00:00:00',
        f'{end_day} 00:00:00',
    )
    existing_time_index = _build_event_time_index(existing_rows)
    staged_time_index = {}
    rows_to_insert = []
    for row in event_rows:
        event_type = row[1]
        moment_dt = _parse_db_datetime(row[2])
        if moment_dt is None:
            continue
        moment_dt = moment_dt.replace(microsecond=0)

        if _has_event_within_tolerance(
            existing_time_index.get(event_type, []),
            moment_dt,
            astromath_cache.DAILY_EVENT_DUPLICATE_TOLERANCE_SECONDS,
        ):
            continue

        staged_times = staged_time_index.setdefault(event_type, [])
        if _has_event_within_tolerance(
            staged_times,
            moment_dt,
            astromath_cache.DAILY_EVENT_DUPLICATE_TOLERANCE_SECONDS,
        ):
            continue

        insort(staged_times, moment_dt)
        rows_to_insert.append(row)

    DBsqlstatements.insert_cache_daily_events(rows_to_insert)

    if logger:
        logger.log(
            'global_newfullmoon_cached',
            rows_inserted=len(rows_to_insert),
            start_day=str(start_day),
            end_day=str(end_day),
        )

    return {'rows_inserted': len(rows_to_insert), 'start_day': start_day, 'end_day': end_day}


def cache_location_newfullmoon_events_for_location(location, now_utc, logger=None):
    start_day, end_day = get_location_newfullmoon_extension_window(location['loc_id'], now_utc)
    if start_day is None:
        return {'rows_inserted': 0, 'start_day': None, 'end_day': None}

    global_rows = DBsqlstatements.get_global_newfullmoon_rows(
        f'{start_day} 00:00:00',
        f'{end_day} 00:00:00',
    )
    if not global_rows:
        if logger:
            logger.log(
                'location_newfullmoon_replicated',
                location_id=location['loc_id'],
                rows_inserted=0,
                start_day=str(start_day),
                end_day=str(end_day),
            )
        return {'rows_inserted': 0, 'start_day': start_day, 'end_day': end_day}

    existing_rows = DBsqlstatements.get_existing_location_newfullmoon_keys(
        location['loc_id'],
        f'{start_day} 00:00:00',
        f'{end_day} 00:00:00',
    )
    existing_time_index = _build_event_time_index(existing_rows)
    staged_time_index = {}
    rows_to_insert = []
    for global_row in global_rows:
        event_type, moment_value, event_body, moon_phase_angle = global_row
        moment_dt = _parse_db_datetime(moment_value)
        if moment_dt is None:
            continue
        moment_dt = moment_dt.replace(microsecond=0)

        if _has_event_within_tolerance(
            existing_time_index.get(event_type, []),
            moment_dt,
            astromath_cache.DAILY_EVENT_DUPLICATE_TOLERANCE_SECONDS,
        ):
            continue

        staged_times = staged_time_index.setdefault(event_type, [])
        if _has_event_within_tolerance(
            staged_times,
            moment_dt,
            astromath_cache.DAILY_EVENT_DUPLICATE_TOLERANCE_SECONDS,
        ):
            continue

        insort(staged_times, moment_dt)
        rows_to_insert.append((
            int(location['loc_id']),
            event_type,
            moment_dt.strftime('%Y-%m-%d %H:%M:%S'),
            event_body,
            None,
            None,
            None if moon_phase_angle is None else float(moon_phase_angle),
        ))

    DBsqlstatements.insert_cache_daily_events(rows_to_insert)

    if logger:
        logger.log(
            'location_newfullmoon_replicated',
            location_id=location['loc_id'],
            rows_inserted=len(rows_to_insert),
            start_day=str(start_day),
            end_day=str(end_day),
        )

    return {'rows_inserted': len(rows_to_insert), 'start_day': start_day, 'end_day': end_day}


def cache_global_newfullmoon_details(logger=None):
    missing_rows = DBsqlstatements.get_global_newfullmoon_missing_fields()
    if not missing_rows:
        if logger:
            logger.log('global_newfullmoon_details_cached', rows_updated=0, moments_count=0)
        return {'rows_updated': 0, 'moments_count': 0}

    global_locations = DBsqlstatements.get_primary_location_center(location_type='town_square')
    if not global_locations:
        if logger:
            logger.log('global_newfullmoon_details_skipped', reason='no_town_square_reference_location')
        return {'rows_updated': 0, 'moments_count': 0}

    global_location = global_locations[0]
    latitude = float(global_location['CenterLatitude'])
    longitude = float(global_location['CenterLongitude'])

    moments = []
    for row in missing_rows:
        moment_str = _moment_mysql_seconds(row.get('MomentEvent'))
        if moment_str is not None:
            moments.append(moment_str)
    unique_moments = sorted(set(moments))
    if not unique_moments:
        if logger:
            logger.log('global_newfullmoon_details_cached', rows_updated=0, moments_count=0)
        return {'rows_updated': 0, 'moments_count': 0}

    bodies_astro_dict, _ = clockactions.get_astrodata(
        [latitude, longitude],
        momentsarray=unique_moments,
        requestlist=['moon'],
        MagRankAllMax=DEFAULT_STARS_MAG_RANK_ALL_MAX,
        LatDec_filter=latitude,
        use_cache=False,
    )
    moon_data = bodies_astro_dict['moon']
    moment_index = {moment: idx for idx, moment in enumerate(unique_moments)}

    update_rows = []
    for row in missing_rows:
        event_id = row.get('event_id')
        moment_str = _moment_mysql_seconds(row.get('MomentEvent'))
        if event_id is None or moment_str is None:
            continue
        idx = moment_index.get(moment_str)
        if idx is None:
            continue
        azimuth = float(moon_data['azimuths'][idx])
        artifae = float(moon_data['artifaes'][idx])
        phase_angle = float(moon_data['moonphaseangles'][idx])
        update_rows.append((azimuth, artifae, phase_angle, int(event_id)))

    DBsqlstatements.update_daily_events_azart_phase(update_rows)

    if logger:
        logger.log(
            'global_newfullmoon_details_cached',
            reference_location_id=int(global_location['loc_id']),
            rows_missing=len(missing_rows),
            rows_updated=len(update_rows),
            moments_count=len(unique_moments),
        )

    return {'rows_updated': len(update_rows), 'moments_count': len(unique_moments)}


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
        dedupe_tolerance_seconds=astromath_cache.DAILY_EVENT_DUPLICATE_TOLERANCE_SECONDS,
    )

    existing_rows = DBsqlstatements.get_existing_daily_event_keys(
        location['loc_id'],
        f'{start_day} 00:00:00',
        f'{end_day} 00:00:00',
    )
    existing_time_index = _build_event_time_index(existing_rows)
    staged_time_index = {}
    rows_to_insert = []
    for row in event_rows:
        event_type = row[1]
        moment_dt = _parse_db_datetime(row[2])
        if moment_dt is None:
            continue
        moment_dt = moment_dt.replace(microsecond=0)

        if _has_event_within_tolerance(
            existing_time_index.get(event_type, []),
            moment_dt,
            astromath_cache.DAILY_EVENT_DUPLICATE_TOLERANCE_SECONDS,
        ):
            continue

        staged_times = staged_time_index.setdefault(event_type, [])
        if _has_event_within_tolerance(
            staged_times,
            moment_dt,
            astromath_cache.DAILY_EVENT_DUPLICATE_TOLERANCE_SECONDS,
        ):
            continue

        insort(staged_times, moment_dt)
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


def cache_daily_event_azart_for_location(location, logger=None):
    missing_rows = DBsqlstatements.get_daily_events_missing_azart(location['loc_id'])
    if not missing_rows:
        if logger:
            logger.log('daily_event_azart_cached', location_id=location['loc_id'], rows_updated=0, moments_count=0)
        return {'rows_updated': 0, 'moments_count': 0}

    rows_by_body = {'sun': [], 'moon': []}
    for row in missing_rows:
        event_body = row.get('EventBody')
        moment_str = _moment_mysql_seconds(row.get('MomentEvent'))
        if event_body in ('sun', 'moon') and moment_str is not None:
            rows_by_body[event_body].append((row, moment_str))

    if not rows_by_body['sun'] and not rows_by_body['moon']:
        if logger:
            logger.log('daily_event_azart_cached', location_id=location['loc_id'], rows_updated=0, moments_count=0)
        return {'rows_updated': 0, 'moments_count': 0}

    azart_lookup = {'sun': {}, 'moon': {}}
    moments_count = 0
    for event_body in ('sun', 'moon'):
        if not rows_by_body[event_body]:
            continue
        body_unique_moments = sorted({moment_str for _, moment_str in rows_by_body[event_body]})
        moments_count += len(body_unique_moments)
        bodies_astro_dict, _ = clockactions.get_astrodata(
            [location['latitude'], location['longitude']],
            momentsarray=body_unique_moments,
            requestlist=[event_body],
            MagRankAllMax=DEFAULT_STARS_MAG_RANK_ALL_MAX,
            LatDec_filter=location['latitude'],
            use_cache=False,
        )
        azimuths = bodies_astro_dict[event_body]['azimuths']
        artifaes = bodies_astro_dict[event_body]['artifaes']
        for idx, moment_str in enumerate(body_unique_moments):
            azart_lookup[event_body][moment_str] = (float(azimuths[idx]), float(artifaes[idx]))

    update_rows = []
    for event_body in ('sun', 'moon'):
        for row, moment_str in rows_by_body[event_body]:
            event_id = row.get('event_id')
            azart = azart_lookup[event_body].get(moment_str)
            if event_id is None or azart is None:
                continue
            update_rows.append((azart[0], azart[1], int(event_id)))

    DBsqlstatements.update_daily_events_azart(update_rows)

    if logger:
        logger.log(
            'daily_event_azart_cached',
            location_id=location['loc_id'],
            rows_missing=len(missing_rows),
            rows_updated=len(update_rows),
            moments_count=moments_count,
        )

    return {'rows_updated': len(update_rows), 'moments_count': moments_count}


# ----- Astrodata Chunks -----
def cache_sunmoon_details_for_location(location, window_start_utc, window_end_utc, logger=None):
    moments = cache_windows.build_moments_iso_utc(window_start_utc, window_end_utc, step_seconds=1)
    details = clockactions.get_sunmoon_details(
        [location['latitude'], location['longitude']],
        elevation_msl=0,
        nowmoments_clockstrings=moments,
        use_cache=False,
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
        use_cache=False,
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
