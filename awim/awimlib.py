import math
import numpy as np
import PIL
import pandas as pd
import astropytools
import metadata_tools, formatters


def generate_empty_AWIMtag_dictionary(default_units=True):
    AWIMtag_dictionary = {}
    AWIMtag_dictionary['awim Version'] = 'awim v2025-03-18'
    AWIMtag_dictionary['awim Location Coordinates'] = [-999.9, -999.9]
    AWIMtag_dictionary['awim Location Coordinates Unit'] = 'Latitude, Longitude; to 6 decimal places so ~11cm'
    AWIMtag_dictionary['awim Location Coordinates Source'] = ''
    AWIMtag_dictionary['awim Location MSL'] = -999.9
    AWIMtag_dictionary['awim Location MSL Unit'] = 'Photo meters above sea level; to 1 decimal place so 10cm'
    AWIMtag_dictionary['awim Location MSL Source'] = ''
    AWIMtag_dictionary['awim Location Terrain Elevation'] = -999.9
    AWIMtag_dictionary['awim Location Terrain Elevation Unit'] = 'Elevation of ground, meters above sea level; to 1 decimal place so 10cm'
    AWIMtag_dictionary['awim Location Terrain Elevation Source'] = ''
    AWIMtag_dictionary['awim Location AGL'] = -999.9
    AWIMtag_dictionary['awim Location AGL Unit'] = 'Meters above ground level; to 2 decimal places so 1cm'
    AWIMtag_dictionary['awim Location AGL Description'] = ''
    AWIMtag_dictionary['awim Location AGL Source'] = ''
    AWIMtag_dictionary['awim Capture Moment'] = '0000-01-01T00:00:00Z'
    AWIMtag_dictionary['awim Capture Moment Unit'] = 'Gregorian New Style Calendar in ISO 8601 YYYY-MM-DDTHH:MM:SSZ'
    AWIMtag_dictionary['awim Capture Moment Source'] = ''
    AWIMtag_dictionary['awim Models Type'] = '' # 3d_degree_poly_fit_abs_from_center
    AWIMtag_dictionary['awim Ref Pixel'] = [-999.9, -999.9]
    AWIMtag_dictionary['awim Ref Pixel Coord Type'] = 'top-left is (0,0) so standard; to 1 decimal so to tenth of a pixel'
    AWIMtag_dictionary['awim Ref Tilt'] = 0.0
    AWIMtag_dictionary['awim Ref Tilt Unit'] = '0.00 is level. -90 to 90. (+) is CCW because user moves right hand up with the camera. (+) tilt means the horizon is down on right side of image and horizon up on left side of image, vice versa for (-) tilt.'
    AWIMtag_dictionary['awim Ref Image Size in Pixels'] = []
    AWIMtag_dictionary['awim Ref Image Size in Pixels Note'] = 'awim tag contains ONLY the size of the original reference image of the camera calibration - not the particular instance of the image - for two reasons: 1. The digital image itself contains its own size, so metadata size would be duplicate information, 2. The user may use some other scaled size in practice. ONLY the original reference size is necessary and appropriate for metadata.'
    AWIMtag_dictionary['awim Angles Models Features'] = []
    AWIMtag_dictionary['awim Angles Model xang_coeffs'] = []
    AWIMtag_dictionary['awim Angles Model yang_coeffs'] = []
    AWIMtag_dictionary['awim Pixels Model Features'] = []
    AWIMtag_dictionary['awim Pixels Model xpx_coeffs'] = []
    AWIMtag_dictionary['awim Pixels Model ypx_coeffs'] = []
    AWIMtag_dictionary['awim Ref Pixel Azimuth Artifae'] = [-999.9, -999.9]
    AWIMtag_dictionary['awim Ref Pixel Azimuth Artifae Source'] = ''
    AWIMtag_dictionary['awim Ref Pixel Azimuth Artifae Unit'] = 'Degrees; to hundredth of a degree'
    AWIMtag_dictionary['awim Grid Pixels'] = []
    AWIMtag_dictionary['awim Grid Angles'] = []
    AWIMtag_dictionary['awim Grid Angles Unit'] = 'Degrees, where xang from -90 left to 90 right. yang from -180 down to 180 up and abs(yang) > 90  means hemisphere behind the camera.'
    AWIMtag_dictionary['awim Grid Direction and Arc'] = []
    AWIMtag_dictionary['awim Grid Direction and Arc Unit'] = 'Degrees, direction from -90 down to 90 up. Arc distance from -180 left to 180 right and abs(arc distance) > 90 means looking in hemisphere behind the camera.'
    AWIMtag_dictionary['awim Grid Azimuth Artifae'] = []
    AWIMtag_dictionary['awim Grid RA Dec'] = []
    AWIMtag_dictionary['awim RA Dec Unit'] = 'ICRS J2000 Epoch, to thousandth of an hour, hundredth of a degree'
    AWIMtag_dictionary['awim Grid Pixel Sizes'] = []
    AWIMtag_dictionary['awim Pixel Size Unit'] = 'Pixels per Degree; to tenth of a pixel'
    AWIMtag_dictionary['awim Image Field of View Fraction'] = -999.9
    AWIMtag_dictionary['awim Image Field of View Fraction Unit'] = 'Denominator of fraction of total that the image field of view covers. Number of images required to cover total. Minimum value of 2 without image looking behind observer.'

    if not default_units:
        AWIMtag_dictionary['awim Location Coordinates Unit'] = ''
        AWIMtag_dictionary['awim Location MSL Unit'] = ''
        AWIMtag_dictionary['awim Location Terrain Elevation Unit'] = ''
        AWIMtag_dictionary['awim Location Elevation Unit'] = ''
        AWIMtag_dictionary['awim Location AGL Unit'] = ''
        AWIMtag_dictionary['awim Capture Moment Unit'] = ''
        AWIMtag_dictionary['awim Ref Pixel Coord Type'] = ''
        AWIMtag_dictionary['awim Ref Pixel Azimuth Artifae Unit'] = ''
        AWIMtag_dictionary['awim RA Dec Unit'] = ''
        AWIMtag_dictionary['awim Pixel Size Unit'] = ''

    return AWIMtag_dictionary


