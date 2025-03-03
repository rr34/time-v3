import numpy as np
import clockmath, formatters

def get_time_strings(location, elevation_msl, currenttime):
    currenttime = np.datetime64(currenttime)
    # nowmoments = formatters.format_datetime(nowmoments, direction='from list of ISO 8601 strings')
    # nowmoments = np.array(nowmoments).astype('datetime64[ns]')
    sundaily, moondaily = clockmath.calculate_astro_risesandsets(location, currenttime, elevation_msl) # todo: cache these results because they take time to calculate.
    nearest_new_moon, nearest_full_moon, moon_illumination_percent = clockmath.calculate_astro_moon_phase(currenttime)
    response_dict = {}
    response_dict['sundaily'] = formatters.format_datetime(sundaily, 'to string for AWIMtag')
    response_dict['moondaily'] = formatters.format_datetime(moondaily, 'to string for AWIMtag')

    return response_dict