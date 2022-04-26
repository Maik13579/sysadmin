FROM python:3 as base

WORKDIR /usr/src
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  libgl1\
  python3-opencv
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY network .

FROM base as camera
COPY camera .

FROM base as server
COPY server .

FROM base as master
COPY master .
