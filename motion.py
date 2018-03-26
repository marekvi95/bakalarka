import queue
import numpy as np
import logging
import time
import datetime
import os

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
    def __init__(self, camera, handler):
        super(MotionAnalysis, self).__init__(camera)
        self.handler = handler

    def analyse(self, a):
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)
        # If there're more than 50 vectors with a magnitude greater
        # than 60, then say we've detected motion
        if (a > BaseConfig.vecMagnitude).sum() > BaseConfig.vecCount:
            # Motion detected!
            logging.debug('Motion detected!')
            self.handler.motion_detected()


class PIRMotionAnalysis:
    def initPIRsensor(PIR_PIN):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIR_PIN, GPIO.IN)

    def PIRscanMotion(PIR_PIN):
        motionFound = False;
        GPIO.add_event_detect(PIR_PIN, GPIO.RISING)
        if GPIO.event_detected(PIR_PIN):
            motionFound = True
            return motionFound

    def PIRMotionDetection():
        initPIRsensor(PIR_PIN)
        logging.info('Scanning for Motion using PIR ......')
        currentCount= 1000
        while True:
            if PIRscanMotion(PIR_PIN):
                filename = getFileName(imagePath, imageNamePrefix, currentCount)
                if numberSequence:
                    currentCount += 1
                if isDay:
                    takeDayImage( imageWidth, imageHeight, filename )
                else:
                    takeNightImage( imageWidth, imageHeight, filename )
                saveToDropbox(filename)


class CaptureHandler:
    def __init__(self, camera, post_capture_callback=None):
        self.camera = camera
        self.callback = post_capture_callback
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

            self.camera.capture(path + filename)
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
                    logging.debug(self.echoCounter, '. echo captured')
                    self.detected = True
            #put the taken picture into queue
            q.put(path + filename)

            logging.debug('Finished capturing')

            self.working = False


class PiMotion:
    def __init__(self, verbose=False, post_capture_callback=None):
        self.verbose = verbose
        self.post_capture_callback = post_capture_callback

    def start(self):
        with picamera.PiCamera() as camera:
            camera.resolution = (BaseConfig.imageWidth, BaseConfig.imageHeight)
            camera.framerate = BaseConfig.cameraFPS

            handler = CaptureHandler(camera, self.post_capture_callback)

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

q = queue.Queue(maxsize=200)
w = FileUploader(storage='gdrive', q=q)
w.start()
motion = PiMotion(verbose=False, post_capture_callback=None)
motion.start()
