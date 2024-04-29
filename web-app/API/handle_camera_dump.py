import os
import glob
import io
import sys
from cryptography.fernet import Fernet
import moviepy.editor as moviepy
from subprocess import call

symmetric_key = "zCm3lRnleW3gwiIJfRJGLPTHCrLN08bnkttZG4Wly6c="
directory = r"C:\Users\janni\github\sysadmin\videos\camera_dump"
storageDirectory = r"C:\Users\janni\github\sysadmin\videos\storage"

class DumpHandler:
    def __init__(self):
        self.read_files()

    def read_files(self):
        for root, dirs, files in os.walk(directory):
            for file in files:
                newFilename = file[:-4] + ".mp4"
                self.convert_to_mp4(file, newFilename)
                #os.remove(os.path.join(directory, file))
                #self.save_file_encrypted(newFilename)

    def convert_to_mp4(self, filename, newFilename):
        #TODO: use MP4Box for converting
        #clip = moviepy.VideoFileClip(os.path.join(directory, filename))
        #clip.write_videofile(os.path.join(directory, newFilename))
        command = "MP4Box -add {} {}".format(os.path.join(directory, filename), os.path.join(directory, newFilename))
        call([command], shell=True)
        print("vid conv")

    def save_file_encrypted(self, filename):
        print("Encrypting " + filename)
        f = Fernet(symmetric_key)
        ogFile = os.path.join(directory, filename)
        with open(ogFile, 'rb') as original:
            video = original.read()

        encrypted = f.encrypt(video)
        with open(os.path.join(storageDirectory, filename), 'wb') as encrypted_file:
            encrypted_file.write(encrypted)

        #os.remove(ogFile)

dumpHanlder = DumpHandler()
