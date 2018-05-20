import queue
import numpy as np
import logging
import time
import datetime
import os
import threading
from io import BytesIO

import picamera
import picamera.array
from gsmmodem.modem import GsmModem
from PIL import Image

import config
import filemanipulation
from config import BaseConfig
from config import UserConfig
from filemanipulation import FileUploader
import RPi.GPIO as GPIO

class MotionAnalysis(picamera.array.PiMotionAnalysis):
    """
        MotionAnalysis class extends PiMotionAnalysis class.

        The array passed to analyse() is organized as (rows, columns)
        where rows and columns are the number of rows and columns of macro-
        blocks (16x16 pixel blocks) in the original frames. There is always
        one extra column of macro-blocks present in motion vector data.

    """
    def __init__(self, camera, handler):
        super(MotionAnalysis, self).__init__(camera)
        self.handler = handler

    def analyse(self, a):

        if UserConfig.mode == 'realtime' or UserConfig.mode == 'batch':
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

        elif UserConfig.mode == 'interval':
            # Interval mode
            # capture
            logging.info('Capturing interval photo')
            self.handler.motion_detected()
            # sleep for some time
            time.sleep(UserConfig.interval)

        else:
            pass


class PIRMotionAnalysis():
    """
        This class provides a handler for PIR sensor
        It detects if the input pin is in the high state
        and calls motion_detected handler

        Args:
            pin (number): BCM number of GPIO pin where is PIR sensor connected
            handler (obj): CaptureHandler object
    """
    def __init__(self, pin, handler):

        self.pin = pin
        self.handler = handler

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)

    def is_detected(self):
        if GPIO.input(self.pin):
            self.handler.motion_detected()
            logging.info('Motion detected from PIR')

