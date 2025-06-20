import numpy as np
import astromath, awimlib, formatters, DBsqlstatements

def get_events(location, elevation_msl, currenttime):
    currenttime = np.datetime64(currenttime)
    # nowmoments = formatters.format_datetime(nowmoments, direction='from list of ISO 8601 strings')
    # nowmoments = np.array(nowmoments).astype('datetime64[ns]')
    sundaily, moondaily = astromath.calculate_astro_risesandsets(location, currenttime, elevation_msl) # todo: cache these results because they take time to calculate.
    newmoon_time, newmoon_angle, fullmoon_time, fullmoon_angle = astromath.calculate_astro_newfullmoon(currenttime)
    response_dict = {}
    response_dict['sundaily'] = formatters.format_datetime(sundaily, 'to string for AWIMtag')
    response_dict['moondaily'] = formatters.format_datetime(moondaily, 'to string for AWIMtag')
    response_dict['newmoon time'] = formatters.format_datetime(newmoon_time, 'to string for AWIMtag')
    response_dict['newmoon angle'] = str(newmoon_angle)
    response_dict['fullmoon time'] = formatters.format_datetime(fullmoon_time, 'to string for AWIMtag')
    response_dict['fullmoon angle'] = str(fullmoon_angle)

    return response_dict


def get_astrodata(awim_dict, momentsarray, requestlist):
    momentsarray = np.array([np.datetime64(moment) for moment in momentsarray])
    location = awim_dict['awim Location Coordinates']
    if not awim_dict['awim Location MSL']:
        if awim_dict['awim Location Terrain Elevation'] and awim_dict['awim Location AGL']:
            elevation = awim_dict['awim Location Terrain Elevation'] and awim_dict['awim Location AGL']
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
            stars_tuples = DBsqlstatements.get_stars(MagRankAll=2000)
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