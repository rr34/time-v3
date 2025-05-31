import DBfunctions
import formatters

def get_photo(batchID, basename):
    qms_tuple = (batchID, basename)
    results = DBfunctions.sql_execute("""
SELECT *
FROM photos_awim
WHERE BatchID = ?
AND CamFilename = ?;
""", qms_tuple, result_type='listdictionaries')

    return results


def get_basenames(batchID):
    qms_tuple = (batchID,)
    results = DBfunctions.sql_execute("""
SELECT CamFilename
FROM photos_awim
WHERE BatchID = ? ;
""", qms_tuple, result_type='listsinglefield')

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


def get_stars(MagRankAll):
    qms_tuple = (MagRankAll,)
    results = DBfunctions.sql_execute("""
SELECT bsc.HarvardRevised , bsc.ReadableName , bsc.RA*15 , bsc.Declination , bsc.Distance , bsc.VisualMagnitude , bsc.MagRankAll , bsc.ConstellationFullName , bsc.MagRankConstellation , bsc.GreekLetter
FROM bright_star_catalogue bsc
WHERE bsc.MagRankAll < ?
OR bsc.MagRankConstellation = 1
AND RA IS NOT NULL
AND Declination IS NOT NULL
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
