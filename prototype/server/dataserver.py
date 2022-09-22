import json
import io
import os

from os.path import exists
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
directory = r"C:\Users\janni\github\sysadmin\videos\storage"
archieveDir = r"C:\Users\janni\github\sysadmin\videos\archieve"
ext = "*.avi"

@app.get("/videos")
def get_videos(filename = None):
    response = None
    filenames =  []
    for root, dirs, files in os.walk(directory):
        for file in files:
            filenames.append(file)

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

@app.get("/archieve")
def get_archieve(filename = None):
    response = None
    filenames =  []
    for root, dirs, files in os.walk(archieveDir):
        for file in files:
            filenames.append(file)

    if filename is None:
        json_string = json.dumps(filenames)
        response = json_string
    else:
        if filename not in filenames:
            return {"Error, please provide a valid filename"}
        f = Fernet(symmetric_key)
        with open(archieveDir + filename, 'rb') as encrypted_file:
            encrypted = encrypted_file.read()
        decrypted = f.decrypt(encrypted)
        response = StreamingResponse(io.BytesIO(decrypted), media_type="video/x-msvideo")

    return response

@app.post("/archieve-add")
def add_to_archieve(filename):
    path = os.path.join(directory, filename)
    if not exists(path):
        return {"Error, please provide a valid filename"}

    os.rename(path, os.path.join(archieveDir, filename))
    return {"Added file to archieve"}

@app.post("/archieve-remove")
def remove_from_archieve(filename):
    path = os.path.join(archieveDir, filename)
    if not exists(path):
        return {"Error, please provide a valid filename"}

    os.rename(path, os.path.join(directory, filename))
    return {"Removed file from archieve"}
