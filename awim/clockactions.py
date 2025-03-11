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
    # The following loop just creates the expanded list of bodies. Within solar system just get a name because RA, Dec has to be calculated. Outside solar system (stars) are a tuple of name with the RA, Dec given.
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
    padding_percent = 10
    inimage_threshold = 2
    for key, value in bodies_astro_dict.items():
        body_azarts = value[:,3:5]
        bodies_xyangs = awimlib.azarts_to_xyangs(awim_dict, body_azarts)
        body_inimage = awimlib.xyangs_inimage(awim_dict, bodies_xyangs, padding_percent=padding_percent)
        if body_inimage.sum() >= inimage_threshold:
            print(key)
            bodies_pxs = awimlib.xyangs_to_pxs(awim_dict, bodies_xyangs)
            if key not in ['sun', 'moon']:
                body_data = np.zeros((momentsarray.size, 4))
            elif key == 'sun':
                body_data = np.zeros((momentsarray.size, 6))
                body_data[:,4:6] = body_azarts
            elif key == 'moon':
                body_data = np.zeros((momentsarray.size, 8))
                body_data[:,4:6] = body_azarts
                phase_angle = astromath.calculate_astro_moonphaseangle(momentsarray)
                body_data[:,6] = phase_angle
                sun_azarts = bodies_astro_dict['sun'][:,3:5]
                brightside_direction = astromath.calculate_astro_moon_brightsidedirection(body_azarts, sun_azarts)
                body_data[:,7] = brightside_direction

            body_data[:,0] = body_inimage
            body_data[:,1:3] = bodies_pxs
            body_data[:,3] = value[:,2]

            bodies_image_dict[key] = body_data
    
    bodies_total = len(bodies_astro_dict)
    bodiescount_inimage = len(bodies_image_dict)
    print(f'Total bodies: {bodies_total}. Bodies in image during period: {bodiescount_inimage}. Percent in image: {bodiescount_inimage/bodies_total * 100}')

    return bodies_astro_dict, bodies_image_dict