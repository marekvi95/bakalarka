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
import RPi.GPIO as GPIO


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


class PIRMotionAnalysis():
    def __init__(self, pin, handler):

        self.pin = pin
        self.handler = handler

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)

    def is_detected(self):
        if GPIO.input(18):
            self.handler.motion_detected()
            logging.info('Motion detected from PIR')
            #return True

class LEDSwitch():
    def _init_(self, pin=BaseConfig.LEDpin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, 0)

    def switch(self):
        if GPIO.input(self.pin):
            GPIO.output(self.pin, 0)
        else:
            GPIO.output(self.pin, 1)

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
    def __init__(self, camera, led, post_capture_callback=None, q=None):
        self.camera = camera
        self.led = led
        self.callback = post_capture_callback
        self.q = q
        self.detected = False
        self.working = False
        self.i = 0
        self.echoCounter = -1

        self.led2 = LEDSwitch()

    def motion_detected(self):
        if not self.working:
            self.detected = True

    def tick(self):
        """
            This tick method provides a handler for capturing the pictures.
            It ticks every second after PiMotion.start() was called.
            If detected == True and method is not processing any capture
            (That is indicated by variable 'working'), it begins with processing.
            First datetime method is called to obtain the actual datetime, then
            the scene is analyzed with scan_dat method which return true if
            light conditions appear to be daylight or false if the light level
            is too low.

            If the echo mode is activated


            For daylight:
                exposure compensation is set to 0 <-25;25>
                exposure mode is set to auto
                camera shutter speed is set to 0 (auto mode)

            For bad light conditions:
                exposure compensation is set to 25 for maximum brightness
                exposure mode is set to night preview
                shutter speed is set to 200000 microseconds which is equal
                to 0,2s
        """
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
                self.camera.exposure_compensation = 0
                self.camera.exposure_mode = 'auto'
                self.camera.shutter_speed = 0
                #self.camera.iso = 200
                self.camera.capture(path + filename, format='jpeg', quality=50)
            else:
                logging.debug("Night mode capture activated")
                self.camera.exposure_compensation = 25
                self.camera.exposure_mode = 'nightpreview'
                self.camera.shutter_speed = 200000
                #self.camera.iso = 800
                # Turn LED on
                self.led2.switch()
                self.camera.capture(path + filename, format='jpeg', quality=50)
                # Turn LED off
                self.led2.switch()

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
            camera.rotation = BaseConfig.rotation
            camera.framerate = 5

            # LED Switch
            #led = LEDSwitch(BaseConfig.LEDpin)
            led = LEDSwitch()

            handler = CaptureHandler(camera, led, self.post_capture_callback, self.q)

            # PIR Motion analyser
            #pir = PIRMotionAnalysis(BaseConfig.PIRpin, handler)

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
                    #pir.is_detected()
                    time.sleep(1)
            finally:
                camera.stop_recording()
                logging.debug('Recording finished')

#q = queue.Queue(maxsize=200)
#w = FileUploader(storage='gdrive', q=q)
#w.start()
#motion = PiMotion(verbose=False, post_capture_callback=None)
#motion.start()