# sph_tri convention [a, b, c, A, B, C], a to b to c is CCW
def _sphtri_solve(a=False, b=False, c=False, A=False, B=False, C=False):
    if isinstance(a, (list, tuple, float)):
        a = np.asarray(a)
    if isinstance(b, (list, tuple, float)):
        b = np.asarray(b)
    if isinstance(a, (list, tuple, float)):
        c = np.asarray(c)
    if isinstance(A, (list, tuple, float)):
        A = np.asarray(A)
    if isinstance(B, (list, tuple, float)):
        B = np.asarray(B)
    if isinstance(a, (list, tuple, float)):
        C = np.asarray(C)

    # SSS: a, b, c are known, and maybe some interior angles so double-check that they match by printing the difference.
    # Case 1 from Wikipedia.
    if isinstance(a, np.ndarray) and isinstance(b, np.ndarray) and isinstance(c, np.ndarray):
        A2 = np.acos(np.divide(np.subtract(np.cos(a),np.multiply(np.cos(b),np.cos(c))),np.multiply(np.sin(b),np.sin(c))))
        if not isinstance(A, np.ndarray):
            A = A2
        else:
            # print('Should be all zeros or close to zero: ' + np.subtract(A2,A) * 180/math.pi)
            pass
        B2 = np.acos(np.divide(np.subtract(np.cos(b),np.multiply(np.cos(a),np.cos(c))),np.multiply(np.sin(a),np.sin(c))))
        if not isinstance(B, np.ndarray):
            B = B2
        else:
            # print('Should be all zeros or close to zero: ' + np.subtract(B2,B) * 180/math.pi)
            pass
        C2 = np.acos(np.divide(np.subtract(np.cos(c),np.multiply(np.cos(a),np.cos(b))),np.multiply(np.sin(a),np.sin(b))))
        if not isinstance(C, np.ndarray):
            C = C2
        else:
            # print('Should be all zeros or close to zero: ' + np.subtract(C2,C) * 180/math.pi)
            pass
        sph_tri = np.array([a, b, c, A, B, C]).transpose()

    # SAS: b, c, A are known.
    # Case 2 from Wikipedia, then to case 1.
    elif isinstance(b, np.ndarray) and isinstance(c, np.ndarray) and isinstance(A, np.ndarray) and not (isinstance(a, np.ndarray) or isinstance(B, np.ndarray) or isinstance(C, np.ndarray)): 
        a = np.acos(np.add(np.multiply(np.cos(b),np.cos(c)), np.prod([np.sin(b),np.sin(c),np.cos(A)], axis=0)))
        sph_tri = _sphtri_solve(b=b, c=c, A=A, a=a)

    # SSA: b, c, B are known.
    # Case 3 from Wikipedia, then to case 7.
    elif isinstance(b, np.ndarray) and isinstance(c, np.ndarray) and isinstance(B, np.ndarray) and not (isinstance(a, np.ndarray) or isinstance(A, np.ndarray) or isinstance(C, np.ndarray)):
        C = np.multiply(np.sin(c), np.divide(np.sin(B), np.sin(b)))
        sph_tri = _sphtri_solve(b=b, c=c, B=B, C=C)

    # SSAA: b, c, B, C are known. Where unknowns are across from each other. Napier analogies.
    # Case 7 from Wikipedia.
    elif isinstance(b, np.ndarray) and isinstance(c, np.ndarray) and isinstance(B, np.ndarray) and isinstance(C, np.ndarray) and not (isinstance(a, np.ndarray) or isinstance(A, np.ndarray)):  
        a = 2 * np.atan(np.multiply(np.tan(np.add(b,c)/2), np.divide(np.cos(np.add(B,C)/2), np.cos(np.subtract(B,C)/2))))
        A = 2 * np.divide(1, np.atan(np.multiply(np.tan(np.add(B,C)/2), np.divide(np.cos(np.add(b,c)/2), np.cos(np.subtract(b,c)/2)))))
        sph_tri = np.array([a, b, c, A, B, C]).transpose()

    return sph_tri


