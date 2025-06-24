import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from dotenv import load_dotenv
import os
import clockactions

app = FastAPI()
env_path = Path(__file__).parent/".env"
load_dotenv(dotenv_path=env_path)

origins = [os.getenv("CLIENT_ORIGIN1"), os.getenv("CLIENT_ORIGIN2")]
print('Allowed origins: ', origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/getevents')
async def getevents(request: Request):
    print('got here')
    try:
        request_dict = await request.json()
    except:
        print('some error on the post request attempt')

    response_dict = clockactions.get_events(request_dict['location'], request_dict['elevation'], request_dict['currenttime'])

    return response_dict

@app.post('/celestialinphotos')
async def celestialinphoto(request: Request):
    try:
        request_dict = await request.json()
    except:
        print('some error on the post request attempt')

    awims_dict = request_dict['awims_dict'] # keys are basenames
    first_key = next(iter(awims_dict)) # first basename
    any_awim = awims_dict[first_key]['awimTag']
    location = any_awim['awim Location Coordinates']
    if not any_awim['awim Location MSL']:
        if any_awim['awim Location Terrain Elevation'] and any_awim['awim Location AGL']:
            elevation = any_awim['awim Location Terrain Elevation'] and any_awim['awim Location AGL'] # elevation is used for events because affects horizon

    MagRankAllMax = request_dict['MagRankAllMax']
    LatDec_filter = request_dict['LatDecFilter']
    if LatDec_filter:
        LatDec_filter = location[0] # equals the latitude, which limits the stars you can see.
    
    astro_dict, astro_dict_list_type = clockactions.get_astrodata(location, request_dict['momentsarray'], request_dict['requestlist'], MagRankAllMax, LatDec_filter)
    # (the lists version of the dictionary is just where the numpy arrays have been converted to standard python lists)

    bodies_inimage_dicts = {}
    for basename, item in awims_dict.items():
        bodies_inimage_dict = clockactions.get_celestialinphoto(item['awimTag'], request_dict['momentsarray'], astro_dict)
        bodies_inimage_dicts[basename] = bodies_inimage_dict

    response_dict = {'astro dict': astro_dict_list_type, 'bodies in images dicts': bodies_inimage_dicts}

    return response_dict

if __name__ == '__main__':
    host = os.getenv("HOST", "127.0.0.1")   # fallback to localhost
    port = int(os.getenv("PORT", 8000))     # fallback to 8000d
    uvicorn.run(app, host=host, port=port)
