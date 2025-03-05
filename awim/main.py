import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import clockactions

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

@app.post('/getevents')
async def getevents(request: Request):
    try:
        request_dict = await request.json()
    except:
        print('some error on the post request attempt')

    response_dict = clockactions.get_events(request_dict['location'], request_dict['elevation'], request_dict['currenttime'])
    response_dict_json = json.dumps(response_dict) # TODO: maybe use orjson at some point? because faster

    return response_dict_json

@app.post('/getsun')
async def getsun(request: Request):
    try:
        request_dict = await request.json()
    except:
        print('some error on the post request attempt')

    response_dict = clockactions.get_events(request_dict['location'], request_dict['elevation'], request_dict['currenttime'])
    response_dict_json = json.dumps(response_dict) # TODO: maybe use orjson at some point? because faster

    return response_dict_json

if __name__ == '__main__':
    uvicorn.run(app)