# Index of functions:
# pxs_to_xyangs
# xyangs_to_dirarcs
# dirarcs_to_azarts TODO
# xyangs_to_azarts TODO maybe eliminate because of dirarcs
# azarts_to_dirarcs TODO
# azarts_to_xyangs TODO maybe eliminate because of dirarcs
# xyangs_inimage
# xyangs_to_pxs
# Figure 1 for all of these. TODO make variables match figure.
def pxs_to_xyangs(AWIMtag_dictionary, pxs, imgsize_correction=False):
    if isinstance(imgsize_correction, (list, tuple)):
        imgsize_tag = AWIMtag_dictionary['awim Ref Image Size in Pixels']
        aspect_ratio_img = imgsize_correction[0] / imgsize_correction[1]
        aspect_ratio_tag = imgsize_tag[0] / imgsize_tag[1]
        aspect_ratio_diff = aspect_ratio_tag - aspect_ratio_img
        print(f'Aspect ratio difference check: {aspect_ratio_diff}')
        correction_factor = imgsize_correction[0] / imgsize_tag[0] # resolution usually less than the original, < 1, so makes the px values larger below to account for the difference.
    elif isinstance(imgsize_correction, float):
        correction_factor = imgsize_correction
    else:
        correction_factor = 1

    pxs = np.asarray(pxs)
    input_shape = pxs.shape
    angs_direction = np.where(pxs < 0, -1, 1) # models are positive values only. Save sign. Same sign for xyangs
    pxs = np.abs(pxs).reshape(-1,2)

    if AWIMtag_dictionary['awim Models Type'] == '3d_degree_poly_fit_abs_from_center':
        pxs = pxs / correction_factor
        pxs_poly = np.zeros((pxs.shape[0], 9))
        pxs_poly[:,0] = pxs[:,0]
        pxs_poly[:,1] = pxs[:,1]
        pxs_poly[:,2] = np.square(pxs[:,0])
        pxs_poly[:,3] = np.multiply(pxs[:,0], pxs[:,1])
        pxs_poly[:,4] = np.square(pxs[:,1])
        pxs_poly[:,5] = np.power(pxs[:,0], 3)
        pxs_poly[:,6] = np.multiply(np.square(pxs[:,0]), pxs[:,1])
        pxs_poly[:,7] = np.multiply(pxs[:,0], np.square(pxs[:,1]))
        pxs_poly[:,8] = np.power(pxs[:,1], 3)

    xang_predict_coeff = AWIMtag_dictionary['awim Angles Model xang_coeffs']
    yang_predict_coeff = AWIMtag_dictionary['awim Angles Model yang_coeffs']

    xyangs = np.zeros(pxs.shape)
    xyangs[:,0] = np.dot(pxs_poly, xang_predict_coeff)
    xyangs[:,1] = np.dot(pxs_poly, yang_predict_coeff)

    xyangs = np.multiply(xyangs.reshape(input_shape), angs_direction)

    return xyangs


