from datetime import timezone
import math
import numpy as np
import copy
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun, get_body
import astroplan

# this function takes a long time to run, greatly affected by the value of gridpts, but is valid for something like 24 hours
def calculate_astro_risesandsets(earth_latlng, moment_now, elevation=0):
    time_now_astropy = Time(moment_now)
    clock_astroplan_observer = astroplan.Observer(longitude=earth_latlng[1]*u.deg, latitude=earth_latlng[0]*u.deg, elevation=elevation*u.m, name='Time v3 Clock', timezone=timezone.utc)
    gridpts = 150

    print('calculating sun daily events')
    sun_daily = np.empty(13, dtype=np.dtype('datetime64[ns]'))

    first_midnight = clock_astroplan_observer.midnight(time=time_now_astropy, which='previous', n_grid_points=gridpts)
    first_sunrise = clock_astroplan_observer.sun_rise_time(time=first_midnight, which='previous', horizon=-0.833*u.deg, n_grid_points=gridpts)
    sun_daily[0] = first_sunrise.datetime64 # 1st sunrise
    astropy_temp = clock_astroplan_observer.noon(time=first_sunrise, which='next', n_grid_points=gridpts)
    sun_daily[1] = astropy_temp.datetime64 # 1st noon
    astropy_temp = clock_astroplan_observer.sun_set_time(time=astropy_temp, which='next', horizon=-0.833*u.deg, n_grid_points=gridpts)
    sun_daily[2] = astropy_temp.datetime64 # 1st sunset
    sun_daily[3] = first_midnight.datetime64 # 1st midnight, already calculated, earliest possible moment_now value
    astropy_temp = clock_astroplan_observer.sun_rise_time(time=first_midnight, which='next', horizon=-0.833*u.deg, n_grid_points=gridpts) # second sunrise is the next instead of previous sunrise
    sun_daily[4] = astropy_temp.datetime64 # 2nd sunrise
    astropy_temp = clock_astroplan_observer.noon(time=astropy_temp, which='next', n_grid_points=gridpts)
    sun_daily[5] = astropy_temp.datetime64 # 2nd noon
    astropy_temp = clock_astroplan_observer.sun_set_time(time=astropy_temp, which='next', horizon=-0.833*u.deg, n_grid_points=gridpts)
    sun_daily[6] = astropy_temp.datetime64 # 2nd sunset
    astropy_temp = clock_astroplan_observer.midnight(time=astropy_temp, which='next', n_grid_points=gridpts)
    sun_daily[7] = astropy_temp.datetime64 # 2nd midnight. The clock could crawl just past this point if moment now were just before midnight because would calculate so far back.
    astropy_temp = clock_astroplan_observer.sun_rise_time(time=astropy_temp, which='next', horizon=-0.833*u.deg, n_grid_points=gridpts)
    sun_daily[8] = astropy_temp.datetime64 # 3rd sunrise
    astropy_temp = clock_astroplan_observer.noon(time=astropy_temp, which='next', n_grid_points=gridpts)
    sun_daily[9] = astropy_temp.datetime64 # 3rd noon
    astropy_temp = clock_astroplan_observer.sun_set_time(time=astropy_temp, which='next', horizon=-0.833*u.deg, n_grid_points=gridpts)
    sun_daily[10] = astropy_temp.datetime64 # 3rd sunset
    astropy_temp = clock_astroplan_observer.midnight(time=astropy_temp, which='next', n_grid_points=gridpts)
    sun_daily[11] = astropy_temp.datetime64 # 3rd and final midnight. 3 of each event.
    astropy_temp = clock_astroplan_observer.sun_rise_time(time=astropy_temp, which='next', horizon=-0.833*u.deg, n_grid_points=gridpts)
    sun_daily[12] = astropy_temp.datetime64 # 4th sunrise to calculate night length in unlikely event clock crawls past 3rd sunrise

    print('calculating moon daily events')
    moon_daily = np.empty(6, dtype=np.dtype('datetime64[ns]'))

    first_moonset = clock_astroplan_observer.moon_set_time(time=time_now_astropy, which='previous', horizon=0*u.deg, n_grid_points=gridpts)
    moon_daily[0] = clock_astroplan_observer.moon_rise_time(time=first_moonset, which='previous', horizon=0*u.deg, n_grid_points=gridpts).datetime64 # 1st moonrise
    moon_daily[1] = first_moonset.datetime64 # 1st moonset, earliest possible moment_now value
    astropy_temp = clock_astroplan_observer.moon_rise_time(time=first_moonset, which='next', horizon=0*u.deg, n_grid_points=gridpts)
    moon_daily[2] = astropy_temp.datetime64 # 2nd moonrise
    astropy_temp = clock_astroplan_observer.moon_set_time(time=astropy_temp, which='next', horizon=0*u.deg, n_grid_points=gridpts)
    moon_daily[3] = astropy_temp.datetime64 # 2nd moonset
    astropy_temp = clock_astroplan_observer.moon_rise_time(time=astropy_temp, which='next', horizon=0*u.deg, n_grid_points=gridpts)
    moon_daily[4] = astropy_temp.datetime64 # 3rd moonrise
    astropy_temp = clock_astroplan_observer.moon_set_time(time=astropy_temp, which='next', horizon=0*u.deg, n_grid_points=gridpts)
    moon_daily[5] = astropy_temp.datetime64 # 3rd moonset

    return sun_daily, moon_daily


