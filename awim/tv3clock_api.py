import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from dotenv import load_dotenv
import os
from tv3clock import clockactions

app = FastAPI()
env_path = Path(__file__).parent/".env"
load_dotenv(dotenv_path=env_path)

origins = [o.strip() for o in os.getenv("CLIENT_ORIGINS", "").split(",") if o.strip()]
print('Allowed origins: ', origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_location_and_elevation_from_awim(awim_tag):
    if not isinstance(awim_tag, dict):
        return None, None
    location = awim_tag.get('awim Location Coordinates')
    elevation = awim_tag.get('awim Location MSL')
    if elevation is None:
        terrain = awim_tag.get('awim Location Terrain Elevation')
        agl = awim_tag.get('awim Location AGL')
        if terrain is not None and agl is not None:
            elevation = terrain + agl
    return location, elevation

@app.post('/getevents')
async def getevents(request: Request):
    print('got here')
    try:
        request_dict = await request.json()
    except:
        print('some error on the post request attempt')

    response_dict = clockactions.get_events(request_dict['location'], request_dict['elevation'], request_dict['currenttime'])

    sunmoon_details = clockactions.get_sunmoon_details(request_dict['location'], request_dict['elevation'], request_dict['nowmoments_clockstrings'])
    response_dict['sunmoon_details'] = sunmoon_details

    return response_dict


@app.post('/glockenspiel')
async def glockenspiel(request: Request):
    try:
        request_dict = await request.json()
    except Exception:
        return {"error": "Invalid JSON"}

    gs_type = request_dict.get('type')
    if gs_type not in ['moonrise_month', 'sunset_year']:
        return {"error": f"Unknown glockenspiel type: {gs_type}"}

    awim_tag = request_dict.get('awimTag')
    if awim_tag:
        location, elevation = _get_location_and_elevation_from_awim(awim_tag)
    else:
        location = request_dict.get('location')
        elevation = request_dict.get('elevation')

    if location is None:
        return {"error": "location required"}

    if elevation is None:
        elevation = 0

    currenttime = request_dict.get('currenttime')
    if not currenttime:
        return {"error": "currenttime required"}

    if gs_type == 'moonrise_month':
        count = 30
        gridpts = 50

        momentsarray = clockactions.get_glockenspiel_moonrise_month(
            location,
            elevation,
            currenttime,
            count=count,
            gridpts=gridpts,
        )
    else:
        days = 366
        gridpts = 50

        momentsarray = clockactions.get_glockenspiel_sunset_year(
            location,
            elevation,
            currenttime,
            days=days,
            gridpts=gridpts,
        )

    return {"momentsarray": momentsarray, "count": len(momentsarray)}

@app.post('/celestialinphotos')
async def celestialinphoto(request: Request):
    try:
        request_dict = await request.json()
        awims_dict = request_dict['awims_dict'] # keys are basenames
        first_key = next(iter(awims_dict)) # first basename
        any_awim = awims_dict[first_key]['awimTag']
        location, elevation = _get_location_and_elevation_from_awim(any_awim)
        if elevation is None:
            elevation = 0

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
    except Exception as e:
        print(f'Error in /celestialinphotos: {e}')
        return {"error": str(e)} # return a json response with CORS headers intact


if __name__ == '__main__':
    host = os.getenv("HOST", "127.0.0.1")   # fallback to localhost
    port = int(os.getenv("PORT", 8000))     # fallback to 8000
    uvicorn.run(app, host=host, port=port)
