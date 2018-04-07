import queue
import numpy as np
import logging
import time
import datetime
import os
import threading

import picamera
import picamera.array

import config
import filemanipulation
from config import BaseConfig
from config import UserConfig
from filemanipulation import FileUploader

#Setup logging
#logging.basicConfig(filename='logfile.log',level=logging.DEBUG,
#                    format='%(asctime)s %(threadName)-12s %(levelname)-8s %(message)s',
#                    datefmt='%m-%d %H:%M',)
# define a Handler which writes INFO messages or higher to the sys.stderr
#console = logging.StreamHandler()
#console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
#formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
#console.setFormatter(formatter)
# add the handler to the root logger
#logging.getLogger('').addHandler(console)

#logging.debug('Libraries loaded')

class MotionAnalysis(picamera.array.PiMotionAnalysis):
    """ MotionAnalysis class extends PiMotionAnalysis class.

        The array passed to analyse() is organized as (rows, columns)
        where rows and columns are the number of rows and columns of macro-
        blocks (16x16 pixel blocks) in the original frames. There is always
        one extra column of macro-blocks present in motion vector data.

    """
    def __init__(self, camera, handler):
        super(MotionAnalysis, self).__init__(camera)
        self.handler = handler

    def analyse(self, a):

        if UserConfig.mode == 'realtime' or 'ondemand' or 'batch':
            a = np.sqrt(
                np.square(a['x'].astype(np.float)) +
                np.square(a['y'].astype(np.float))
                ).clip(0, 255).astype(np.uint8)
                # If there're more than 50 vectors with a magnitude greater
                # than 60, then say we've detected motion

            if (a > BaseConfig.vecMagnitude).sum() > BaseConfig.vecCount:
                # Motion detected!
                logging.info('Motion detected!')
                self.handler.motion_detected()

        if UserConfig.mode == 'interval':
            # Interval mode
            # capture
            self.handler.motion_detected()
            # sleep for some time
            time.sleep(UserConfig.interval)


class PIRMotionAnalysis(threading.Thread):
    def __init__(pin, handler):

        self.pin = pin
        self.handler = handler

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN)

        super().__init__(group=None, target=None, name="PIRMotionAnalysis",
                     daemon=None)

    def run(self):
        time.sleep(2) # to stabilize sensor
        while True:
            if GPIO.input(self.pin):
                logging.debug("PIR Motion detected")
                self.handler.motion_detected()
                time.sleep(5) #to avoid multiple detection
            time.sleep(0.1)



class CaptureHandler:
    """
        It provides a handler for capturing the pictures

        Attributes:
            camera (obj): PiCamera object
            callback (str): callback
            q (obj): queue for passing captured photos
            detected (bool): True if motion is detected
            working (bool): True if the picture is saving
            i (int): counter of captured photos
            echoCounter (int): counter of taken pictures with echo mode

    """
    def __init__(self, camera, post_capture_callback=None, q=None):
        self.camera = camera
        self.callback = post_capture_callback
        self.q = q
        self.detected = False
        self.working = False
        self.i = 0
        self.echoCounter = -1

    def motion_detected(self):
        if not self.working:
            self.detected = True

    def tick(self):
        if self.detected:
            logging.debug('Capturing!')
            self.working = True
            self.detected = False
            self.i += 1

            filename = '%s.jpg' % datetime.datetime.now().isoformat()
            path = BaseConfig.imagePath + "/" + BaseConfig.imageDir + "/"
            if not os.path.exists(path):
                os.makedirs(path)
                logging.debug('Path was created')

            if BaseConfig.imagePreview:
                self.camera.start_preview()

            if self.scan_day():
                logging.debug("Day mode capture acitvated")
                #self.camera.exposure_compensation = 0
                #self.camera.exposure_mode = 'auto'
                #self.camera.shutter_speed = 10
                #self.camera.iso = 200
                self.camera.capture(path + filename)
            else:
                logging.debug("Night mode capture activated")
                self.camera.exposure_compensation = 25
                self.camera.exposure_mode = 'nightpreview'
                self.camera.shutter_speed = 200000
                #self.camera.iso = 800
                self.camera.capture(path + filename)

                #self.camera.exposure_mode = 'auto'
                #self.camera.shutter_speed = 0


            logging.debug('Captured ' + filename)

            self.camera.stop_preview()

            if self.echoCounter == -1 and UserConfig.echo:
                logging.debug('Echo mode enabled, capturing will continue')
                self.echoCounter = 0
                self.detected = True

            if self.echoCounter >= 0:
                if self.echoCounter >= 10:
                    self.echoCounter = -1
                else:
                    self.echoCounter += 1
                    logging.debug('Echo image captured')
                    self.detected = True
            #put the taken picture into queue
            self.q.put(path + filename)

            logging.debug('Finished capturing')

            self.working = False

    def scan_day(self):
        with picamera.array.PiRGBArray(self.camera) as stream:
            #camera.exposure_mode = 'auto'
            #camera.awb_mode = 'auto'
            self.camera.capture(stream, format='rgb')
            pixAverage = int(np.average(stream.array[...,1]))

        logging.info("Light Meter pixAverage=%i" % pixAverage)
        if (pixAverage > 50):
            return True
        else:
            return False

    def turn_led():
        pass


class PiMotion:
    def __init__(self, verbose=False, post_capture_callback=None, q=None):
        self.verbose = verbose
        self.post_capture_callback = post_capture_callback
        self.q = q

    def start(self):
        with picamera.PiCamera() as camera:
            camera.resolution = (BaseConfig.imageWidth, BaseConfig.imageHeight)
            # camera.framerate = BaseConfig.cameraFPS
            camera.framerate = 5

            handler = CaptureHandler(camera, self.post_capture_callback, self.q)

            logging.debug('Starting camera')
            time.sleep(2)

            try:
                logging.debug('Capture of video started')
                camera.start_recording(
                    '/dev/null', format='h264',
                    motion_output=MotionAnalysis(camera, handler)
                )

                while True:
                    handler.tick()
                    time.sleep(1)
            finally:
                camera.stop_recording()
                logging.debug('Recording finished')

#q = queue.Queue(maxsize=200)
#w = FileUploader(storage='gdrive', q=q)
#w.start()
#motion = PiMotion(verbose=False, post_capture_callback=None)
#motion.start()
