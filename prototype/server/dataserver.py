import glob
import json
import io

from starlette.responses import StreamingResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
)
directory = "./videos/"
ext = "*.avi"    

@app.get("/videos")
def get_videos(filename = None):
    response = None
    paths = glob.glob(directory + ext)
    filenames =  []
    for path in paths:
        name = path.replace(directory, "")
        filenames.append(name)
    if filename is None:
        json_string = json.dumps(filenames)
        response = json_string
    else:
        if filename not in filenames:
            return {"Error, please provide a valid filename"}
        video = open(directory + filename, mode="rb")
        response = StreamingResponse(video, media_type="video/x-msvideo")

    return response