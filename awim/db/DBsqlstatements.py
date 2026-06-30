from typing import List, Any
from db import DBfunctions
from core import formatters


def insert_camfilenames(camfilenames: List[str]) -> None:
    qms_tuple = [(camfilename,) for camfilename in camfilenames]
    results = DBfunctions.sql_execute("""
INSERT INTO photos_awim (CamFilename)
VALUES (%s) ;
""", qms_tuple, result_type='updatedb', many=True)

    return results


def get_photo(group_id, basename):
    qms_tuple = (group_id, basename)
    results = DBfunctions.sql_execute("""
SELECT p.*
FROM photos_awim p
JOIN photo_grouping pg ON pg.PhotoID = p.photo_id
JOIN groups g ON g.group_id = pg.GroupID
WHERE g.GroupType = 'batch'
AND g.group_id = ?
AND p.CamFilename = ?;
""", qms_tuple, result_type='listdictionaries')

    return results


def get_basenames(group_id):
    qms_tuple = (group_id,)
    results = DBfunctions.sql_execute("""
SELECT p.CamFilename
FROM photos_awim p
JOIN photo_grouping pg ON pg.PhotoID = p.photo_id
JOIN groups g ON g.group_id = pg.GroupID
WHERE g.GroupType = 'batch'
AND g.group_id = ? ;
""", qms_tuple, result_type='listsinglefield')

    return results


def get_photos_with_coordinates():
    results = DBfunctions.sql_execute("""
SELECT photo_id, Latitude, Longitude
FROM photos_awim
WHERE Latitude IS NOT NULL
AND Longitude IS NOT NULL;
""", result_type='listdictionaries')

    return results


def get_primary_location_center(location_type='town_square'):
    qms_tuple = (location_type,)
    results = DBfunctions.sql_execute("""
SELECT loc_id, CenterLatitude, CenterLongitude
FROM locations
WHERE LocationType = ?
AND CenterLatitude IS NOT NULL
AND CenterLongitude IS NOT NULL
ORDER BY loc_id ASC
LIMIT 1;
""", qms_tuple, result_type='listdictionaries')

    return results


def get_location_centers(location_type=None):
    if location_type is None:
        results = DBfunctions.sql_execute("""
SELECT loc_id, LocationType, CenterLatitude, CenterLongitude
FROM locations
WHERE CenterLatitude IS NOT NULL
AND CenterLongitude IS NOT NULL;
""", result_type='listdictionaries')
    else:
        qms_tuple = (location_type,)
        results = DBfunctions.sql_execute("""
SELECT loc_id, LocationType, CenterLatitude, CenterLongitude
FROM locations
WHERE LocationType = ?
AND CenterLatitude IS NOT NULL
AND CenterLongitude IS NOT NULL;
""", qms_tuple, result_type='listdictionaries')

    return results


def insert_locations(location_rows):
    if not location_rows:
        return

    results = DBfunctions.sql_execute("""
INSERT INTO locations (LocationName, LocationType, CenterLatitude, CenterLongitude)
VALUES (?, ?, ?, ?);
""", location_rows, result_type='updatedb', many=True)

    return results


def get_cache_locations_with_photo_counts():
    results = DBfunctions.sql_execute("""
SELECT
    l.loc_id,
    l.LocationName,
    l.LocationType,
    l.CenterLatitude,
    l.CenterLongitude,
    COUNT(p.photo_id) AS PhotoCount
FROM locations l
LEFT JOIN photos_awim p ON p.LocationID = l.loc_id
WHERE l.CenterLatitude IS NOT NULL
AND l.CenterLongitude IS NOT NULL
GROUP BY l.loc_id, l.LocationName, l.LocationType, l.CenterLatitude, l.CenterLongitude
ORDER BY l.loc_id ASC;
""", result_type='listdictionaries')

    return results


def get_cached_daily_events(location_id, start_moment, end_moment, event_types=None):
    params = [location_id, start_moment, end_moment]
    event_type_clause = ""
    if event_types:
        placeholders = ", ".join(["?"] * len(event_types))
        event_type_clause = f"AND EventType IN ({placeholders})"
        params.extend(event_types)

    results = DBfunctions.sql_execute(f"""
SELECT
    event_id,
    LocationID,
    EventType,
    MomentEvent,
    EventBody,
    EventAzimuth,
    EventArtifae,
    EventMoonPhaseAngle
FROM cache_daily_events
WHERE LocationID = ?
AND MomentEvent >= ?
AND MomentEvent < ?
{event_type_clause}
ORDER BY MomentEvent ASC, event_id ASC;
""", tuple(params), result_type='listdictionaries')

    return results


