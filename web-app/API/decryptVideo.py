import sys
import os
from cryptography.fernet import Fernet

symmetric_key = "zCm3lRnleW3gwiIJfRJGLPTHCrLN08bnkttZG4Wly6c=";
directory = r"C:\Users\janni\github\sysadmin\videos\storage"
tempDir = r"C:\Users\janni\github\sysadmin\videos\temp"

filename = sys.argv[1]
f = Fernet(symmetric_key)
with open(os.path.join(directory, filename), 'rb') as encrypted_file:
    encrypted = encrypted_file.read()
decrypted = f.decrypt(encrypted)
with open(os.path.join(tempDir, filename), 'wb') as encrypted_file:
    encrypted_file.write(decrypted)
#response = StreamingResponse(io.BytesIO(decrypted), media_type="video/x-msvideo")

sys.stdout.flush()
