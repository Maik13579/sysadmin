#!/usr/bin/python
import os
import signal
import paramiko
from paramiko import SSHClient
from scp import SCPClient
from io import BytesIO
import numpy as np
import picamera
import picamera.array
import datetime
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(message)s")
LOG = logging.getLogger("capture_motion")

def signal_term_handler(signal, frame):
  LOG.info('shutting down ...')
  sys.exit(0)
signal.signal(signal.SIGTERM, signal_term_handler)


HOST = '192.168.0.97'
HOST_USER = 'pi'
PASSWORD = 'baum'
LOCAL_IMG_PATH = '/home/pi-cam1/captured'
REMOTE_IMG_PATH = '/home/pi/Documents/sysadmin/videos/camera_dump'

minimum_still_interval = 3
clip_time = 10
motion_detected = False
recording = False
last_still_capture_time = datetime.datetime.now()

# The 'analyse' method gets called on every frame processed while picamera
# is recording h264 video.
# It gets an array (see: "a") of motion vectors from the GPU.
class DetectMotion(picamera.array.PiMotionAnalysis):
  def analyse(self, a):
    global minimum_still_interval, motion_detected, last_still_capture_time
    if recording:
        pass
    elif datetime.datetime.now() > last_still_capture_time + \
        datetime.timedelta(seconds=minimum_still_interval):
      a = np.sqrt(
        np.square(a['x'].astype(np.float64)) +
        np.square(a['y'].astype(np.float64))
      ).clip(0, 255).astype(np.uint8)
      # experiment with the following "if" as it may be too sensitive ???
      # if there're more than 10 vectors with a magnitude greater
      # than 60, then motion was detected:
      if (a > 60).sum() > 10:
        LOG.info('motion detected at: %s' % datetime.datetime.now().strftime('%Y-%m-%dT%H.%M.%S.%f'))
        motion_detected = True

def anotate_time(dt):
    start = datetime.datetime.now()
    while (datetime.datetime.now() - start).seconds < dt:
        camera.annotate_text = datetime.datetime.now().strftime('%d.%m.%Y - %H:%M.%S')
        camera.wait_recording(0.1)

camera = picamera.PiCamera(resolution = (640, 480), framerate = 24)
stream = picamera.PiCameraCircularIO(camera, seconds=clip_time)
with DetectMotion(camera) as output:
  try:
    # record video to nowhere, as we are just trying to capture images:
    camera.start_recording(stream, format='h264', motion_output=output)
    while True:
      while not motion_detected:
        LOG.info('waiting for motion...')
        anotate_time(1)

      LOG.info('motion detected. Start recording video...')
      motion_detected = False
      recording = True

      # replace the following code that saves the image to a file with:
      # 1. scp or somehow copy image to another computer,
      #    such as gdrive, ftp, or a shared folder
      # 2. use tcp to stream the image to a a web browser via a web server,
      #    such as nginx, python -m SimpleHTTPServer, gstreamer, or ???
      # just avoid saving the file to disk ... why?
      # a raspberry pi is limited to a microSD for storage, so the
      # repetition of adding/deleting images will wear it out

      filename = '/vid_' + \
        datetime.datetime.now().strftime('%Y-%m-%dT%H.%M.%S') + '.h264'
      LOG.info('capturing video: %s' % filename)

      videoIO = BytesIO()
      anotate_time(clip_time / 2)
      stream.copy_to(videoIO, seconds=clip_time)

      videoIO.seek(0)

      ssh = SSHClient()
      #key auth
      #ssh.load_system_host_keys()
      #ssh.connect(HOST)

      #pass auth
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh.connect(HOST, username=HOST_USER, password=PASSWORD)

      scp = SCPClient(ssh.get_transport())
      scp.putfo(videoIO, remote_path=REMOTE_IMG_PATH + filename)
      scp.close()
      LOG.info('video transfer to %s successful' % HOST)
      videoIO.close()
      recording = False
      motion_detected = False

  except KeyboardInterrupt as e:
    LOG.info("\nreceived KeyboardInterrupt via Ctrl-C")
    pass
  finally:
    camera.stop_recording();
    stream.clear()
    stream.close()
    camera.close()
    LOG.info("\ncamera turned off!")
    LOG.info("detect motion has ended.\n")