def get_cached_astrodata_chunk(location_id, cache_type, start_moment, end_moment, schema_version=1):
    qms_tuple = (location_id, cache_type, schema_version, start_moment, end_moment)
    results = DBfunctions.sql_execute("""
SELECT
    SchemaVersion,
    LocationID,
    CacheType,
    ChunkStartUTC,
    StepSeconds,
    MomentsCount,
    CachedData,
    MomentCreated
FROM cache_astrodata
WHERE LocationID = ?
AND CacheType = ?
AND SchemaVersion = ?
AND ChunkStartUTC <= ?
AND DATE_ADD(ChunkStartUTC, INTERVAL (StepSeconds * MomentsCount) SECOND) > ?
ORDER BY ChunkStartUTC DESC
LIMIT 1;
""", qms_tuple, result_type='listdictionaries')

    return results[0] if results else None


def get_locations_by_name_prefix(name_prefix):
    qms_tuple = (name_prefix,)
    results = DBfunctions.sql_execute("""
SELECT loc_id, LocationName
FROM locations
WHERE LocationName LIKE ?
ORDER BY loc_id ASC;
""", qms_tuple, result_type='listdictionaries')

    return results


def update_photo_locations_with_distance(update_rows):
    if not update_rows:
        return

    results = DBfunctions.sql_execute("""
UPDATE photos_awim
SET LocationID = ?, DistanceFromCenter = ?
WHERE photo_id = ?;
""", update_rows, result_type='updatedb', many=True)

    return results


def get_daily_events_max_moment(location_id):
    qms_tuple = (location_id,)
    results = DBfunctions.sql_execute("""
SELECT MAX(MomentEvent)
FROM cache_daily_events
WHERE LocationID = ?
AND EventType NOT IN ('newmoon', 'fullmoon');
""", qms_tuple, result_type='listsinglefield')

    return results[0] if results else None


def get_daily_events_max_moments_by_event_type(location_id, event_types):
    if not event_types:
        return []

    placeholders = ", ".join(["?"] * len(event_types))
    qms_tuple = tuple([location_id] + list(event_types))
    results = DBfunctions.sql_execute(f"""
SELECT EventType, MAX(MomentEvent) AS MaxMomentEvent
FROM cache_daily_events
WHERE LocationID = ?
AND EventType IN ({placeholders})
GROUP BY EventType;
""", qms_tuple, result_type='listdictionaries')

    return results


def get_global_newfullmoon_max_moment():
    results = DBfunctions.sql_execute("""
SELECT MAX(MomentEvent)
FROM cache_daily_events
WHERE LocationID IS NULL
AND EventType IN ('newmoon', 'fullmoon');
""", result_type='listsinglefield')

    return results[0] if results else None


def get_location_newfullmoon_max_moment(location_id):
    qms_tuple = (location_id,)
    results = DBfunctions.sql_execute("""
SELECT MAX(MomentEvent)
FROM cache_daily_events
WHERE LocationID = ?
AND EventType IN ('newmoon', 'fullmoon');
""", qms_tuple, result_type='listsinglefield')

    return results[0] if results else None


def get_existing_daily_event_keys(location_id, start_moment, end_moment):
    qms_tuple = (location_id, start_moment, end_moment)
    results = DBfunctions.sql_execute("""
SELECT EventType, MomentEvent
FROM cache_daily_events
WHERE LocationID = ?
AND MomentEvent >= ?
AND MomentEvent < ?;
""", qms_tuple, result_type='listtuples')

    return results


def get_existing_location_newfullmoon_keys(location_id, start_moment, end_moment):
    qms_tuple = (location_id, start_moment, end_moment)
    results = DBfunctions.sql_execute("""
SELECT EventType, MomentEvent
FROM cache_daily_events
WHERE LocationID = ?
AND EventType IN ('newmoon', 'fullmoon')
AND MomentEvent >= ?
AND MomentEvent < ?;
""", qms_tuple, result_type='listtuples')

    return results


def get_existing_global_newfullmoon_keys(start_moment, end_moment):
    qms_tuple = (start_moment, end_moment)
    results = DBfunctions.sql_execute("""
SELECT EventType, MomentEvent
FROM cache_daily_events
WHERE LocationID IS NULL
AND EventType IN ('newmoon', 'fullmoon')
AND MomentEvent >= ?
AND MomentEvent < ?;
""", qms_tuple, result_type='listtuples')

    return results


def get_global_newfullmoon_rows(start_moment, end_moment):
    qms_tuple = (start_moment, end_moment)
    results = DBfunctions.sql_execute("""
SELECT EventType, MomentEvent, EventBody, EventMoonPhaseAngle
FROM cache_daily_events
WHERE LocationID IS NULL
AND EventType IN ('newmoon', 'fullmoon')
AND MomentEvent >= ?
AND MomentEvent < ?
ORDER BY MomentEvent ASC;
""", qms_tuple, result_type='listtuples')

    return results


def insert_cache_daily_events(event_rows):
    if not event_rows:
        return

    results = DBfunctions.sql_execute("""
INSERT INTO cache_daily_events
(LocationID, EventType, MomentEvent, EventBody, EventAzimuth, EventArtifae, EventMoonPhaseAngle)
VALUES (?, ?, ?, ?, ?, ?, ?);
""", event_rows, result_type='updatedb', many=True)

    return results


