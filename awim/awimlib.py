import math
import numpy as np
import PIL
import pandas as pd
import astropytools
import metadata_tools, formatters


def generate_empty_AWIMtag_dictionary(default_units=True):
    AWIMtag_dictionary = {}
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
    AWIMtag_dictionary['awim Ref Image Size'] = []
    AWIMtag_dictionary['awim Ref Image Size Note'] = 'awim tag contains ONLY the size of the original reference image of the camera calibration - not the particular instance of the image - for two reasons: 1. The digital image itself contains its own size, so metadata size would be duplicate information, 2. The user may use some other scaled size in practice. ONLY the original reference size is necessary and appropriate for metadata.'
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
    AWIMtag_dictionary['awim Grid Direction and Arc'] = []
    AWIMtag_dictionary['awim Grid Azimuth Artifae'] = []
    AWIMtag_dictionary['awim Grid RA Dec'] = []
    AWIMtag_dictionary['awim Grid Pixel Sizes'] = []
    AWIMtag_dictionary['awim RA Dec Unit'] = 'ICRS J2000 Epoch, to thousandth of an hour, hundredth of a degree'
    AWIMtag_dictionary['awim Pixel Size Unit'] = 'Pixels per Degree; to tenth of a pixel'

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


# conversions among azarts, xyangs, pixels
# need to use Figure 1 for all of these.
def pxs_to_xyangs(AWIMtag_dictionary, pxs, imgsize_relative=1):
    pxs = np.asarray(pxs)

    input_shape = pxs.shape
    angs_direction = np.where(pxs < 0, -1, 1) # models are positive values only. Save sign. Same sign for xyangs

    pxs = np.abs(pxs).reshape(-1,2)

    if AWIMtag_dictionary['awim Models Type'] == '3d_degree_poly_fit_abs_from_center':
        pxs = pxs / imgsize_relative
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


# sph_tri convention [a, A, b, B, c, C], a to b to c is CW
# b, A, c
def spherical_solve(sph_tri):
    a = sph_tri[0]
    if isinstance(sph_tri[0], (np.ndarray, list, float)):
        a_ = True
    else:
        a_ = False
    A = sph_tri[1]
    if isinstance(A, (np.ndarray, list, float)):
        A_ = True
    else:
        A_ = False
    b = sph_tri[2]
    if isinstance(b, (np.ndarray, list, float)):
        b_ = True
    else:
        b_ = False
    B = sph_tri[3]
    if isinstance(B, (np.ndarray, list, float)):
        B_ = True
    else:
        B_ = False
    c = sph_tri[4]
    if isinstance(c, (np.ndarray, list, float)):
        c_ = True
    else:
        c_ = False
    C = sph_tri[5]
    if isinstance(C, (np.ndarray, list, float)):
        C_ = True
    else:
        C_ = False
    if a_ and b_ and c_:
        A2 = np.acos(np.divide(np.subtract(np.cos(b),np.multiply(np.cos(a),np.cos(c))),np.multiply(np.sin(a),np.sin(c))))
        if not A_:
            A = A2
        else:
            print(np.subtract(A2,A) * 180/math.pi)
        B2 = np.acos(np.divide(np.subtract(np.cos(b),np.multiply(np.cos(a),np.cos(c))),np.multiply(np.sin(a),np.sin(c))))
        if not B_:
            B = B2
        else:
            print(np.subtract(B2,B) * 180/math.pi)
        C2 = np.acos(np.divide(np.subtract(np.cos(c),np.multiply(np.cos(a),np.cos(b))),np.multiply(np.sin(a),np.sin(b))))
        if not C_:
            C = C2
        else:
            print(np.subtract(C2,C) * 180/math.pi)
    elif b_ and A_ and c_ and not (a_ or B_ or C_): 
        a = np.acos(np.add(np.multiply(np.cos(b),np.cos(c)), np.prod([np.sin(b),np.sin(c),np.cos(A)], axis=0)))
        sph_tri = [a, A, b, B, c, C]
        sph_tri = spherical_solve(sph_tri)


    return sph_tri


# xang sign matches the pxarc sign
# yang sign matches the PXDIRECTION sign (and yang_arc sign)
def xyangs_to_spherical(AWIMtag_dictionary, xyangs):
    xyangs = np.asarray(xyangs)
    input_shape = xyangs.shape
    xyangs = xyangs.reshape(-1,2)

    angs_direction = np.where(xyangs < 0, -1, 1)
    xyangs = np.abs(xyangs)
    xyangs *= math.pi/180

    # see photoshop Figure 1 for variable names
    xang_compliment = np.subtract(math.pi/2, xyangs[:,0]) # always (+) because xang < 90
    d1 = 1*np.cos(xang_compliment) # always (+), correct here because pt2 = pt1 and is on the surface of the unit sphere
    r2 = 1*np.sin(xang_compliment) # always (+), correct here because pt2 = pt1 and is on the surface of the unit sphere
    # xyangs[:,1] are the yangs and can be -180 to 180
    d2_ = np.multiply(np.cos(xyangs[:,1]), r2) # (-) for yang > 90 or < -90, meaning px behind observer
    art_seg_ = np.multiply(np.sin(xyangs[:,1]), r2) # (-) for (-) yangs
    yang_arcs = np.arcsin(art_seg_ / 1) # (-) for (-) art_seg_, hypotenuse is 1 because unit circle
# [a, A, b, B, c, C] A to B to C is CW
    sph_tri = [False, math.pi/2, yang_arcs, False, xyangs[0], False]
    sph_solved = spherical_solve([False, np.full(yang_arcs.shape, math.pi/2), yang_arcs, False, xyangs[:,0], False])
    PXDIRECTION = sph_solved[3]
    pxarc = sph_solved[0]
    C2 = sph_solved[5]


    px_dirarc = np.zeros(xyangs.shape)
    px_dirarc[:,0] = PXDIRECTION * 180/math.pi
    px_dirarc[:,1] = pxarc * 180/math.pi

    px_dirarc = px_dirarc.reshape(input_shape)

    return px_dirarc


def xyangs_to_azarts(AWIMtag_dictionary, xyangs, ref_azart_override=False):
    xyangs = np.asarray(xyangs)

    input_shape = xyangs.shape
    angs_direction = np.where(xyangs < 0, -1, 1)
    xyangs = xyangs.reshape(-1,2)
    angs_direction = angs_direction.reshape(-1,2)
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
    # todonext: also, do the xyangs range from -180 to 180 and make sense through the entire range? xyangs should be usable independent of the image to know where an object is relative to the user looking in reference direction
    xyangs = np.asarray(xyangs)

    input_shape = xyangs.shape
    xyangs = xyangs.reshape(-1,2)

    grid_angles = np.asarray(AWIMtag_dictionary['awim Grid Angles']).reshape(-1,2)
    yang_up = np.min(grid_angles[:,1])
    yang_down = np.max(grid_angles[:,1])
    xang_left = np.min(grid_angles[:,0])
    xang_right = np.max(grid_angles[:,0])

    pad = (padding_percent + 100) / 100
    inimage_array = np.empty(xyangs.shape[0], dtype=bool)
    inimage_array = np.where(np.logical_and(xyangs[:,1] > yang_up*pad, xyangs[:,1] < yang_down*pad), True, False)
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

    pxs = pxs.reshape(input_shape)

    return pxs


# gets pixel angular sizes
# TODO: the horizontal angular size of pixels near top and bottwm center within 10-100 pixels of center seem to be too small, too many pixels per degree
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