# I don't know why this doesn't return exactly a full/new moon matching online sources - differs by up to ~30 minutes? Why? phase is different from "ecliptic longitude different by 180°?" - but since I did it here it is...
# This function is good enough for now because I only really care about the single new or full moon that is the closest. I don't ever care about a full moon 14 days past or future because the new moon would be within a day so obviously closer.
# TODO calculate the 180deg ecliptic longitude difference full moon and see if different
def calculate_astro_newfullmoon(moment_now, discretize=150):
    print('calculating moon phase events')
    # lunar_cycle_average = np.timedelta64(29.53, 'D') # not used but here it is
    # moment_now_astropy = Time(moment_now)
    # moon_illumination_percent = astroplan.moon_illumination(moment_now_astropy) * 100
    check_period = 31 # days. Better to get two than zero of a new or full moon.
    check_period = np.timedelta64(check_period*24*60*60*1000, 'ms')
    # 1st iteration
    step_size = check_period / discretize
    moments_check_array = np.arange(moment_now-check_period/2, moment_now+check_period/2, step_size)
    moments_check_astropy = Time(moments_check_array)
    moon_phase_check = astroplan.moon_phase_angle(moments_check_astropy).to_value()
    maxmin = np.diff(np.sign(np.diff(moon_phase_check)))
    newmoon = np.where(maxmin == -2, True, False) # finds max, which is new moon
    fullmoon = np.where(maxmin == 2, True, False) # finds min, which is full moon

    # new moon calculation finding the maximum phase angle.
    if newmoon.sum() == 2: # if two new moons are found, keep only the closer one.
        newmoon1 = np.where(newmoon == True)[0][0] + 1
        newmoon2 = np.where(newmoon == True)[0][1] + 1
        if np.abs(moments_check_array[newmoon1] - moment_now) < np.abs(moments_check_array[newmoon2] - moment_now):
            newmoon[newmoon2 - 1] = False
        elif np.abs(moments_check_array[newmoon2] - moment_now) < np.abs(moments_check_array[newmoon1] - moment_now):
            newmoon[newmoon1 - 1] = False
    if newmoon.sum() == 1:
        newmoon = np.where(newmoon == True)[0][0] + 1
        # 2nd interation
        step_size_new = step_size / (discretize / 2) # the period is divided by only half the discretize
        moments_check_array_new = np.arange(moments_check_array[newmoon-1] - step_size_new, moments_check_array[newmoon+1] + step_size_new, step_size_new)
        moments_check_astropy = Time(moments_check_array_new)
        moon_phase_check = astroplan.moon_phase_angle(moments_check_astropy).to_value()
        maxmin = np.diff(np.sign(np.diff(moon_phase_check)))
        newmoon = np.where(maxmin <= -1, True, False)
    else:
        newmoon_time = False
        newmoon_angle = False
        print('some error look here')

    if newmoon.sum() == 1:
        newmoon = np.where(newmoon == True)[0][0] + 1
        # 3rd interation
        step_size_new = step_size_new / (discretize / 2) # the period is divided by only half the discretize
        moments_check_array_new = np.arange(moments_check_array_new[newmoon-1] - step_size_new, moments_check_array_new[newmoon+1] + step_size_new, step_size_new)
        moments_check_astropy = Time(moments_check_array_new)
        moon_phase_check = astroplan.moon_phase_angle(moments_check_astropy).to_value()
        maxmin = np.diff(np.sign(np.diff(moon_phase_check)))
        newmoon = np.where(maxmin <= -1, True, False)
    else:
        newmoon_time = False
        newmoon_angle = False
        print('some error look here')

    if newmoon.sum() == 1:
        newmoon = np.where(newmoon == True)[0][0] + 1
        newmoon_time = moments_check_array_new[newmoon] # result is the check of the 3rd iteration
        newmoon_angle = moon_phase_check[newmoon] * 180/math.pi
    else:
        newmoon_time = False
        newmoon_angle = False
        print('some error look here')

    # full moon calculation finding the minimum phase angle.
    if fullmoon.sum() == 2: # if two full moons are found, keep only the closer one.
        fullmoon1 = np.where(fullmoon == True)[0][0] + 1
        fullmoon2 = np.where(fullmoon == True)[0][1] + 1
        if np.abs(moments_check_array[fullmoon1] - moment_now) < np.abs(moments_check_array[fullmoon2] - moment_now):
            fullmoon[fullmoon2 - 1] = False
        elif np.abs(moments_check_array[fullmoon2] - moment_now) < np.abs(moments_check_array[fullmoon1] - moment_now):
            fullmoon[fullmoon1 - 1] = False
    if fullmoon.sum() == 1:
        fullmoon = np.where(fullmoon == True)[0][0] + 1
        # 2nd interation
        step_size_full = step_size / (discretize / 2) # the period is divided by only half the discretize
        moments_check_array_full = np.arange(moments_check_array[fullmoon-1] - step_size_full, moments_check_array[fullmoon+1] + step_size_full, step_size_full)
        moments_check_astropy = Time(moments_check_array_full)
        moon_phase_check = astroplan.moon_phase_angle(moments_check_astropy).to_value()
        maxmin = np.diff(np.sign(np.diff(moon_phase_check)))
        fullmoon = np.where(maxmin >= 1, True, False)
    else:
        fullmoon_time = False
        fullmoon_angle = False
        print('some error look here')

    if fullmoon.sum() == 1:
        fullmoon = np.where(fullmoon == True)[0][0] + 1
        # 3rd interation
        step_size_full = step_size_full / (discretize / 2) # the period is divided by only half the discretize
        moments_check_array_full = np.arange(moments_check_array_full[fullmoon-1] - step_size_full, moments_check_array_full[fullmoon+1] + step_size_full, step_size_full)
        moments_check_astropy = Time(moments_check_array_full)
        moon_phase_check = astroplan.moon_phase_angle(moments_check_astropy).to_value()
        maxmin = np.diff(np.sign(np.diff(moon_phase_check)))
        fullmoon = np.where(maxmin >= 1, True, False)
    else:
        fullmoon_time = False
        fullmoon_angle = False
        print('some error look here')

    if fullmoon.sum() == 1:
        fullmoon = np.where(fullmoon == True)[0][0] + 1
        fullmoon_time = moments_check_array_full[fullmoon] # result is the check of the 3rd iteration
        fullmoon_angle = moon_phase_check[fullmoon] * 180/math.pi
    else:
        fullmoon_time = False
        fullmoon_angle = False
        print('some error look here')

    return newmoon_time, newmoon_angle, fullmoon_time, fullmoon_angle


