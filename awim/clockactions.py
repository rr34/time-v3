import numpy as np
import clockmath, formatters

def get_events(location, elevation_msl, currenttime):
    currenttime = np.datetime64(currenttime)
    # nowmoments = formatters.format_datetime(nowmoments, direction='from list of ISO 8601 strings')
    # nowmoments = np.array(nowmoments).astype('datetime64[ns]')
    sundaily, moondaily = clockmath.calculate_astro_risesandsets(location, currenttime, elevation_msl) # todo: cache these results because they take time to calculate.
    newmoon_time, newmoon_angle, fullmoon_time, fullmoon_angle = clockmath.calculate_astro_newfullmoon(currenttime)
    response_dict = {}
    response_dict['sundaily'] = formatters.format_datetime(sundaily, 'to string for AWIMtag')
    response_dict['moondaily'] = formatters.format_datetime(moondaily, 'to string for AWIMtag')
    response_dict['newmoon time'] = formatters.format_datetime(newmoon_time, 'to string for AWIMtag')
    response_dict['newmoon angle'] = str(newmoon_angle)
    response_dict['fullmoon time'] = formatters.format_datetime(fullmoon_time, 'to string for AWIMtag')
    response_dict['fullmoon angle'] = str(fullmoon_angle)

    return response_dict


def get_celestialinphoto(awim_dict, momentsarray, elevation, requestlist):
    momentsarray = np.array([np.datetime64(moment) for moment in momentsarray])
    requests_expanded = []
    for request in requestlist:
        if request == 'sun':
            requests_expanded.append('sun')
        elif request == 'moon':
            requests_expanded.append('moon')
        elif request == 'planets':
            planetslist = ['mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
            for planet in planetslist:
                requests_expanded.append(planet)
        elif request == 'stars':

    response_dict = {}
    for request in requestlist:
        if request == 'sun':

            print('get sun')
            response_dict['sun'] = 'something'