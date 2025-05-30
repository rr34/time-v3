import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import clockactions

app = FastAPI()
load_dotenv('.env')

origins = [os.getenv("CLIENT_ORIGIN1"), os.getenv("CLIENT_ORIGIN2")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/getevents')
async def getevents(request: Request):
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

    # use any awimtag to get the astro data because current assumption is the photos are geographically close to one another.
    astro_dict, astro_dict_lists = clockactions.get_astrodata(request_dict['awims_dict'][0]['awimTag'], request_dict['momentsarray'], request_dict['requestlist'])

    bodies_inimage_dicts = {}
    for key, value in request_dict['awims_dict'].items():
        bodies_inimage_dict = clockactions.get_celestialinphoto(value['awimTag'], request_dict['momentsarray'], astro_dict)
        bodies_inimage_dicts[key] = bodies_inimage_dict

    response_dict = {'astro dict': astro_dict_lists, 'bodies in image dicts': bodies_inimage_dicts}

    return response_dict

if __name__ == '__main__':
    uvicorn.run(app)