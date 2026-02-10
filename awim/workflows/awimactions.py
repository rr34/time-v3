from typing import AnyStr, Dict
import os, shutil
import json
import numpy as np
from matplotlib import pyplot, cm
from mpl_toolkits.mplot3d import Axes3D
import datetime
import astropy.units as u
from astropy.time import Time
from core import camera
from workflows import XMPtext
from core import metadata_tools
from db import DBsqlstatements
from core import formatters
from core import astropytools


def cam_calibration():
    workingpath = os.path.join(os.getcwd(), 'working')
    image_path = os.path.join(workingpath, 'calimage.jpg')
    cal_file_path = os.path.join(workingpath, 'calspreadsheet.xlsx')

    cam_AWIMtag, filename = camera.generate_camera_AWIM_from_calibration(image_path, cal_file_path)

    file_path = os.path.join(workingpath, filename)
    with open(file_path, 'w') as json_file:
        json.dump(cam_AWIMtag, json_file, indent=4, sort_keys=True)

    return


def generate_metatext_files():
    workingpath = os.path.join(os.getcwd(), 'working')
    for file in os.listdir(workingpath):
        file_path = os.path.join(workingpath, file)
        metadata_dict = metadata_tools.get_metadata(file_path)
        file_base = os.path.splitext(file_path)[0]
        json_file_name = file_base + '.json'
        with open(json_file_name, "w") as text_file:
            json.dump(metadata_dict, text_file, indent=4, sort_keys=True)

    return


def add_camfilenames_todb() -> None:
    workingpath = os.path.join(os.getcwd(), 'working')
    camfilenames_list = []
    for file in os.listdir(workingpath):
        file_type = os.path.splitext(file)[-1]
        file_base = os.path.splitext(file)[0]
        if file_type.lower() in ('.jpg', '.png', 'jpeg'):
            file_path = os.path.join(workingpath, file)
            camfilenames_list.append(file_base)
    DBsqlstatements.insert_camfilenames(camfilenames_list)


def generate_image_tags(group_id: AnyStr) -> None:
    # 1. Get lists of photo files and list of entries in the database.
    photoshoot_basenames = DBsqlstatements.get_basenames(group_id)
    workingpath = os.path.join(os.getcwd(), 'working')
    imagebases_list = []
    images_list_iterable = []
    for file in os.listdir(workingpath):
        file_type = os.path.splitext(file)[-1]
        file_base = os.path.splitext(file)[0]
        if 'cam_awim.json' in file.lower(): # software could eventually select the correct camera awim from many based on the exif lens information from the images, but for now all photos in the batch need to be taken with the same lens.
            awim_path = os.path.join(workingpath, file)
            with open(awim_path, 'r') as json_file:
                cam_AWIMtag_dictionary = json.load(json_file) # todonext: start troubleshooting here. Possibly regenerate camawim because the one I have didn't work here.
        elif file_type.lower() in ('.jpg', '.png', 'jpeg'):
            file_path = os.path.join(workingpath, file)
            imagebases_list.append(file_base)
            if file_base in photoshoot_basenames:
                images_list_iterable.append((file_path, file_base)) # enough information to match the image file path to the correct unique entry in the database.

    # 2. Match the photo files to entries in the database and identify mismatches.
    matches = list(set(photoshoot_basenames).intersection(imagebases_list))
    lonely_files = list(set(imagebases_list) - set(photoshoot_basenames))
    lonely_shootentries = list(set(photoshoot_basenames) - set(imagebases_list))
    if len(lonely_files) == 0 and len(lonely_shootentries) == 0:
        perfect_match = True
    else:
        perfect_match = False
    if perfect_match:
        print('Photo files and shoot entries match perfectly.')
    else:
        print('Lonely files list: ' + str(lonely_files))
        print('Lonely photoshoot entries list: ' + str(lonely_shootentries))

    # 3. Iterate over the image files using the basename to get the unique corresponding entry in the database.
    for image in images_list_iterable:
        image_path = image[0]
        camimage_basename = image[1]
        photoshoot_dictionary = DBsqlstatements.get_photo(group_id, camimage_basename)
        if len(photoshoot_dictionary) == 1:
            photoshoot_dictionary = photoshoot_dictionary[0]
        elif len(photoshoot_dictionary) > 1:
            print('Duplicate entry for basename: ' + camimage_basename)
        elif len(photoshoot_dictionary) < 1:
            print('Some unknown error for : ' + camimage_basename)
        
        AWIMtag_dict, dev_dict = camera.generate_tag_from_exif_plus_misc(image_path, cam_AWIMtag_dictionary, photoshoot_dictionary)

        # 4. Save each awim tag json file, along with a copy of the image file of the same base name.
        moment_capture = formatters.format_datetime(AWIMtag_dict['awim Capture Moment'], 'to string for filename')
        photo_basename = photoshoot_dictionary['SiteName'].replace(' ', '') + '-' + moment_capture + '-' + camimage_basename.replace(' ', '').replace('_', '')
        image_filetype = os.path.splitext(image_path)[1]
        new_image_path = os.path.join(workingpath, photo_basename) + image_filetype.lower()
        json_path = os.path.join(workingpath, photo_basename) + '.json'

        with open(json_path, "w") as text_file:
            json.dump(AWIMtag_dict, text_file, indent=4, sort_keys=True)

        shutil.copy2(image_path, new_image_path) # todo: generate the tag in place, then rename the file later? copy2 preserves metadata like time stamps

        # 5. Update the DB with values caluclated for awim tag to show "scratchpad notes". These are duplicate to the awim tag values, but useful mostly for dev.
        dev_dict['Basename'] = photo_basename
        dev_dict['awimTag'] = json.dumps(AWIMtag_dict, indent=4, sort_keys=True)
        DBsqlstatements.update_scratchpad(AWIMtag_dict, dev_dict)

    return


