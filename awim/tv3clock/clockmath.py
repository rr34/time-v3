from io import StringIO
import PIL
from PIL.ImageFilter import BoxBlur
import numpy as np
import pandas as pd

# these functions were used in the original clock made entirely in Python with a python GUI

# output dictionary of available images
# each image with a dictionary of celestial objects
# each object with a numpy array of placement data by moment# for a single location, list of moments, images, celestial objects
# 1. return a numpy array of standard astro data by moment
# 2. and a dictionary of the images, each with a dictionary of celestial objects, each with a numpy array of image-specific data
# the data in the rows of the numpy arrays correspond to the moments in column 0 of the astro data array
def calculate_astro_data_to_images(moments, celestial_objs_dictionary, awim_imgs_list, img_dims, sun_moon_size_px):
    imgs_objs_dictionary = {}
    tracker_list = []
    for awim_filename in awim_imgs_list:
        imgs_objs_dictionary[awim_filename] = {} # bc dictionary of dictionaries
        awim_png = PIL.Image.open(awim_filename)
        awim_dictionary_text = awim_png.text
        awim_img_size = awim_png.size
        awim_img_center = np.divide(awim_img_size, 2)
        awim_image_object = astroimage.AstroImage(awim_dictionary_text) # create the awim object for the image
        pxs_per_minute = awim_image_object.pxsperdeg_ballpark * 15/60
        awim_png_littleblur = awim_png.filter(filter=BoxBlur(pxs_per_minute*5))
        awim_png_bigblur = awim_png.filter(filter=BoxBlur(pxs_per_minute*17))
        # awim_png_littleblur.save(fp=awim_filename+'littleblur.png') # TODO comment this out
        # awim_png_bigblur.save(fp=awim_filename+'bigblur.png') # TODO comment this out
        # img_alpha_channel = np.array(list(awim_png_bigblur.getdata(band=3))).reshape(awim_png_bigblur.size[::-1])
        
        for key, value in celestial_objs_dictionary.items():
            img_astro_data_array = np.zeros((moments.size, 8)) # empty array of appropriate size. One array per celestial object per image. Images x objects number of these arrays.
            # each row:
            # 0,1 KVpx
            # 2 PSpx y values only. x are same as KVpx
            # 3 object within image bounds True/False
            # 4 opacity on little blurred alpha channel of image
            # 5 opacity on big blurred alpha channel of image
            # 6 px distance from center
            img_astro_data_array[:,[0,1]] = awim_image_object.azalts_to_pxs(value[:,[1,2]], 'KVpx')
            img_astro_data_array[:,2] = np.subtract(img_dims[1], img_astro_data_array[:,[1]]).flatten() # PSpx y
            img_astro_data_array[:,3] = (img_astro_data_array[:,0]>0-sun_moon_size_px[0]/2)&(img_astro_data_array[:,0]<awim_img_size[0]+sun_moon_size_px[0]/2)&(img_astro_data_array[:,1]>0-sun_moon_size_px[1]/2)&(img_astro_data_array[:,1]<awim_img_size[1]+sun_moon_size_px[1]/2)
            index_counter = 0
            for PSpx in img_astro_data_array[:,[0,2]]:
                if (0<PSpx[0]<img_dims[0])&(0<PSpx[1]<img_dims[1]):
                    img_astro_data_array[index_counter,4] = awim_png_littleblur.getpixel(tuple(PSpx))[3]
                    img_astro_data_array[index_counter,5] = awim_png_bigblur.getpixel(tuple(PSpx))[3]
                else:
                    img_astro_data_array[index_counter,4] = 255
                    img_astro_data_array[index_counter,5] = 255
                index_counter += 1
            img_astro_data_array[:,6] = np.sqrt(np.add(np.square(np.subtract(img_astro_data_array[:,0], awim_img_center[0])), np.square(np.subtract(img_astro_data_array[:,1], awim_img_center[1]))))

            imgs_objs_dictionary[awim_filename][key] = img_astro_data_array
            
            track_condition = np.where(img_astro_data_array[:,4] < 255) # indexes of objects on the image not behind little blur opacity
            to_save = np.concatenate((np.array(track_condition[0]).reshape(-1,1), np.full((track_condition[0].size, 1), awim_filename), np.full((track_condition[0].size, 1), key), value[track_condition][:,[0,2]], img_astro_data_array[track_condition][:,4:7]), axis=1)
            tracker_list.append(to_save.reshape(-1).tolist()) # awim filled in

    tracker_list_flattened = [val for sublist in tracker_list for val in sublist]
    tracker_list_oflists = zip(*[iter(tracker_list_flattened)]*8)
    # tracker_array = np.array(tracker_list_flattened).reshape(-1,7) # this works also but the list thing skips making an array
    dictionary_TOC = pd.DataFrame(tracker_list_oflists, columns=['step_count', 'awim', 'object', 'moment', 'altitude', 'little blur opacity', 'big blur opacity', 'px distance from center'])
    dictionary_TOC['step_count'] = dictionary_TOC['step_count'].astype(int)
    dictionary_TOC[['altitude', 'little blur opacity', 'big blur opacity', 'px distance from center']] = dictionary_TOC[['altitude', 'little blur opacity', 'big blur opacity', 'px distance from center']].astype(float)
    dictionary_TOC.to_csv('tracker dataframe.csv') # TODO comment this out

    return imgs_objs_dictionary, dictionary_TOC


