import numpy as np
import json
import math
from db import DBsqlstatements
from core import formatters
from core import astromath
from core import awimlib


SCHEMA_VERSION = 1
CACHE_LOCATION_MAX_DISTANCE_M = 10000.0
DEFAULT_STARS_MAG_RANK_ALL_MAX = 350
ASTRODATA_REQUEST_LIST = ['sun', 'moon', 'planets', 'stars']


# ----- Cache helpers -----
def _to_datetime64_seconds(value):
    if isinstance(value, str):
        normalized = value.strip()
        if normalized.endswith('Z'):
            normalized = normalized[:-1]
        return np.datetime64(normalized, 's')
    return np.datetime64(value, 's')


def _to_mysql_datetime_string(value):
    return formatters.format_datetime(_to_datetime64_seconds(value), 'to string for mysql')


def _to_awim_datetime_string(value):
    return formatters.format_datetime(_to_datetime64_seconds(value), 'to string for AWIMtag')


def _haversine_m(lat1, lon1, lat2, lon2):
    earth_radius_m = 6371000.0
    lat1_rad = math.radians(float(lat1))
    lon1_rad = math.radians(float(lon1))
    lat2_rad = math.radians(float(lat2))
    lon2_rad = math.radians(float(lon2))
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    return earth_radius_m * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _get_nearest_cache_location(location, max_distance_m=CACHE_LOCATION_MAX_DISTANCE_M):
    if location is None or len(location) < 2:
        return None

    rows = DBsqlstatements.get_cache_locations_with_photo_counts()
    nearest = None
    nearest_distance = None
    for row in rows:
        distance_m = _haversine_m(
            location[0],
            location[1],
            row['CenterLatitude'],
            row['CenterLongitude'],
        )
        if nearest_distance is None or distance_m < nearest_distance:
            nearest = row
            nearest_distance = distance_m

    if nearest is None or nearest_distance is None:
        return None
    if nearest_distance > max_distance_m:
        return None

    return {
        'loc_id': int(nearest['loc_id']),
        'latitude': float(nearest['CenterLatitude']),
        'longitude': float(nearest['CenterLongitude']),
        'distance_m': nearest_distance,
    }


def _row_moment64(row):
    return _to_datetime64_seconds(row['MomentEvent'])


def _index_rows_by_event_type(rows):
    indexed = {}
    for row in rows:
        indexed.setdefault(row['EventType'], []).append(row)
    for event_type in indexed:
        indexed[event_type].sort(key=_row_moment64)
    return indexed


def _latest_row_at_or_before(rows, moment64):
    matches = [row for row in rows if _row_moment64(row) <= moment64]
    return matches[-1] if matches else None


def _next_row_after(rows, moment64):
    for row in rows:
        if _row_moment64(row) > moment64:
            return row
    return None


def _event_data_from_rows(rows, body_type, readable_name):
    azimuths = []
    artifaes = []
    for row in rows:
        if row is None or row.get('EventAzimuth') is None or row.get('EventArtifae') is None:
            return None
        azimuths.append(float(row['EventAzimuth']))
        artifaes.append(float(row['EventArtifae']))

    return {
        'type': body_type,
        'ReadableName': readable_name,
        'azimuths': formatters.round_numbers(azimuths, 'azimuths'),
        'artifaes': formatters.round_numbers(artifaes, 'artifaes'),
    }


def _build_cached_sun_daily(indexed_rows, currenttime64):
    sunrises = indexed_rows.get('sunrise', [])
    noons = indexed_rows.get('noon', [])
    sunsets = indexed_rows.get('sunset', [])
    midnights = indexed_rows.get('midnight', [])
    if not sunrises or not noons or not sunsets or not midnights:
        return None, None

    first_midnight = _latest_row_at_or_before(midnights, currenttime64)
    if first_midnight is None:
        return None, None

    first_midnight64 = _row_moment64(first_midnight)
    first_sunrise = _latest_row_at_or_before(sunrises, first_midnight64)
    if first_sunrise is None:
        return None, None

    rows = [first_sunrise]
    rows.append(_next_row_after(noons, _row_moment64(rows[-1])))
    rows.append(_next_row_after(sunsets, _row_moment64(rows[-1])))
    rows.append(first_midnight)
    rows.append(_next_row_after(sunrises, _row_moment64(rows[-1])))
    rows.append(_next_row_after(noons, _row_moment64(rows[-1])))
    rows.append(_next_row_after(sunsets, _row_moment64(rows[-1])))
    rows.append(_next_row_after(midnights, _row_moment64(rows[-1])))
    rows.append(_next_row_after(sunrises, _row_moment64(rows[-1])))
    rows.append(_next_row_after(noons, _row_moment64(rows[-1])))
    rows.append(_next_row_after(sunsets, _row_moment64(rows[-1])))
    rows.append(_next_row_after(midnights, _row_moment64(rows[-1])))
    rows.append(_next_row_after(sunrises, _row_moment64(rows[-1])))

    if any(row is None for row in rows):
        return None, None
    return rows, _event_data_from_rows(rows, 'sun', 'Sun')


