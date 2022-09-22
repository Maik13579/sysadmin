import uvicorn

if __name__ == '__main__':
    uvicorn.run("dataserver:app",
                host="127.0.0.1",
                port=8000,
                reload=True,
                ssl_keyfile=r"C:\Users\janni\github\sysadmin\prototype\key.pem",
                ssl_certfile=r"C:\Users\janni\github\sysadmin\prototype\cert.pem"
                )
