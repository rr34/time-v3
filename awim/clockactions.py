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


def get_celestialinphoto(awim_dict, momentsarray, elevation, requestlist):
    momentsarray = np.array([np.datetime64(moment) for moment in momentsarray])
    location = awim_dict['awim Location Coordinates']
    celestial_bodies = []
    for request in requestlist:
        if request == 'sun':
            celestial_bodies.append('sun')
        elif request == 'moon':
            celestial_bodies.append('moon')
        elif request == 'planets':
            planetslist = ['mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
            for planet in planetslist:
                celestial_bodies.append(planet)
        elif request == 'stars':
            stars_tuples = DBsqlstatements.get_stars()
            for star in stars_tuples:
                star_name = 'HR ' + str(star[6])
                RA = star[3]
                Dec = star[4]
                celestial_bodies.append((star_name, RA, Dec))

    # astro data function generates a dictionary within it because it uses the common location and times for calculation efficiency
    bodies_astro_dict = astromath.calculate_astro_data(momentsarray, location, celestial_bodies)

    # bodies in the image dictionary generated here outside the awimlib functions because there is no commonality among the bodies in image for efficiency
    bodies_image_dict = {}
    for key, value in bodies_astro_dict.items():
        azarts = value[:,3:5]
        bodies_xyangs = awimlib.azarts_to_xyangs(awim_dict, azarts)
        bodies_inimage = awimlib.xyangs_inimage(awim_dict, bodies_xyangs, padding_percent=10)
        body_data = np.zeros((momentsarray.size, 3))
        body_data[:,0] = bodies_inimage
        # body_data[:,1:3] = pxs

        bodies_image_dict[key] = body_data