def _build_cached_moon_daily(indexed_rows, currenttime64):
    moonrises = indexed_rows.get('moonrise', [])
    moonsets = indexed_rows.get('moonset', [])
    if not moonrises or not moonsets:
        return None, None

    first_moonset = _latest_row_at_or_before(moonsets, currenttime64)
    if first_moonset is None:
        return None, None

    first_moonrise = _latest_row_at_or_before(moonrises, _row_moment64(first_moonset))
    if first_moonrise is None:
        return None, None

    rows = [first_moonrise, first_moonset]
    rows.append(_next_row_after(moonrises, _row_moment64(rows[-1])))
    rows.append(_next_row_after(moonsets, _row_moment64(rows[-1])))
    rows.append(_next_row_after(moonrises, _row_moment64(rows[-1])))
    rows.append(_next_row_after(moonsets, _row_moment64(rows[-1])))

    if any(row is None for row in rows):
        return None, None
    return rows, _event_data_from_rows(rows, 'moon', 'Moon')


def _nearest_event_row(rows, event_type, currenttime64):
    event_rows = [row for row in rows if row['EventType'] == event_type]
    if not event_rows:
        return None
    return min(event_rows, key=lambda row: abs(_row_moment64(row) - currenttime64))


def _get_events_from_cache(location, currenttime):
    cache_location = _get_nearest_cache_location(location)
    if cache_location is None:
        return None

    currenttime64 = _to_datetime64_seconds(currenttime)
    start_moment = _to_mysql_datetime_string(currenttime64 - np.timedelta64(45, 'D'))
    end_moment = _to_mysql_datetime_string(currenttime64 + np.timedelta64(45, 'D'))
    rows = DBsqlstatements.get_cached_daily_events(
        cache_location['loc_id'],
        start_moment,
        end_moment,
        event_types=[
            'sunrise',
            'sunset',
            'noon',
            'midnight',
            'moonrise',
            'moonset',
            'newmoon',
            'fullmoon',
        ],
    )
    if not rows:
        return None

    indexed_rows = _index_rows_by_event_type(rows)
    sun_rows, sundata = _build_cached_sun_daily(indexed_rows, currenttime64)
    moon_rows, moondata = _build_cached_moon_daily(indexed_rows, currenttime64)
    nearest_new = _nearest_event_row(rows, 'newmoon', currenttime64)
    nearest_full = _nearest_event_row(rows, 'fullmoon', currenttime64)

    if sun_rows is None or sundata is None:
        return None
    if moon_rows is None or moondata is None:
        return None
    if nearest_new is None or nearest_full is None:
        return None
    if nearest_new.get('EventMoonPhaseAngle') is None or nearest_full.get('EventMoonPhaseAngle') is None:
        return None

    return {
        'sundaily': [_to_awim_datetime_string(row['MomentEvent']) for row in sun_rows],
        'sundailydata': sundata,
        'moondaily': [_to_awim_datetime_string(row['MomentEvent']) for row in moon_rows],
        'moondailydata': moondata,
        'newmoon time': _to_awim_datetime_string(nearest_new['MomentEvent']),
        'newmoon angle': str(float(nearest_new['EventMoonPhaseAngle'])),
        'fullmoon time': _to_awim_datetime_string(nearest_full['MomentEvent']),
        'fullmoon angle': str(float(nearest_full['EventMoonPhaseAngle'])),
    }


def _slice_cached_body_data(cached_data, indices, moments_count):
    sliced = {}
    for body_key, body_value in cached_data.items():
        if not isinstance(body_value, dict):
            sliced[body_key] = body_value
            continue

        sliced_body = {}
        for key, value in body_value.items():
            if isinstance(value, list) and len(value) == moments_count:
                sliced_body[key] = [value[idx] for idx in indices]
            else:
                sliced_body[key] = value
        sliced[body_key] = sliced_body

    return sliced