def xyangs_to_dirarcs(xyangs, return_sphtri=False):
    xyangs = np.asarray(xyangs)
    input_shape = xyangs.shape
    xyangs = xyangs.reshape(-1,2)
    xyangs_count = xyangs.shape[0]

    xangs_direction = np.where(xyangs[:,0] < 0, -1, 1)
    yangs_direction = np.where(xyangs[:,1] < 0, -1, 1)
    xyangs = np.abs(xyangs)
    xyangs *= math.pi/180

    # see photoshop Figure 1 for variable names
    # xyangs[:,0] are the xangs and can be -90 to 90
    # xang sign matches the pxarc sign
    # xyangs[:,1] are the yangs and can be -180 to 180
    # yang sign matches the PXDIRECTION sign (and yang_arc sign)
    # spherical triangle 2 parts are:
    # a is pxarc
    # b is xangs. xangs are arcs
    # c is yang_arc
    # A is 90 degrees
    # B is useful to find the area of the image on the unit sphere
    # C is PXDIRECTION
    xang_compliment = np.subtract(math.pi/2, xyangs[:,0]) # always (+) because xang < 90
    r2 = 1*np.sin(xang_compliment) # always (+), correct here because pt2 = pt1 and is on the surface of the unit sphere
    art_seg_ = np.multiply(np.sin(xyangs[:,1]), r2) # (-) for (-) yangs
    yang_arcs = np.arcsin(art_seg_ / 1) # (-) for (-) art_seg_, hypotenuse is 1 because unit circle

    # Case 2 spherical triangle SAS: b, c, A are known:
    sph_solved = _sphtri_solve(b=xyangs[:,0], c=yang_arcs, A=np.full(xyangs_count, math.pi/2))
    pxarc = sph_solved[:,0]
    PXDIRECTION = sph_solved[:,5]
    PXDIRECTION = np.where(pxarc != 0, PXDIRECTION, 0) # PXDIRECTION undefined for origin, set to zero

    px_dirarc = np.zeros([xyangs_count,2])
    px_dirarc[:,0] = np.multiply(PXDIRECTION * 180/math.pi, yangs_direction) # pxdir goes with yang direction
    px_dirarc[:,1] = np.multiply(pxarc * 180/math.pi, xangs_direction) # pxarc goes with xang direction

    px_dirarc = px_dirarc.reshape(input_shape)

    if not return_sphtri:
        return px_dirarc
    else:
        return px_dirarc, sph_solved


def dirarcs_to_azarts():
    pass


def xyangs_to_azarts(AWIMtag_dictionary, xyangs, ref_azart_override=False):
    xyangs = np.asarray(xyangs)
    input_shape = xyangs.shape
    xyangs = xyangs.reshape(-1,2)
    angs_direction = np.where(xyangs < 0, -1, 1)

    xyangs[:,0] = np.abs(xyangs[:,0])
    xyangs *= math.pi/180
    if isinstance(ref_azart_override, (list, tuple, np.ndarray)): # This gives the option to use the awim tag of a photo and point the photo in any direction.
        ref_azart_rad = np.multiply(ref_azart_override, math.pi/180)
    else:
        ref_azart_rad = np.multiply(AWIMtag_dictionary['awim Ref Pixel Azimuth Artifae'], math.pi/180)

    # see photoshop diagram of sphere, circles, and triangles for variable names
    xang_compliment = np.subtract(math.pi/2, xyangs[:,0]) # always (+) because xang < 90
    d1 = 1*np.cos(xang_compliment) # always (+) TODO: not right because d3 < 1, not = 1, because it is not on the surface of the unit sphere.
    r2 = 1*np.sin(xang_compliment) # always (+)
    ang_totalsmallcircle = np.add(ref_azart_rad[1], xyangs[:,1]) # -180 to 180
    d2_ = np.multiply(np.cos(ang_totalsmallcircle), r2) # (-) for ang_totalsmallcircle > 90 or < -90, meaning px behind observer
    art_seg_ = np.multiply(np.sin(ang_totalsmallcircle), r2) # (-) for (-) ang_totalsmallcircle
    arts = np.arcsin(art_seg_ / 1) # (-) for (-) art_seg_
    az_rel = np.subtract(math.pi/2, np.arctan(np.divide(d2_, d1))) # d2 (-) for px behind observer and therefore az_rel > 90 because will subtract (-) atan
    az_rel = np.multiply(az_rel, angs_direction[:,0])
    azs = np.mod(np.add(ref_azart_rad[0], az_rel), 2*math.pi)

    azarts = np.zeros(xyangs.shape)
    azarts[:,0] = np.multiply(azs, 180/math.pi)
    azarts[:,1] = np.multiply(arts, 180/math.pi)

    azarts = azarts.reshape(input_shape)

    return azarts


