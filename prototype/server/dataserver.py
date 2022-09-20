import glob
import json
import io

from cryptography.fernet import Fernet
from starlette.responses import StreamingResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

symmetric_key = "zCm3lRnleW3gwiIJfRJGLPTHCrLN08bnkttZG4Wly6c="
app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
)
directory = "./videos/storage/"
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
        f = Fernet(symmetric_key)
        with open(directory + filename, 'rb') as encrypted_file:
            encrypted = encrypted_file.read()
        decrypted = f.decrypt(encrypted)
        response = StreamingResponse(io.BytesIO(decrypted), media_type="video/x-msvideo")

    return response