def _get_astrodata_cache_slice(location, momentsarray, cache_type):
    if not momentsarray:
        return None

    cache_location = _get_nearest_cache_location(location)
    if cache_location is None:
        return None

    moments64 = np.array([_to_datetime64_seconds(moment) for moment in momentsarray])
    start_moment = _to_mysql_datetime_string(moments64.min())
    end_moment = _to_mysql_datetime_string(moments64.max())
    chunk = DBsqlstatements.get_cached_astrodata_chunk(
        cache_location['loc_id'],
        cache_type,
        start_moment,
        end_moment,
        schema_version=SCHEMA_VERSION,
    )
    if chunk is None or not chunk.get('CachedData'):
        return None

    chunk_start64 = _to_datetime64_seconds(chunk['ChunkStartUTC'])
    step_seconds = int(chunk['StepSeconds'])
    moments_count = int(chunk['MomentsCount'])
    indices = []
    for moment64 in moments64:
        offset_seconds = int((moment64 - chunk_start64) / np.timedelta64(1, 's'))
        if offset_seconds < 0 or offset_seconds % step_seconds != 0:
            return None
        idx = offset_seconds // step_seconds
        if idx < 0 or idx >= moments_count:
            return None
        indices.append(idx)

    cached_data = json.loads(chunk['CachedData'])
    return _slice_cached_body_data(cached_data, indices, moments_count)


# ----- Clock API actions -----
def get_events(location, elevation_msl, currenttime, use_cache=True):
    if use_cache:
        cached_response = _get_events_from_cache(location, currenttime)
        if cached_response is not None:
            return cached_response

    return _calculate_events(location, elevation_msl, currenttime)


def _calculate_events(location, elevation_msl, currenttime):
    currenttime = np.datetime64(currenttime)
    sundaily, moondaily = astromath.calculate_astro_risesandsets(location, currenttime, elevation_msl)

    justsundict = {'sun': {'type': 'sun', 'ReadableName': 'Sun'}}
    sundata = astromath.calculate_astro_data(sundaily, location, justsundict)['sun']
    sundata['azimuths'] = formatters.round_numbers(sundata['azimuths'], 'azimuths')
    sundata['artifaes'] = formatters.round_numbers(sundata['artifaes'], 'artifaes')
    sundata = formatters.dict_arrays_tolists(sundata)

    justmoondict = {'moon': {'type': 'moon', 'ReadableName': 'Moon'}}
    moondata = astromath.calculate_astro_data(moondaily, location, justmoondict)['moon']
    moondata['azimuths'] = formatters.round_numbers(moondata['azimuths'], 'azimuths')
    moondata['artifaes'] = formatters.round_numbers(moondata['artifaes'], 'artifaes')
    moondata = formatters.dict_arrays_tolists(moondata)

    newmoon_time, newmoon_angle, fullmoon_time, fullmoon_angle = astromath.calculate_astro_newfullmoon(currenttime)
    response_dict = {}
    response_dict['sundaily'] = formatters.format_datetime(sundaily, 'to string for AWIMtag')
    response_dict['sundailydata'] = sundata
    response_dict['moondaily'] = formatters.format_datetime(moondaily, 'to string for AWIMtag')
    response_dict['moondailydata'] = moondata
    response_dict['newmoon time'] = formatters.format_datetime(newmoon_time, 'to string for AWIMtag')
    response_dict['newmoon angle'] = str(newmoon_angle)
    response_dict['fullmoon time'] = formatters.format_datetime(fullmoon_time, 'to string for AWIMtag')
    response_dict['fullmoon angle'] = str(fullmoon_angle)

    return response_dict


def _can_use_cached_astrodata(requestlist, MagRankAllMax, LatDec_filter, location):
    if int(MagRankAllMax) != DEFAULT_STARS_MAG_RANK_ALL_MAX:
        return False
    if set(requestlist) - set(ASTRODATA_REQUEST_LIST):
        return False
    if 'stars' in requestlist and LatDec_filter != location[0]:
        return False
    return True


def get_astrodata(location, momentsarray, requestlist, MagRankAllMax, LatDec_filter, use_cache=True):
    if use_cache and _can_use_cached_astrodata(requestlist, MagRankAllMax, LatDec_filter, location):
        cached_astrodata = _get_astrodata_cache_slice(location, momentsarray, cache_type='astrodata')
        if cached_astrodata is not None:
            return cached_astrodata, cached_astrodata

    return _calculate_astrodata(location, momentsarray, requestlist, MagRankAllMax, LatDec_filter)