def lightroom_timelapse_XMP_process():
    XMPdirectory = os.path.join(os.getcwd(), 'working')

    # read XMP files
    columns_to_interpolate = ['crs Temperature', 'crs Tint', 'crs Exposure2012', 'crs Contrast2012', 'crs Highlights2012', 'crs Shadows2012', 'crs Whites2012', 'crs Blacks2012', 'crs Texture', 'crs Clarity2012', 'crs Dehaze', 'crs Vibrance', 'crs Saturation']
    XMP_snapshot, lapse_latlng = XMPtext.readXMPfiles(XMPdirectory, columns_to_interpolate)
    XMP2 = XMP_snapshot.copy()
    # set variables for sun and moon calculations
    moments_list = XMP2['exif DateTimeOriginal'].values
    moments_list = formatters.format_datetime(input_datetime=moments_list, direction='from list of ISO 8601 strings')
    print(lapse_latlng)
    # calculate sun and moon values
    sun_az_list, sun_art_list = astropytools.get_AzArts(earth_latlng=lapse_latlng, moments=moments_list, celestial_object='sun')
    moon_az_list, moon_art_list = astropytools.get_AzArts(earth_latlng=lapse_latlng, moments=moments_list, celestial_object='moon')
    # convert sun and moon values to day, night, twilight labels, format numbers, add to dataframe
    day_night_twilight_list = astropytools.day_night_twilight(sun_art_list, moon_art_list)
    sun_az_list = formatters.round_to_string(sun_az_list, 'azimuth')
    sun_art_list = formatters.round_to_string(sun_art_list, 'artifae')
    moon_az_list = formatters.round_to_string(moon_az_list, 'azimuth')
    moon_art_list = formatters.round_to_string(moon_art_list, 'artifae')
    XMP2['awim SunAz'] = sun_az_list
    XMP2['awim SunArt'] = sun_art_list
    XMP2['awim MoonAz'] = moon_az_list
    XMP2['awim MoonArt'] = moon_art_list
    XMP2['awim DayNightTwilight'] = day_night_twilight_list
    # concatenate new tags together with the old tags, comma-separated
    XMP2['awim CommaSeparatedTags'] = XMP2.apply(lambda x:'%s,%s' % (x['awim CommaSeparatedTags'], x['awim DayNightTwilight']), axis=1)
    # save dataframe to CSV file
    timenow = datetime.datetime.now()
    time_string = formatters.format_datetime(timenow, 'to string for filename')
    filename = f'XMP_step1 {time_string}.csv'
    filepath = os.path.join(XMPdirectory, filename)
    XMP2.to_csv(filepath)

    # write the comma-separated tags to the XMP files
    XMPtext.addTags(XMP_snapshot, XMP2, XMPdirectory)
    print('Completed step 1 labelling XMP files with celestial events.')

    XMP_snapshot, lapse_latlng = XMPtext.readXMPfiles(XMPdirectory, columns_to_interpolate)
    XMP2 = XMP_snapshot.copy() # this seems unnecessary since XMP2 is defined in the next line, but maybe reauired to prevent XMP2 from pointing to XMP_snapshot.
    print('Interpolating the dataframe of XMP values...')
    XMP2 = XMPtext.interpolate(XMP_snapshot, columns_to_interpolate)
    # save dataframe to CSV file
    print('Saving interpolated dataframe to CSV...')
    timenow = datetime.datetime.now()
    time_string = formatters.format_datetime(timenow, 'to string for filename')
    filename = f'XMP_step2 {time_string}.csv'
    filepath = os.path.join(XMPdirectory, filename)
    XMP2.to_csv(filepath)

    # write the new values to the XMP files
    XMPtext.write_values(XMP2, columns_to_interpolate, XMPdirectory)
    print('Completed step 2 interpolating between the keyframes and writing to XMP files.')


