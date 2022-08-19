#!/usr/bin/python
import os
import signal
import paramiko
from paramiko import SSHClient
from scp import SCPClient
import numpy as np
import picamera
import picamera.array
import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
LOG = logging.getLogger("capture_motion")

def signal_term_handler(signal, frame):
  LOG.info('shutting down ...')
  sys.exit(0)
signal.signal(signal.SIGTERM, signal_term_handler)


HOST = '192.168.7.48'
HOST_USER = 'iki'
LOCAL_IMG_PATH = '/home/pi-cam/captured'
REMOTE_IMG_PATH = '/home/iki/captured'
PORT = 44444
HOST_PORT = (HOST,PORT)
BUFSIZE = 4096

minimum_still_interval = 5
motion_detected = False
last_still_capture_time = datetime.datetime.now()

# The 'analyse' method gets called on every frame processed while picamera
# is recording h264 video.
# It gets an array (see: "a") of motion vectors from the GPU.
class DetectMotion(picamera.array.PiMotionAnalysis):
  def analyse(self, a):
    global minimum_still_interval, motion_detected, last_still_capture_time
    if datetime.datetime.now() > last_still_capture_time + \
        datetime.timedelta(seconds=minimum_still_interval):
      a = np.sqrt(
        np.square(a['x'].astype(np.float)) +
        np.square(a['y'].astype(np.float))
      ).clip(0, 255).astype(np.uint8)
      # experiment with the following "if" as it may be too sensitive ???
      # if there're more than 10 vectors with a magnitude greater
      # than 60, then motion was detected:
      if (a > 60).sum() > 10:
        LOG.info('motion detected at: %s' % datetime.datetime.now().strftime('%Y-%m-%dT%H.%M.%S.%f'))
        motion_detected = True

camera = picamera.PiCamera()
with DetectMotion(camera) as output:
  try:
    camera.resolution = (640, 480)
    camera.framerate= 10
    # record video to nowhere, as we are just trying to capture images:
    camera.start_recording('/dev/null', format='h264', motion_output=output)
    while True:
      while not motion_detected:
        LOG.info('waiting for motion...')
        camera.wait_recording(1)

      LOG.info('stop recording and capture an image...')
      camera.stop_recording()
      motion_detected = False

      # replace the following code that saves the image to a file with:
      # 1. scp or somehow copy image to another computer,
      #    such as gdrive, ftp, or a shared folder
      # 2. use tcp to stream the image to a a web browser via a web server,
      #    such as nginx, python -m SimpleHTTPServer, gstreamer, or ???
      # just avoid saving the file to disk ... why?
      # a raspberry pi is limited to a microSD for storage, so the
      # repetition of adding/deleting images will wear it out

      filename = LOCAL_IMG_PATH+'/img_' + \
        datetime.datetime.now().strftime('%Y-%m-%dT%H.%M.%S.%f') + '.jpg'
      camera.capture(filename, format='jpeg', use_video_port=True)
      LOG.info('image captured to file: %s' % filename)

      ssh = SSHClient()
      #key auth
      ssh.load_system_host_keys()
      ssh.connect(HOST)

      #pass auth
      #ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      #ssh.connect(HOST, username=HOST_USER, password=PASSWORD')

      scp = SCPClient(ssh.get_transport())
      scp.put(filename, remote_path=REMOTE_IMG_PATH)
      scp.close()
      LOG.info('copied image to %s' % HOST)

      os.remove(filename)
      LOG.info('deleted image')

      # record video to nowhere, as we are just trying to capture images:
      camera.start_recording('/dev/null', format='h264', motion_output=output)
  except KeyboardInterrupt as e:
    LOG.info("\nreceived KeyboardInterrupt via Ctrl-C")
    pass
  finally:
    camera.close()
    LOG.info("\ncamera turned off!")
    LOG.info("detect motion has ended.\n")