def _calculate_astrodata(location, momentsarray, requestlist, MagRankAllMax, LatDec_filter):
    momentsarray = np.array([np.datetime64(moment) for moment in momentsarray])
    bodies_astro_dict = {}
    # The following loop just creates the expanded list of bodies. Within solar system just get a name because RA, Dec has to be calculated. Outside solar system (stars) are a tuple of name with the RA, Dec given.
    for request in requestlist:
        if request == 'sun':
            bodies_astro_dict['sun'] = {'type': 'sun', 'ReadableName': 'Sun'}
        elif request == 'moon':
            bodies_astro_dict['moon'] = {'type': 'moon', 'ReadableName': 'Moon'}
        elif request == 'planets':
            planetslist = ['mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
            for planet in planetslist:
                bodies_astro_dict[planet] = {'type': 'planet', 'ReadableName': planet.capitalize()}
        elif request == 'stars':
            stars_tuples = DBsqlstatements.get_stars(MagRankAllMax, LatDec_filter=LatDec_filter)
            for star in stars_tuples:
                bodies_astro_dict['HR ' + str(star[0])] = {
                'type': 'star', # string
                'ReadableName': star[1],
                'RA': star[2], # number
                'Declination': star[3], # number
                'Distance': star[4], # number
                'VisualMagnitude': star[5], # number
                'MagRankAll': star[6], # number
                'ConstellationFullName': star[7], # string
                'MagRankConstellation': star[8], # number
                'GreekLetter': star[9], # string
                }

    # astro data function generates a dictionary within it because it uses the common location and times for calculation efficiency
    bodies_astro_dict = astromath.calculate_astro_data(momentsarray, location, bodies_astro_dict)

    bodies_astro_dict_lists = formatters.dict_arrays_tolists(bodies_astro_dict)

    return bodies_astro_dict, bodies_astro_dict_lists


def get_celestialinphoto(awim_dict, momentsarray, bodies_astro_dict, inimage_threshold=2, padding_percent=5):
    # bodies in the image dictionary generated here, not inside awimlib, because there is no commonality among the bodies in image for efficiency
    # bodies in the image dictionary has same keys as the astro_dict, but fewer because only includes bodies that pass through the image.
    bodies_image_dict = {}
    for key, value in bodies_astro_dict.items():
        # azart_to_dirarc here?
        body_azarts = np.column_stack((value['azimuths'], value['artifaes']))
        body_xyangs = awimlib.azarts_to_xyangs(awim_dict, body_azarts) # with dirarc, xyangs are just an intermediary, but still necessary and still useful for determining if body is in image.
        body_inimage = awimlib.xyangs_inimage(awim_dict, body_xyangs, padding_percent=padding_percent)
        if body_inimage.sum() >= inimage_threshold:
            bodies_image_dict[key] = {}
            body_dirarcs = awimlib.xyangs_to_dirarcs(body_xyangs) # dirarcs are useful because possible to correct for tilt. Are they otherwise necessary?
            body_pxs = awimlib.xyangs_to_pxs(awim_dict, body_xyangs, 'for svg') # convert this calculation to dirarcs_to_pixels because more versatile and can implement tilt.

            bodies_image_dict[key]['xangs'] = body_xyangs[:,0]
            bodies_image_dict[key]['yangs'] = body_xyangs[:,1]
            bodies_image_dict[key]['dirs'] = body_dirarcs[:,0]
            bodies_image_dict[key]['arcs'] = body_dirarcs[:,1]
            bodies_image_dict[key]['pixelpos x'] = body_pxs[:,0]
            bodies_image_dict[key]['pixelpos y'] = body_pxs[:,1]
            for astrokey, astrovalue in bodies_astro_dict[key].items():
                bodies_image_dict[key][astrokey] = astrovalue

            if key == 'moon':
                phase_angles = astromath.calculate_astro_moonphaseangle(momentsarray)
                bodies_image_dict[key]['phaseangles'] = phase_angles
                sun_azarts = np.column_stack((bodies_astro_dict['sun']['azimuths'], bodies_astro_dict['sun']['artifaes']))
                brightside_directions = astromath.calculate_astro_moon_brightsidedirection(body_azarts, sun_azarts)
                bodies_image_dict[key]['brightsidedirections'] = brightside_directions
    
    bodies_total = len(bodies_astro_dict)
    bodiescount_inimage = len(bodies_image_dict)
    print(f'{bodies_total} total bodies, {bodiescount_inimage} bodies in image during period, so {round(bodiescount_inimage/bodies_total * 100, 2)} percent of total passed through image during period.')

    bodies_image_dict_lists = formatters.dict_arrays_tolists(bodies_image_dict)

    return bodies_image_dict_lists


def get_sunmoon_details(location, elevation_msl, nowmoments_clockstrings, use_cache=True):
    if use_cache:
        cached_sunmoon_details = _get_astrodata_cache_slice(
            location,
            nowmoments_clockstrings,
            cache_type='sunmoon_details',
        )
        if cached_sunmoon_details is not None:
            return cached_sunmoon_details

    return _calculate_sunmoon_details(location, elevation_msl, nowmoments_clockstrings)


def _calculate_sunmoon_details(location, elevation_msl, nowmoments_clockstrings):
    momentsarray = np.array([np.datetime64(moment) for moment in nowmoments_clockstrings])
    sunmoondict = {'sun': {'type': 'sun', 'ReadableName': 'Sun'}, 'moon': {'type': 'moon', 'ReadableName': 'Moon'}}

    sunmoon_details = astromath.calculate_astro_data(momentsarray, location, sunmoondict)
    sunmoon_details['sun']['azimuths'] = formatters.round_numbers(sunmoon_details['sun']['azimuths'], 'degrees')
    sunmoon_details['sun']['artifaes'] = formatters.round_numbers(sunmoon_details['sun']['artifaes'], 'degrees')
    sunmoon_details['moon']['azimuths'] = formatters.round_numbers(sunmoon_details['moon']['azimuths'], 'degrees')
    sunmoon_details['moon']['artifaes'] = formatters.round_numbers(sunmoon_details['moon']['artifaes'], 'degrees')
    sunmoon_details['moon']['moonphaseangles'] = formatters.round_numbers(sunmoon_details['moon']['moonphaseangles'], 'degrees')
    sunmoon_details = formatters.dict_arrays_tolists(sunmoon_details)

    return sunmoon_details

def _get_glockenspiel_event_moments_from_cache(location, currenttime, event_type, count, offset_minutes, window_days):
    cache_location = _get_nearest_cache_location(location)
    if cache_location is None:
        return None

    currenttime64 = _to_datetime64_seconds(currenttime)
    start_moment = _to_mysql_datetime_string(currenttime64)
    end_moment = _to_mysql_datetime_string(currenttime64 + np.timedelta64(window_days, 'D'))
    rows = DBsqlstatements.get_cached_daily_events(
        cache_location['loc_id'],
        start_moment,
        end_moment,
        event_types=[event_type],
    )
    if len(rows) < count:
        return None

    offset = np.timedelta64(int(offset_minutes), 'm')
    moments = [_to_datetime64_seconds(row['MomentEvent']) + offset for row in rows[:count]]
    return [_to_awim_datetime_string(moment) for moment in moments]


# glockenspiel: next 30 moonrises (event-based), starting now; offset +2 hours
def get_glockenspiel_moonrise_month(location, elevation_msl, currenttime, count=30, gridpts=50, use_cache=True):
    if use_cache:
        cached_moments = _get_glockenspiel_event_moments_from_cache(
            location,
            currenttime,
            event_type='moonrise',
            count=count,
            offset_minutes=120,
            window_days=90,
        )
        if cached_moments is not None:
            return cached_moments

    currenttime = np.datetime64(currenttime)
    start_time = currenttime

    moonrises = astromath.calculate_astro_moonrise_times(
        location,
        start_time,
        count=count,
        elevation=elevation_msl,
        gridpts=gridpts,
    )

    momentsarray = moonrises + np.timedelta64(120, 'm')
    momentsarray = formatters.format_datetime(momentsarray, 'to string for AWIMtag')

    return momentsarray

# glockenspiel: sunset - 30 minutes every day for a year (366 frames), starting today
def get_glockenspiel_sunset_year(location, elevation_msl, currenttime, days=366, gridpts=80, use_cache=True):
    if use_cache:
        start_day = _to_datetime64_seconds(currenttime).astype('datetime64[D]')
        cached_moments = _get_glockenspiel_event_moments_from_cache(
            location,
            start_day,
            event_type='sunset',
            count=days,
            offset_minutes=-30,
            window_days=days + 7,
        )
        if cached_moments is not None:
            return cached_moments

    currenttime = np.datetime64(currenttime)
    start_day = currenttime.astype('datetime64[D]')

    sunsets = astromath.calculate_astro_sunset_times(
        location,
        start_day,
        days=days,
        elevation=elevation_msl,
        gridpts=gridpts,
    )

    sunsets = sunsets - np.timedelta64(30, 'm')

    momentsarray = formatters.format_datetime(sunsets, 'to string for AWIMtag')

    return momentsarray
