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

@app.post('/celestialinphoto')
async def celestialinphoto(request: Request):
    try:
        request_dict = await request.json()
    except:
        print('some error on the post request attempt')

    astro_dict, bodies_inimage_dict = clockactions.get_celestialinphoto(request_dict['awim'], request_dict['momentsarray'], request_dict['requestlist'])

    if request_dict['returnastro'] == 'true':
        response_dict = {'astro dict': astro_dict, 'bodies in image dict': bodies_inimage_dict}
    elif request_dict['returnastro'] == 'false':
        response_dict = {'bodies in image dict': bodies_inimage_dict}

    return response_dict

if __name__ == '__main__':
    uvicorn.run(app)