def azarts_to_dirarcs():
    pass


def azarts_to_xyangs(AWIMtag_dictionary, azarts):
    azarts = np.asarray(azarts)
    input_shape = azarts.shape
    azarts = azarts.reshape(-1,2)

    ref_px_azart = AWIMtag_dictionary['awim Ref Pixel Azimuth Artifae']

    # find az_rels, convert to -180 < x <= 180, then abs value + direction matrix
    # also need az_rel compliment angle + store which are behind camera
    # then to radians
    simple_subtract = np.subtract(azarts[:,0], ref_px_azart[0])
    big_angle_correction = np.where(simple_subtract > 0, -360, 360)
    az_rel = np.where(np.abs(simple_subtract) <= 180, simple_subtract, np.add(simple_subtract, big_angle_correction))
    az_rel_direction = np.where(az_rel < 0, -1, 1)
    az_rel_abs = np.abs(az_rel)
    az_rel_behind_observer = np.where(az_rel_abs <= 90, False, True) # true if point is behind observer - assume because camera pointed up very high past zenith or pointed very low below nether-zenith
    # Note: cannot allow az_rel_compliment (and therefore d2) to be negative because must simple_ang_totalsmallcircle be (-) if art_seg_ is (-), which is good.
    az_rel_compliment = np.where(az_rel_abs <= 90, np.subtract(90, az_rel_abs), np.subtract(az_rel_abs, 90)) # 0 to 90 angle from line perpendicular to az
    az_rel_compliment_rad = np.multiply(az_rel_compliment, math.pi/180) # (+) only, 0 to 90
    ref_px_azart_rad = np.multiply(ref_px_azart, math.pi/180)

    # artifae direction matrix, then artifaes to radians, keep sign just convert to radian
    art_direction = np.where(azarts[:,1] < 0, -1, 1)
    art_rad = np.multiply(azarts[:,1], math.pi/180)

    # trigonometry, see photoshop diagrams for variable descriptions. segment ending with underscore_ means "can be negative distance"
    art_seg_ = np.sin(art_rad) # notice: (-) for (-) arts
    d3 = np.cos(art_rad) # (+) only, because arts are always -90 to 90
    d2 = np.multiply(np.sin(az_rel_compliment_rad), d3) # (+) only
    d1 = np.multiply(np.cos(az_rel_compliment_rad), d3) # (+) only because az_rel_compliment_rad is 0 to 90
    r2 = np.sqrt(np.square(d2), np.square(art_seg_))
    xang_abs = np.subtract(math.pi/2, np.arccos(d1)) # TODO? what if xang is actually > 90? would be unusual, difficult to combine with large yang
    xang = np.multiply(xang_abs, az_rel_direction)
    pt1_art_ = np.multiply(r2, np.sin(ref_px_azart_rad[1])) # (-) for (-) cam_arts, which is good
    lower_half = np.where(art_seg_ < pt1_art_, True, False) # true if px is below middle of photo
    ang_smallcircle_fromhorizon = np.arctan(np.divide(art_seg_, d2)) # -90 to 90, (-) for (-) art_seg_, bc d2 always (+) 
    # for yang, if in front, simple, but behind observer, the angle from must be subtracted from 180 or -180 because different angle meaning see photoshop diagram
    ang_totalsmallcircle = np.where(np.logical_not(az_rel_behind_observer), ang_smallcircle_fromhorizon, np.subtract(np.multiply(art_direction, math.pi), ang_smallcircle_fromhorizon))
    yang = np.subtract(ang_totalsmallcircle, ref_px_azart_rad[1]) # simply subtract because |ang_totalsmallcircle| < 180 AND |center_azart[1]| < 90 AND if |ang_totalsmallcircle| > 90, then they are same sign

    xyangs = np.zeros(azarts.shape)
    xyangs[:,0] = np.multiply(xang, 180/math.pi)
    xyangs[:,1] = np.multiply(yang, 180/math.pi)

    xyangs = xyangs.reshape(input_shape)

    return xyangs