def awim_chooser(animation_type, moments, celestial_objs_dictionary, imgs_objs_dictionary, TOC_df, placeholder_image):
    first_moment = moments[0]
    last_moment = moments[-1]
    bymoment_awims = np.full(moments.size, False, dtype=list)

    # fill in the awims for sun
    sun_df = TOC_df[TOC_df['object']=='sun']
    # find with medium opacity, meaning near objects in image.
    # find sunrise
    sun_df_sunriseandset = sun_df[(sun_df['altitude'] > -6) & (sun_df['altitude'] < 6)]
    sun_df_sunriseandset.sort_values('px distance from center', ascending=True)
    riseandset_pick = sun_df_sunriseandset['awim'].values[0]
    TOC_indexes = sun_df_sunriseandset.index.tolist()
    for TOC_index in TOC_indexes:
        pick_step = TOC_df.iloc[TOC_index]['step_count']
        if not bymoment_awims[pick_step]:
            bymoment_awims[pick_step] = riseandset_pick

    sun_df_opacityfinder = (sun_df['big blur opacity'] > 0) & (sun_df['big blur opacity'] < 200)
    awims_sun_opacity = sun_df[sun_df_opacityfinder]
    awim_sun_opacity_picks = awims_sun_opacity['awim'].value_counts().index.tolist()
    for opacity_pick in awim_sun_opacity_picks:
        pick_steps = sun_df[sun_df['awim']==opacity_pick]['step_count'].values
        bymoment_awims[pick_steps] = np.where(np.logical_not(bymoment_awims[pick_steps]), opacity_pick, bymoment_awims[pick_steps])

    sun_df_sorted_pxcenterdist = sun_df.sort_values('px distance from center', ascending=True)
    # sun_df.to_csv('sun px dist from center.csv') # TODO comment this out
    sorted_df_indexes = sun_df_sorted_pxcenterdist.index.tolist()
    for TOC_index in sorted_df_indexes:
        pick_step = TOC_df.iloc[TOC_index]['step_count']
        if not bymoment_awims[pick_step]:
            bymoment_awims[pick_step] = TOC_df.iloc[TOC_index]['awim']
    
    # fill awims for moon
    moon_df = TOC_df[TOC_df['object']=='moon']
    # TODO make the list only unique values
    moon_df.sort_values('px distance from center', ascending=True, inplace=True)
    moon_df.to_csv('moon picks dataframe.csv') # TODO comment this out
    sorted_df_indexes = moon_df.index.tolist()
    for TOC_index in sorted_df_indexes:
        pick_step = TOC_df.iloc[TOC_index]['step_count']
        if not bymoment_awims[pick_step]:
            bymoment_awims[pick_step] = TOC_df.iloc[TOC_index]['awim']

    bymoment_awims[:] = np.where(np.logical_not(bymoment_awims), placeholder_image, bymoment_awims)

    awims_with_sun = pd.unique(sun_df['awim'])
    
    return bymoment_awims


# converts center position of image to bottom left coordinate of image to place image
# TODO orient the image based on desired angle
# TODO size the image based on multiple desired coords in image 
def img_placer(pos_want, img_dims, obj_dims):
    x_poshint = float((pos_want[0]-obj_dims[0]/2) / img_dims[0]) # float required to convert to regular python float instead of numpy float64
    y_poshint = float((pos_want[1]-obj_dims[1]/2) / img_dims[1]) # float required to convert to regular python float instead of numpy float64
    if not ((0 <= x_poshint <= 1) and (0 <= y_poshint <= 1)):
        x_poshint = 1.0
        y_poshint = 1.0
    pos_dictionary = {'x':x_poshint, 'y':y_poshint}
    # pos = (pos_want[0]-img_size[0]/2, pos_want[1]-img_size[1]/2)

    return pos_dictionary