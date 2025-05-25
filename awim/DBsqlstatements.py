import DBfunctions

def get_photo(photoshoot_id, basename):
    qms_tuple = (photoshoot_id, basename)
    results = DBfunctions.sql_execute("""
SELECT *, CONCAT(CamFilePre , CamFileUnique ) as basename
FROM shoot_cte sc 
WHERE ShootID = ? 
HAVING basename = ?;
""", qms_tuple, result_type='listdictionaries')

    return results


def get_basenames(photoshoot_id):
    qms_tuple = (photoshoot_id,)
    results = DBfunctions.sql_execute("""
SELECT CONCAT(CamFilePre , CamFileUnique ) as basename
FROM shoot_photos
WHERE ShootID = ? ;
""", qms_tuple, result_type='listsinglefield')

    return results


def get_stars(magnitude):
    qms_tuple = (magnitude,)
    results = DBfunctions.sql_execute("""
SELECT bsc.HarvardRevised , bsc.ReadableName , bsc.RA*15 , bsc.Declination , bsc.Distance , bsc.VisualMagnitude , bsc.MagRankAll , bsc.ConstellationFullName , bsc.MagRankConstellation , bsc.GreekLetter
FROM bright_star_catalogue bsc
WHERE bsc.VisualMagnitude < ?
OR bsc.MagRank = 1
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