def parse_brightstar_text():
    workingpath = os.path.join(os.getcwd(), 'working')
    image_path = os.path.join(workingpath, 'V_50.txt')
    with open(image_path, 'r') as text_file:
        brightstar_str = text_file.read()
    brightstars_df = formatters.brightstar_text_to_dataframe(brightstar_str)

    save_path = os.path.join(workingpath, 'V_50 stars 2.csv')
    brightstars_df.to_csv(save_path, index=False)

    remarks_df = formatters.brightstar_remarks_to_dataframe(brightstar_str)
    save_path = os.path.join(workingpath, 'V_50 remarks.csv')
    remarks_df.to_csv(save_path, index=False)


def db_update():
    constellation_names = [('Andromeda','And'),('Antlia','Ant'),('Apus','Aps'),('Aquarius','Aqr'),('Aquila','Aql'),('Ara','Ara'),('Aries','Ari'),('Auriga','Aur'),('Bootes','Boo'),('Caelum','Cae'),('Camelopardalis','Cam'),('Cancer','Cnc'),('Canes Venatici','CVn'),('Canis Major','CMa'),('Canis Minor','CMi'),('Capricornus','Cap'),('Carina','Car'),('Cassiopeia','Cas'),('Centaurus','Cen'),('Cepheus','Cep'),('Cetus','Cet'),('Chamaeleon','Cha'),('Circinus','Cir'),('Columba','Col'),('Coma Berenices','Com'),('Corona Australis','CrA'),('Corona Borealis','CrB'),('Corvus','Crv'),('Crater','Crt'),('Crux','Cru'),('Cygnus','Cyg'),('Delphinus','Del'),('Dorado','Dor'),('Draco','Dra'),('Equuleus','Equ'),('Eridanus','Eri'),('Fornax','For'),('Gemini','Gem'),('Grus','Gru'),('Hercules','Her'),('Horologium','Hor'),('Hydra','Hya'),('Hydrus','Hyi'),('Indus','Ind'),('Lacerta','Lac'),('Leo','Leo'),('Leo Minor','LMi'),('Lepus','Lep'),('Libra','Lib'),('Lupus','Lup'),('Lynx','Lyn'),('Lyra','Lyr'),('Mensa','Men'),('Microscopium','Mic'),('Monoceros','Mon'),('Musca','Mus'),('Norma','Nor'),('Octans','Oct'),('Ophiuchus','Oph'),('Orion','Ori'),('Pavo','Pav'),('Pegasus','Peg'),('Perseus','Per'),('Phoenix','Phe'),('Pictor','Pic'),('Pisces','Psc'),('Piscis Austrinus','PsA'),('Puppis','Pup'),('Pyxis','Pyx'),('Reticulum','Ret'),('Sagitta','Sge'),('Sagittarius','Sgr'),('Scorpius','Sco'),('Sculptor','Scl'),('Scutum','Sct'),('Serpens','Ser'),('Sextans','Sex'),('Taurus','Tau'),('Telescopium','Tel'),('Triangulum','Tri'),('Triangulum Australe','TrA'),('Tucana','Tuc'),('Ursa Major','UMa'),('Ursa Minor','UMi'),('Vela','Vel'),('Virgo','Vir'),('Volans','Vol'),('Vulpecula','Vul')]
    for qms in constellation_names:
        qms = (qms[1],qms[0])
        print(qms)
        DBsqlstatements.db_temp(qms)