def xyangs_inimage(AWIMtag_dictionary, xyangs, padding_percent=0):
    xyangs = np.asarray(xyangs).reshape(-1,2)

    grid_angles = np.asarray(AWIMtag_dictionary['awim Grid Angles']).reshape(-1,2)
    yang_up = np.max(grid_angles[:,1])
    yang_down = np.min(grid_angles[:,1])
    xang_left = np.min(grid_angles[:,0])
    xang_right = np.max(grid_angles[:,0])

    pad = (padding_percent + 100) / 100
    inimage_array = np.empty(xyangs.shape[0], dtype=bool)
    inimage_array = np.where(np.logical_and(xyangs[:,1] < yang_up*pad, xyangs[:,1] > yang_down*pad), True, False)
    inimage_array = np.where(np.logical_and(inimage_array, np.logical_and(xyangs[:,0] > xang_left*pad, xyangs[:,0] < xang_right*pad)), True, False)

    return inimage_array


def xyangs_to_pxs(AWIMtag_dictionary, xyangs):
    xyangs = np.asarray(xyangs)
    input_shape = xyangs.shape
    xyangs = xyangs.reshape(-1,2)

    xyangs_direction = np.where(xyangs < 0, -1, 1)
    xyangs_abs = np.abs(xyangs)

    if AWIMtag_dictionary['awim Models Type'] == '3d_degree_poly_fit_abs_from_center':
        xyangs_poly = np.zeros((xyangs.shape[0], 9))
        xyangs_poly[:,0] = xyangs_abs[:,0]
        xyangs_poly[:,1] = xyangs_abs[:,1]
        xyangs_poly[:,2] = np.square(xyangs_abs[:,0])
        xyangs_poly[:,3] = np.multiply(xyangs_abs[:,0], xyangs_abs[:,1])
        xyangs_poly[:,4] = np.square(xyangs_abs[:,1])
        xyangs_poly[:,5] = np.power(xyangs_abs[:,0], 3)
        xyangs_poly[:,6] = np.multiply(np.square(xyangs_abs[:,0]), xyangs_abs[:,1])
        xyangs_poly[:,7] = np.multiply(xyangs_abs[:,0], np.square(xyangs_abs[:,1]))
        xyangs_poly[:,8] = np.power(xyangs_abs[:,1], 3)
    
    x_px_predict_coeff = AWIMtag_dictionary['awim Pixels Model xpx_coeffs']
    y_px_predict_coeff = AWIMtag_dictionary['awim Pixels Model ypx_coeffs']

    pxs = np.zeros(xyangs.shape)
    pxs[:,0] = np.dot(xyangs_poly, x_px_predict_coeff)
    pxs[:,1] = np.dot(xyangs_poly, y_px_predict_coeff)

    pxs = np.multiply(pxs, xyangs_direction)
    # TODO: convert this to all-positive pixel values (new function?) based on the AWIMtag dimensions since negative pixel values are not a convention anywhere

    pxs = pxs.reshape(input_shape)

    return pxs


def get_image_area(AWIMtag_dictionary, grid_sphtri2):
    grid_xyangs = np.abs(np.asarray(AWIMtag_dictionary['awim Grid Angles']) * math.pi/180)
    grid_dirarcs = np.abs(np.asarray(AWIMtag_dictionary['awim Grid Direction and Arc']) * math.pi/180)
    grid_xyangs.reshape(-1,2)
    grid_dirarcs.reshape(-1,2)
    # 4 quandrants of triangles 2 and 3 CCW from upper right
    # 4 corners are at indices 0, 6, 42, 48
    # TBLR are at indices 3, 45, 21, 27
    # See Figure 1 for spherical triangle definitions and variable names.
    # spherical triangle 2 parts are a comment in the xyangs_to_dirarcs function
    sphtri2_array = np.abs(np.array([grid_sphtri2[6,:],grid_sphtri2[0,:],grid_sphtri2[42,:],grid_sphtri2[48,:]]))
    # spherical triangle 3 parts are:
    # a is unknown and unused really, should be < xang at the bottom because the arcs are smaller farther away
    # b is yang_arc, which vertical at the center is yang
    # c is px_arc, which comes from the diarcs
    # A is PXDIRECTION_COMP
    # B is useful to find the area of the image on the unit sphere
    # C should be 90 degrees, but going to be treated as an unknown
    yang_arcs = np.array([grid_xyangs[3,1],grid_xyangs[3,1],grid_xyangs[45,1],grid_xyangs[45,1]])
    pxarcs = np.array([grid_dirarcs[6,1],grid_dirarcs[0,1],grid_dirarcs[42,1],grid_dirarcs[48,1]])
    PXDIRECTION_COMP = np.subtract(math.pi/2, sphtri2_array[:,5])
    # Case 2 spherical triangle SAS: b, c, A are known:
    sphtri3_solved = _sphtri_solve(b=yang_arcs, c=pxarcs, A=PXDIRECTION_COMP)
    B3 = sphtri3_solved[:,4]
    B2 = sphtri2_array[:,4]

    surface_area_covered = np.sum(B3) + np.sum(B2) - (4-2)*math.pi # sum of the angles minus sides minus two times pi
    fraction_covered_denominator = 4*math.pi / surface_area_covered

    return fraction_covered_denominator