def calculate_astro_moonphaseangle(moments):
    moments_astropy = Time(moments)
    moon_phase = astroplan.moon_phase_angle(moments_astropy).to_value()

    return moon_phase


# dictionary of objects, get data for objects at moments, return dictionary
def calculate_astro_data(moments, earth_latlng, celestial_objects_dict):
    img_astropy_location = EarthLocation(lat=earth_latlng[0]*u.deg, lon=earth_latlng[1]*u.deg) # can be outside loop because photos are near each other and using same latlng for all
    img_astropy_times = Time(moments)
    img_astropy_altazframes = AltAz(obstime=img_astropy_times, location=img_astropy_location)
    # TODO? With long lists of stars like I usually have, this would be more efficient doing ~20 moment iterations, each with a large array of star RA, Dec rather than 500+ star iterations, each with a small array of moments.
    # TODO: ChatGPT says there's a way to batch calculate the stars, which would be more efficient, but I didn't want to implement at the time.
    response_dict = copy.deepcopy(celestial_objects_dict)
    for key, value in celestial_objects_dict.items():
        if value['type'] == 'sun':
            object_SkyCoords = get_sun(img_astropy_times)
        elif value['type'] in ['planet', 'moon']:
            object_SkyCoords = get_body(key, img_astropy_times)
        elif value['type'] == 'star':
            object_SkyCoords = SkyCoord(ra=value['RA']*u.deg, dec=value['Declination']*u.deg)
        print('Calculating astro data for: ' + key)

        object_AltAzs = object_SkyCoords.transform_to(img_astropy_altazframes)

        response_dict[key]['azimuths'] = object_AltAzs.az.degree
        response_dict[key]['artifaes'] = object_AltAzs.alt.degree
        if value['type'] in ['sun', 'moon', 'planet']:
            response_dict[key]['ras'] = object_SkyCoords.ra.degree
            response_dict[key]['decs'] = object_SkyCoords.dec.degree
            response_dict[key]['distances'] = object_SkyCoords.distance.au

    return response_dict


