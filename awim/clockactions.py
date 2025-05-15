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


def get_celestialinphoto(awim_dict, momentsarray, requestlist, inimage_threshold=2, padding_percent = 5):
    momentsarray = np.array([np.datetime64(moment) for moment in momentsarray])
    location = awim_dict['awim Location Coordinates']
    elevation = awim_dict['awim Location Terrain Elevation'] + awim_dict['awim Location AGL'] # this should be only if awim Location MSL is null, which it usually is but not always.
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
    
    for key, value in bodies_astro_dict.items():
        print('Calculating position in image for: ' + key)
        body_azarts = value[:,3:5]
        # azart_to_dirarc here?
        body_xyangs = awimlib.azarts_to_xyangs(awim_dict, body_azarts) # with dirarc, xyangs are just an intermediary, but still necessary and still useful for determining if body is in image.
        body_inimage = awimlib.xyangs_inimage(awim_dict, body_xyangs, padding_percent=padding_percent)
        if body_inimage.sum() >= inimage_threshold:
            print(key + ' appears in the image.')
            body_dirarcs = awimlib.xyangs_to_dirarcs(body_xyangs) # dirarcs are useful because possible to correct for tilt. Are they otherwise necessary?
            body_pxs = awimlib.xyangs_to_pxs(awim_dict, body_xyangs) # convert this calculation to dirarcs_to_pixels because more versatile and can implement tilt.
            # For all bodies:
            # 0: In the photo? True / False by moment
            # 1: Pixel position x
            # 2: Pixel position y
            # 3: Distance in AU within solar system or light years outside - TODO for the stars because the catalogues do not include distances and it seems it's not always known very well? Currently setting to zero for the stars.
            # Plus for sun and moon:
            # 4: Azimuth just for interesting information and completeness to go with artifae
            # 5: Artifae for information and for the sky color animation
            # Plus for moon only:
            # 6: Phase angle
            # 7: Bright side direction
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
            body_data[:,1:3] = body_pxs
            body_data[:,3] = value[:,2]

            bodies_image_dict[key] = body_data
    
    bodies_total = len(bodies_astro_dict)
    bodiescount_inimage = len(bodies_image_dict)
    print(f'{bodies_total} total bodies, {bodiescount_inimage} bodies in image during period, so {round(bodiescount_inimage/bodies_total * 100, 2)} percent of total passed through image during period.')

    bodies_astro_dict_lists = formatters.dict_arrays_tolists(bodies_astro_dict)
    bodies_image_dict_lists = formatters.dict_arrays_tolists(bodies_image_dict)

    return bodies_astro_dict_lists, bodies_image_dict_lists