# ----- unknown below this line -----
# Would be nice to make this function work again to see the angular shape of lenses.
def display_camera_lens_shape(awim_dictionary):
    # open the object from a file, run its __repr__ method, use it to predict and plot its own predictions
    this_camera_filename = askopenfilename()
    camera_aim_pickle = open(this_camera_filename, 'rb')
    this_camera = camera_aim_pickle # used to be pickle.load
    camera_aim_pickle.close()

    this_camera.represent_camera()

    plot_dims = [160, 90]
    x_axis_px = np.linspace(0, this_camera.center_px[0], plot_dims[0])
    y_axis_px = np.linspace(0, this_camera.center_px[1], plot_dims[1])
    px_x_axis, px_y_axis = np.meshgrid(x_axis_px, y_axis_px)
    px_meshgrid = np.empty([plot_dims[1], plot_dims[0], 2])
    px_meshgrid[:,:,0] = px_x_axis
    px_meshgrid[:,:,1] = px_y_axis
    xyangs_predicted = this_camera.px_xyangs_models_convert(input=px_meshgrid, direction='px_to_xyangs')

    fig1, (ax1, ax2) = pyplot.subplots(1, 2, subplot_kw={"projection": "3d"})
    fig1.suptitle('x,y Angles from Pixels')
    ax1.set_title('x Angle')
    ax1.plot_surface(px_meshgrid[:,:,0], px_meshgrid[:,:,1], xyangs_predicted[:,:,0], cmap = cm.viridis)
    ax1.scatter(this_camera.ref_df['x_px'], this_camera.ref_df['y_px'], this_camera.ref_df['xang'], s=50, c='purple')
    ax2.set_title('y Angle')
    ax2.plot_surface(px_meshgrid[:,:,0], px_meshgrid[:,:,1], xyangs_predicted[:,:,1], cmap=cm.inferno)
    ax2.scatter(this_camera.ref_df['x_px'], this_camera.ref_df['y_px'], this_camera.ref_df['yang'], s=50, c='red')

    xang_axis = np.linspace(this_camera.xyangs_edges[3,0], this_camera.xyangs_edges[1,0], plot_dims[0])
    yang_axis = np.linspace(this_camera.xyangs_edges[2,1], this_camera.xyangs_edges[0,1], plot_dims[1])
    xang_axis, yang_axis = np.meshgrid(xang_axis, yang_axis)
    xyangs_meshgrid = np.empty([plot_dims[1], plot_dims[0], 2])
    xyangs_meshgrid[:,:,0] = xang_axis
    xyangs_meshgrid[:,:,1] = yang_axis
    px_predicted = this_camera.px_xyangs_models_convert(input=xyangs_meshgrid, direction='xyangs_to_px')

    fig2, (ax3, ax4) = pyplot.subplots(1, 2, subplot_kw={"projection": "3d"})
    fig2.suptitle('Pixels from x,y Angles')
    ax3.set_title('x Pixel')
    ax3.plot_surface(xyangs_meshgrid[:,:,0], xyangs_meshgrid[:,:,1], px_predicted[:,:,0], cmap = cm.viridis)
    ax3.scatter(this_camera.ref_df['xang'], this_camera.ref_df['yang'], this_camera.ref_df['x_px'], s=50, c='purple')
    ax4.set_title('y Pixel')
    ax4.plot_surface(xyangs_meshgrid[:,:,0], xyangs_meshgrid[:,:,1], px_predicted[:,:,1], cmap=cm.inferno)
    ax4.scatter(this_camera.ref_df['xang'], this_camera.ref_df['yang'], this_camera.ref_df['y_px'], s=50, c='red')

    pyplot.show()