# to display the moon partially illuminated I need the angle it appears to be illuminated.
# return degrees. straight down = sun straight below moon = 0°. (+) angle is CCW = illum up the right side. (-) angle is CW = illum up the left side.
# see diagrams for variable meanings.
def calculate_astro_moon_brightsidedirection(moon_azalts_deg, sun_azalts_deg):
    # moon_azalts[:,2] = np.where(np.greater_equal(moon_azalts[:,2], 0), moon_azalts[:,2], 0)
    moon_azalts = moon_azalts_deg * math.pi/180
    sun_azalts = sun_azalts_deg * math.pi/180

    # get abs + direction matrix for moon and sun alts
    # moon_alts_positive = np.where(moon_azalts[:,1] >= 0)
    # sun_alts_positive = np.where(sun_azalts[:,1] >= 0)
    moon_alts_abs = np.abs(moon_azalts[:,1])
    sun_alts_abs = np.abs(sun_azalts[:,1])

    # get the az_rel of the sun relative to the moon, from -180 to +180, then abs + direction matrix
    simple_subtract = np.subtract(sun_azalts[:,0], moon_azalts[:,0])
    big_angle_correction = np.where(simple_subtract > 0, -2*math.pi, 2*math.pi)
    az_rels = np.where(np.abs(simple_subtract) <= math.pi, simple_subtract, np.add(simple_subtract, big_angle_correction))
    degazrels = az_rels * 180/math.pi
    az_rels_direction = np.where(az_rels < 0, -1, 1)
    az_rels_abs = np.abs(az_rels)

    # mh = np.subtract(math.pi/2, np.arcsin(np.multiply(np.cos(moon_alts_abs), np.cos(az_rels_abs))))
    # degmh = mh * 180/math.pi
    # M = np.subtract(math.pi/2, np.arcsin(np.multiply(np.tan(moon_alts_abs), np.tan(math.pi/2 - mh))))
    # degM = M * 180/math.pi
    # A = np.subtract(math.pi/2, np.arcsin(np.multiply(np.tan(az_rels_abs), np.tan(math.pi/2 - mh))))
    # degA = A * 180/math.pi
    sh = np.subtract(math.pi/2, np.arcsin(np.multiply(np.cos(sun_alts_abs), np.cos(az_rels_abs))))
    degsh = sh * 180/math.pi
    # S = np.subtract(math.pi/2, np.arcsin(np.multiply(np.tan(sun_alts_abs), np.tan(math.pi/2 - sh))))
    # degS = S * 180/math.pi
    B = np.subtract(math.pi/2, np.arcsin(np.multiply(np.tan(az_rels_abs), np.tan(math.pi/2 - sh))))
    degB = B * 180/math.pi

    B2 = np.where(sun_azalts[:,1] >= 0, math.pi/2 - B, math.pi/2 + B)
    degB2 = B2 * 180/math.pi
    sm = np.arccos(np.add(np.multiply(np.cos(B2), np.multiply(np.sin(moon_alts_abs), np.sin(sh))), np.multiply(np.cos(moon_alts_abs), np.cos(sh))))
    degsm = sm * 180/math.pi
    moon_brightsidedirections_abs = np.arccos(np.divide(np.subtract(np.cos(sh), np.multiply(np.cos(moon_alts_abs), np.cos(sm))), np.multiply(np.sin(moon_alts_abs), np.sin(sm))))

    moon_brightsidedirections = np.multiply(moon_brightsidedirections_abs, az_rels_direction * 180/math.pi)

    return moon_brightsidedirections