def get_global_newfullmoon_missing_fields():
    results = DBfunctions.sql_execute("""
SELECT event_id, EventType, EventBody, MomentEvent
FROM cache_daily_events
WHERE LocationID IS NULL
AND EventType IN ('newmoon', 'fullmoon')
AND (EventAzimuth IS NULL OR EventArtifae IS NULL OR EventMoonPhaseAngle IS NULL)
ORDER BY MomentEvent ASC, event_id ASC;
""", result_type='listdictionaries')

    return results


def get_daily_events_missing_azart(location_id):
    qms_tuple = (location_id,)
    results = DBfunctions.sql_execute("""
SELECT event_id, EventBody, MomentEvent
FROM cache_daily_events
WHERE LocationID = ?
AND EventBody IN ('sun', 'moon')
AND (EventAzimuth IS NULL OR EventArtifae IS NULL)
ORDER BY MomentEvent ASC, event_id ASC;
""", qms_tuple, result_type='listdictionaries')

    return results


def update_daily_events_azart_phase(update_rows):
    if not update_rows:
        return

    results = DBfunctions.sql_execute("""
UPDATE cache_daily_events
SET EventAzimuth = ?, EventArtifae = ?, EventMoonPhaseAngle = ?
WHERE event_id = ?;
""", update_rows, result_type='updatedb', many=True)

    return results


def update_daily_events_azart(update_rows):
    if not update_rows:
        return

    results = DBfunctions.sql_execute("""
UPDATE cache_daily_events
SET EventAzimuth = ?, EventArtifae = ?
WHERE event_id = ?;
""", update_rows, result_type='updatedb', many=True)

    return results


def upsert_cache_astrodata(schema_version, location_id, cache_type, chunk_start_utc, step_seconds, moments_count, cached_data_json):
    qms_tuple = (schema_version, location_id, cache_type, chunk_start_utc, step_seconds, moments_count, cached_data_json)
    results = DBfunctions.sql_execute("""
INSERT INTO cache_astrodata
(SchemaVersion, LocationID, CacheType, ChunkStartUTC, StepSeconds, MomentsCount, CachedData)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON DUPLICATE KEY UPDATE
    StepSeconds = VALUES(StepSeconds),
    MomentsCount = VALUES(MomentsCount),
    CachedData = VALUES(CachedData),
    MomentCreated = CURRENT_TIMESTAMP();
""", qms_tuple, result_type='updatedb')

    return results


# Duplicate data, but this puts the calculated values in the DB for a table view of how the awim tag values were calculated.
def update_scratchpad(AWIMtag_dictionary, dev_dict):
    momentcapture = formatters.format_datetime(AWIMtag_dictionary['awim Capture Moment'], 'to string for mysql')
    basename = dev_dict['Basename']
    photomsl = AWIMtag_dictionary['awim Location MSL']
    objadjaz = dev_dict.get('AzRefObjAdjAz')
    azart = AWIMtag_dictionary['awim Ref Pixel Azimuth Artifae']
    awimtag = dev_dict['awimTag']
    dbid = AWIMtag_dictionary['DB id']

    qms_tuple = (momentcapture, basename, photomsl, objadjaz, azart[0], azart[1], awimtag, dbid)

    results = DBfunctions.sql_execute("""
UPDATE photos_awim
SET
    MomentCapture = ?,
    Basename = ?,
    PhotoMSL = ?,
    AzRefObjAdjAz = ?,
    Azimuth = ?,
    Artifae = ?,
    awimTag = ?
WHERE id = ? ;
""", qms_tuple, result_type='updatedb')

    return results


def get_stars(MagRankAll, LatDec_filter=False):
    LatDec_clause = ""
    if isinstance(LatDec_filter, (int, float)) and LatDec_filter != 0:
        if LatDec_filter > 0:
            DecLimit = LatDec_filter - 91
            LatDec_clause = f" AND Declination > {DecLimit} "
        else:
            DecLimit = LatDec_filter + 91
            LatDec_clause = f" AND Declination < {DecLimit} "

    qms_tuple = (MagRankAll,)
    results = DBfunctions.sql_execute(
"""
SELECT bsc.HarvardRevised , bsc.ReadableName , bsc.RA*15 , bsc.Declination , bsc.Distance , bsc.VisualMagnitude , bsc.MagRankAll , bsc.ConstellationFullName , bsc.MagRankConstellation , bsc.GreekLetter
FROM bright_star_catalogue bsc
WHERE (bsc.MagRankAll <= ? OR bsc.MagRankConstellation = 1)
AND RA IS NOT NULL
AND Declination IS NOT NULL
""" + LatDec_clause + """
order by bsc.VisualMagnitude ;
""", qms_tuple, result_type='listtuples')

    return results


def db_temp(qms_tuple):
    results = DBfunctions.sql_execute("""
UPDATE bright_star_catalogue
SET ConstellationAbbreviation = ?
where bright_star_catalogue.ConstellationFullName  = ?;
""", qms_tuple, result_type='updatedb')

    return results
