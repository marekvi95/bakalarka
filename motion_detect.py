import queue
import numpy as np

import picamera
import picamera.array

import config


class MotionAnalysis(picamera.array.PiMotionAnalysis):
    def __init__(self, camera, handler):
        super(MyMotionDetector, self).__init__(camera)
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


class PIRMotionAnalysis():
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


class CaptureHandler():
    def __init__(self, camera, post_capture_callback=None):
        self.camera = camera
        self.callback = post_capture_callback
        self.detected = False
        self.working = False
        self.i = 0

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
            os.makedirs(path)

            if BaseConfig.imagePreview:
                self.camera.start_preview()

            self.camera.capture(path + filename)
            logging.debug('Captured ' + filename)

            self.camera.stop_preview()
            #put the taken picture into queue
            q.put(filename)

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
motion = PiMotion(verbose=False, post_capture_callback=None)
motion.start()
