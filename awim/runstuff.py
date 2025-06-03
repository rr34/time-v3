import awimactions
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv('.env')

# awimactions.lightroom_timelapse_XMP_process()

# awimactions.generate_metatext_files()

# awimactions.cam_calibration()

awimactions.add_camfilenames_todb()

# awimactions.generate_image_tags()

# awimactions.parse_brightstar_text()

# awimactions.db_update()

user=os.getenv('MYSQL_USER'),
host=os.getenv('MYSQL_PASSWORD'),
password=os.getenv('MYSQL_PASSWORD'),
port=os.getenv('MYSQL_PORT'),
database=os.getenv('MYSQL_DATABASE')

print(port[0])
print(user[0])