class CaptureHandler:
    """
        It provides a handler for capturing the pictures. With the LED Switch
        functionality.

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

        # Configure LED
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BaseConfig.LEDpin, GPIO.OUT)
        GPIO.output(BaseConfig.LEDpin, 0)

    def motion_detected(self):
        if not self.working:
            self.detected = True

    def tick(self):
        """
            This tick method provides a handler for capturing the pictures.
            It ticks every second after PiMotion.start() was called.
            If detected is True and method is not processing any capture
            (That is indicated by variable 'working'), it begins with processing.
            First, datetime method is called to obtain the actual datetime, then
            the scene is analyzed with scan_day method which returns true if
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
                Turn on the LED
        """
        if self.detected:
            logging.debug('Capturing!')
            self.working = True
            self.detected = False
            self.i += 1

            stream = BytesIO()

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
                #self.camera.capture(path + filename, format='jpeg', quality=50)
                self.camera.capture(stream, format='jpeg')
            else:
                logging.debug("Night mode capture activated")
                self.camera.exposure_compensation = 25
                self.camera.exposure_mode = 'nightpreview'
                self.camera.shutter_speed = 200000
                #self.camera.iso = 800
                # Turn LED on
                GPIO.output(BaseConfig.LEDpin, 1)
                #self.camera.capture(path + filename, format='jpeg', quality=50)
                self.camera.capture(stream, format='jpeg')
                # Turn LED off
                GPIO.output(BaseConfig.LEDpin, 0)

            stream.seek(0)
            picture = Image.open(stream)
            picture.save(path + filename, optimize=True, quality=75)
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
        """ This method captures picture as an RGB array and calculates
        average value of the pixels in the matrix.
        If the value pixAverage is more than 50 (scene is gray to black).
        It indicates that the light condition is poor and we can set up night
        params.
        """
        with picamera.array.PiRGBArray(self.camera) as stream:
            self.camera.capture(stream, format='rgb')
            pixAverage = int(np.average(stream.array[...,1]))

        logging.info("Light Meter pixAverage=%i" % pixAverage)
        if (pixAverage > 50):
            return True
        else:
            return False

class SMSHandler:
    def __init__(self, handler):
        """ This class handles receiving of SMS messages. After receiving
        the SMS, it's checked if SMSControl and SMSNotifications are allowed and also
        if the phone number is allowed.
        """
        self.handler = handler

        modem = GsmModem(BaseConfig.GSMport, BaseConfig.GSMbaud,
                         smsReceivedCallbackFunc=self.handle_sms, AT_CNMI="2,1,0,1")

        modem.smsTextMode = False
        modem.connect(BaseConfig.GSMPIN)

    def __del__(self):
        modem.close()

    def handle_sms(self, sms):
        logging.debug(u'== SMS message received ==\nFrom: {0}\nTime: {1}\nMessage:\n{2}\n'.format(sms.number, sms.time, sms.text))
        if sms.number == UserConfig.authorizedNumber:
            if UserConfig.SMSControl:
                if sms.text.lower() == 'set mode realtime':
                    # set mode
                    UserConfig.mode = 'realtime'
                    logging.debug('Mode has been set to realtime by SMS')
                    sms.reply(u'Mode has been set to realtime')

                elif sms.text.lower() == 'set mode batch':
                    # set mode
                    UserConfig.mode = 'batch'
                    logging.debug('Mode has been set to batch by SMS')
                    sms.reply(u'Mode has been set to batch')

                elif sms.text.lower() == 'set mode interval':
                    # set mode
                    UserConfig.mode = 'interval'
                    logging.debug('Mode has been set to interval by SMS')
                    sms.reply(u'Mode has been set to interval')

                elif sms.text.lower() == 'set mode ondemand':
                    # set mode
                    UserConfig.mode = 'ondemand'
                    logging.debug('Mode has been set to ondemand by SMS')
                    sms.reply(u'Mode has been set to ondemand')

                elif sms.text.lower() == 'q mode':
                    # query mode
                    logging.debug('Mode has been queried by SMS')
                    sms.reply(u'Mode is {}'.format(UserConfig.mode))

                elif sms.text.lower() == 'battery':
                    # query mode
                    logging.debug('Status of charging has been queried')
                    sms.reply(u'Charging 12V.3')

                elif sms.text.lower() == 'takephoto':
                    # query mode
                    self.handler.motion_detected()
                    logging.debug('Photo has been requested')
                    sms.reply(u'Photo taken')

            else:
                logging.debug('SMS Control not allowed')
        else:
            logging.debug('Number is not authorized')


class PiMotion:
    """ This class handles the camera and PIR sensor setup.
    It sets up resolution and framerate and starts
    capturing the video outputting it to the MotionAnalysis object.

    Args:
        post_capture_callback (callback): not in use
        q (Queue obj): queue for captured photos

    Raises:
        KeyboardInterrupt: Interrupt the program

    """
    def __init__(self, post_capture_callback=None, q=None):
        self.post_capture_callback = post_capture_callback
        self.q = q

    def start(self):
        with picamera.PiCamera() as camera:
            camera.resolution = (BaseConfig.imageWidth, BaseConfig.imageHeight)
            camera.framerate = BaseConfig.cameraFPS
            camera.rotation = BaseConfig.rotation

            handler = CaptureHandler(camera, self.post_capture_callback, self.q)

            # PIR Motion analyser
            pir = PIRMotionAnalysis(BaseConfig.PIRpin, handler)

            # SMS handler
            smshandle = SMSHandler(handler)

            logging.debug('Starting camera')
            #time.sleep(2)

            try:
                logging.debug('Capture of video started')
                camera.start_recording(
                    '/dev/null', format='h264',
                    motion_output=MotionAnalysis(camera, handler)
                )

                while True:
                    # Tick for the camera motion detection
                    handler.tick()
                    # Tick for PIR motion detecion
                    if UserConfig.usePIR:
                        pir.is_detected()
                    time.sleep(1)

            except KeyboardInterrupt:
                logging.debug('Keyboard interrupt Exiting main loop')

            finally:
                camera.stop_recording()
                logging.debug('Recording finished')
                del smshandle
                GPIO.cleanup()