# TODO: the horizontal angular size of pixels near top and bottwm center within 1-100 pixels of center seem to be too small, too many pixels per degree
def get_pixel_sizes(AWIMtag_dictionary, pxs, imgsize_relative=1):
    pxs = np.asarray(pxs)
    input_shape = pxs.shape
    pxs.reshape(-1,2)

    small_px = 100
    px_sizes_grid = np.zeros(pxs.shape)

    left_shift_pxs = np.copy(pxs)
    left_shift_pxs[:,0] -= small_px
    left_shift_angs = pxs_to_xyangs(AWIMtag_dictionary, left_shift_pxs, imgsize_relative)
    right_shift_pxs = np.copy(pxs)
    right_shift_pxs[:,0] += small_px
    right_shift_angs = pxs_to_xyangs(AWIMtag_dictionary, right_shift_pxs, imgsize_relative)
    up_shift_pxs = np.copy(pxs)
    up_shift_pxs[:,1] += small_px
    up_shift_angs = pxs_to_xyangs(AWIMtag_dictionary, up_shift_pxs, imgsize_relative)
    down_shift_pxs = np.copy(pxs)
    down_shift_pxs[:,1] -= small_px
    down_shift_angs = pxs_to_xyangs(AWIMtag_dictionary, down_shift_pxs, imgsize_relative)

    px_sizes_grid[:,0] = np.divide(small_px*2,np.abs(np.subtract(left_shift_angs[:,0],right_shift_angs[:,0])))
    px_sizes_grid[:,1] = np.divide(small_px*2,np.abs(np.subtract(up_shift_angs[:,1],down_shift_angs[:,1])))

    px_sizes_grid.reshape(input_shape)

    return px_sizes_grid


# generates the pixel coordinates of the thirds grid and top, bottom, left, right of the image, which are used in the awim tag
def get_ref_px_sixths_grid(source_image_path, ref_px):
    with PIL.Image.open(source_image_path) as source_image: # todo: do for jpg, not just png
        img_pxsize = source_image.size
    img_pointsize = np.subtract(img_pxsize, 1) # the size from pixel center to pixel center is 1 pixel smaller because it excludes all the edge pixels' outer halves

    img_half = np.divide(img_pxsize, 2)
    img_sixth = np.divide(img_pxsize, 6)
    img_center_index = np.subtract(img_half, 0.5).tolist()

    if ref_px == 'center, get from image': # todo: for ref_px allow for a cropped image where the reference pixel is not the center pixel
        ref_px = img_center_index

    img_grid_pxs = np.zeros(shape=(49,2))
    px_count = 0
    for iy in range(3,-4,-1):
        for ix in range(-3,4):
            img_grid_pxs[px_count,0] = ix*img_sixth[0] - np.sign(ix)*0.5
            img_grid_pxs[px_count,1] = iy*img_sixth[1] - np.sign(iy)*0.5
            px_count += 1

    return ref_px, img_grid_pxs


# user guesses an azimuth lined up with a structure of known orientation and this function gives the exact azimuth of the structure's side closest to the guess
def closest_to_x_sides(guess_angle, oneside_angle, number_sides):
    sides_angles = []
    for x in range(0,number_sides):
        side_angle = oneside_angle + (x/number_sides)*360
        sides_angles.append(side_angle)

    differences = []
    for side_angle in sides_angles:
        difference = guess_angle - side_angle
        difference = (difference + 180) % 360 - 180
        differences.append(abs(difference))

    min_index = differences.index(min(differences))
    correct_az = sides_angles[min_index]

    return correct_az