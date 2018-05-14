import contextlib
import logging
import json

class BaseConfig:
    """ Basic configuration which cannot be changed online

        Variables:

        confFileName -- name of the default JSON configuration file

        imageDir -- default image directory
        imagePath -- path to the directory + imageDir
        imageNamePrefix -- Prefix for all image file names. Eg front-
        imageWidth -- width of taken pictures in pixels
        imageHeight -- height of taken pictures in pixels
        imageVFlip -- flips image vertically if true
        imageHFlip -- flips image Horizontally if true
        imagePreview -- opens window with picture if true
        imageQuality -- JPEG quality 0...100

        confCheckTime -- how long does it take between conf file checks in sec

    """
    # Default Settings
    confFileName = "conf.json"

    imageDir = "images"
    imagePath = "/home/pi/" + imageDir
    imageNamePrefix = 'capture-'  # Prefix for all image file names. Eg front-
    imageWidth = 640
    imageHeight = 368
    imageVFlip = False   # Flip image Vertically
    imageHFlip = False   # Flip image Horizontally
    rotation = 90 # Rotation of the image
    imagePreview = False
    imageQuality = 72

    vecMagnitude = 60  # Vector magnitude
    vecCount = 50  # How many vectors change
    cameraFPS = 10 # framerate

    nightISO = 800
    # nightShutSpeed = 2 * SECONDS2MICRO  # seconds times conversion to microseconds constant

    # Advanced Settings not normally changed
    testWidth = 128
    testHeight = 80

    confCheckTime = 10

    PIRpin = 18
    LEDpin = 23

    pictureFolderID = '1AO_tQMMz2c6_l69s9vo9PW0PTy4nrYqi'
    confFileID='1TBLQfJHsZYPXDvcpS_ysg6asxf-5_Oku'
    dashboardFileID = '1XNmtg0NoCiU03NDZohlBwmOpFC-heHWbdRzY_tTYjhg'
    logRange = 'Log!A:A'
    msgRange = 'Zpravy!A:A'
    OAuthJSON = 'client_secret.json'

    # File uploader sleep time in seconds
    fileUploadSleep = 5

    batchUploadWindow = 23

class UserConfig(BaseConfig):
    """ Extends BaseConfig class with user defined configuration

        Variables:

        mode -- mode of motion detection

    """
    mode = 'realtime'
    echo = False
    interval = 100
    storage = 'gdrive'
    usePIR = False
    dropboxToken = 'MZ2iiIImvUAAAAAAAAAAzo2V-UCXSK7MUojx9f7qDKo73tiFjRwJo0J2N2zwkYgz'
    SMSNotification = False
    SMSControl = False
    authorizedNumber = 733733733

    @classmethod
    def load_config(cls, conf):
        try:
            if conf['mode'] != 'realtime' or 'interval' or 'batch' or 'ondemand':
                logging.error('Mode is invalid!!')
            else:
                cls.mode = conf['mode']
            cls.interval = conf['interval']

            if conf['usePIR'] == 'on':
                cls.usePIR = True
            else:
                cls.usePIR = False

            cls.authorizedNumber = conf['authorizedNumber']

            if conf['SMSNotification'] == 'on':
                cls.SMSNotification = True
            else:
                cls.SMSNotification = False

            if conf['SMSControl'] == 'on':
                cls.SMSControl = True
            else:
                cls.SMSControl = False

            if conf['echo'] == 'on':
                cls.echo = True
            else:
                cls.echo = False

        except KeyError:
            logging.error('New configuration cannot be loaded, check syntax!')


@contextlib.contextmanager
def stopwatch(message):
    # Measure how long the block of code took to process
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        logging.info('Total elapsed time for %s: %.3f' % (message, t1 - t0))