def locations_cluster():
    auto_cluster_radius_m = 1000.0
    town_square_radius_m = 10000.0
    earth_radius_m = 6371008.8

    photos = DBsqlstatements.get_photos_with_coordinates()
    if not photos:
        return

    photo_ids = np.array([row['photo_id'] for row in photos], dtype=np.int64)
    latitudes = np.array([row['Latitude'] for row in photos], dtype=np.float64)
    longitudes = np.array([row['Longitude'] for row in photos], dtype=np.float64)

    def haversine_m(lat1, lon1, lat2, lon2):
        lat1_rad = np.deg2rad(lat1)
        lon1_rad = np.deg2rad(lon1)
        lat2_rad = np.deg2rad(lat2)
        lon2_rad = np.deg2rad(lon2)
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2.0) ** 2
        return 2.0 * earth_radius_m * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))

    update_rows_with_distance = []
    remaining_mask = np.ones(photo_ids.size, dtype=bool)

    town_square_rows = DBsqlstatements.get_location_centers('town_square')
    if town_square_rows:
        town_square_ids = np.array([int(row['loc_id']) for row in town_square_rows], dtype=np.int64)
        town_square_lats = np.array([float(row['CenterLatitude']) for row in town_square_rows], dtype=np.float64)
        town_square_lons = np.array([float(row['CenterLongitude']) for row in town_square_rows], dtype=np.float64)
        town_square_distances_matrix = haversine_m(
            latitudes[:, np.newaxis],
            longitudes[:, np.newaxis],
            town_square_lats[np.newaxis, :],
            town_square_lons[np.newaxis, :],
        )
        nearest_town_square_index = np.argmin(town_square_distances_matrix, axis=1)
        nearest_town_square_distance = town_square_distances_matrix[np.arange(photo_ids.size), nearest_town_square_index]
        town_square_mask = nearest_town_square_distance <= town_square_radius_m
        if np.any(town_square_mask):
            update_rows_with_distance.extend(
                (int(town_square_ids[loc_idx]), float(distance_m), int(photo_id))
                for photo_id, loc_idx, distance_m in zip(
                    photo_ids[town_square_mask],
                    nearest_town_square_index[town_square_mask],
                    nearest_town_square_distance[town_square_mask],
                )
            )
            remaining_mask[town_square_mask] = False

    auto_cluster_rows = DBsqlstatements.get_location_centers('auto_cluster')
    if auto_cluster_rows:
        remaining_indices = np.flatnonzero(remaining_mask)
        if remaining_indices.size > 0:
            auto_cluster_ids = np.array([int(row['loc_id']) for row in auto_cluster_rows], dtype=np.int64)
            auto_cluster_lats = np.array([float(row['CenterLatitude']) for row in auto_cluster_rows], dtype=np.float64)
            auto_cluster_lons = np.array([float(row['CenterLongitude']) for row in auto_cluster_rows], dtype=np.float64)
            remaining_lats = latitudes[remaining_indices]
            remaining_lons = longitudes[remaining_indices]
            auto_cluster_distances_matrix = haversine_m(
                remaining_lats[:, np.newaxis],
                remaining_lons[:, np.newaxis],
                auto_cluster_lats[np.newaxis, :],
                auto_cluster_lons[np.newaxis, :],
            )
            nearest_auto_cluster_index = np.argmin(auto_cluster_distances_matrix, axis=1)
            nearest_auto_cluster_distance = auto_cluster_distances_matrix[np.arange(remaining_indices.size), nearest_auto_cluster_index]
            auto_cluster_mask = nearest_auto_cluster_distance <= auto_cluster_radius_m
            if np.any(auto_cluster_mask):
                matched_photo_indices = remaining_indices[auto_cluster_mask]
                update_rows_with_distance.extend(
                    (int(auto_cluster_ids[loc_idx]), float(distance_m), int(photo_id))
                    for photo_id, loc_idx, distance_m in zip(
                        photo_ids[matched_photo_indices],
                        nearest_auto_cluster_index[auto_cluster_mask],
                        nearest_auto_cluster_distance[auto_cluster_mask],
                    )
                )
                remaining_mask[matched_photo_indices] = False

    remaining_indices = np.flatnonzero(remaining_mask)
    if remaining_indices.size == 0:
        DBsqlstatements.update_photo_locations_with_distance(update_rows_with_distance)
        return

    remaining_photo_ids = photo_ids[remaining_indices]
    remaining_latitudes = latitudes[remaining_indices]
    remaining_longitudes = longitudes[remaining_indices]

    lat0 = np.deg2rad(np.mean(remaining_latitudes))
    m_per_deg_lat = 111132.0
    m_per_deg_lon = 111320.0 * np.cos(lat0)
    x_coords = remaining_longitudes * m_per_deg_lon
    y_coords = remaining_latitudes * m_per_deg_lat
    xy = np.column_stack((x_coords, y_coords))

    def cluster_radius(indices: np.ndarray) -> float:
        cluster_points = xy[indices]
        center = cluster_points.mean(axis=0)
        distances = np.linalg.norm(cluster_points - center, axis=1)
        return float(distances.max())

    def split_cluster(indices: np.ndarray):
        if indices.size <= 1:
            return indices, np.array([], dtype=np.int64)

        cluster_points = xy[indices]
        center = cluster_points.mean(axis=0)
        dists = np.linalg.norm(cluster_points - center, axis=1)
        seed1_idx = int(np.argmax(dists))
        seed1 = cluster_points[seed1_idx]
        seed2_idx = int(np.argmax(np.linalg.norm(cluster_points - seed1, axis=1)))
        seed2 = cluster_points[seed2_idx]

        if seed1_idx == seed2_idx:
            return indices[:1], indices[1:]

        for _ in range(8):
            d1 = np.sum((cluster_points - seed1) ** 2, axis=1)
            d2 = np.sum((cluster_points - seed2) ** 2, axis=1)
            left_mask = d1 <= d2
            right_mask = ~left_mask
            if not left_mask.any() or not right_mask.any():
                sorted_idx = np.argsort(d1 - d2)
                half = indices.size // 2
                left_indices = indices[sorted_idx[:half]]
                right_indices = indices[sorted_idx[half:]]
                return left_indices, right_indices
            seed1 = cluster_points[left_mask].mean(axis=0)
            seed2 = cluster_points[right_mask].mean(axis=0)

        return indices[left_mask], indices[right_mask]

    pending = [np.arange(remaining_photo_ids.size, dtype=np.int64)]
    clusters = []
    while pending:
        current = pending.pop()
        if current.size == 0:
            continue
        if cluster_radius(current) <= auto_cluster_radius_m or current.size == 1:
            clusters.append(current)
            continue
        left, right = split_cluster(current)
        if left.size == 0 or right.size == 0:
            clusters.append(current)
            continue
        pending.append(left)
        pending.append(right)

    run_tag = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    location_rows = []
    cluster_centers = []
    for cluster_idx, cluster in enumerate(clusters, start=1):
        center_lat = float(remaining_latitudes[cluster].mean())
        center_lon = float(remaining_longitudes[cluster].mean())
        location_name = f'auto_cluster_{run_tag}_{cluster_idx}'
        location_rows.append((location_name, 'auto_cluster', center_lat, center_lon))
        cluster_centers.append((location_name, center_lat, center_lon, cluster))

    DBsqlstatements.insert_locations(location_rows)

    inserted_rows = DBsqlstatements.get_locations_by_name_prefix(f'auto_cluster_{run_tag}_%')
    loc_id_by_name = {row['LocationName']: row['loc_id'] for row in inserted_rows}

    for location_name, center_lat, center_lon, cluster in cluster_centers:
        loc_id = loc_id_by_name.get(location_name)
        if loc_id is None:
            continue
        cluster_lats = remaining_latitudes[cluster]
        cluster_lons = remaining_longitudes[cluster]
        distances = haversine_m(cluster_lats, cluster_lons, center_lat, center_lon)
        update_rows_with_distance.extend(
            (int(loc_id), float(distance_m), int(remaining_photo_ids[idx]))
            for idx, distance_m in zip(cluster, distances)
        )

    DBsqlstatements.update_photo_locations_with_distance(update_rows_with_distance)
