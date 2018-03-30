import contextlib
import logging
import json

#Setup logging
#logging.basicConfig(filename='logfile.log',level=logging.DEBUG,
#                    format='%(asctime)s %(threadName)-12s %(levelname)-8s %(message)s',
#                    datefmt='%m-%d %H:%M',)
# define a Handler which writes INFO messages or higher to the sys.stderr
#console = logging.StreamHandler()
#console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
#formatter = logging.Formatter('%(threadName)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
#console.setFormatter(formatter)
# add the handler to the root logger
#logging.getLogger('googleapiclient.discovery').setLevel(logging.CRITICAL)
#logging.getLogger('').addHandler(console)

#logging.debug('Libraries loaded')

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
    imageHeight = 360
    imageVFlip = False   # Flip image Vertically
    imageHFlip = False   # Flip image Horizontally
    imagePreview = False
    imageQuality = 72

    vecMagnitude = 60  # Vector magnitude
    vecCount = 50  # How many pixels change
    cameraFPS = 10 # framerate

    nightISO = 800
    # nightShutSpeed = 2 * SECONDS2MICRO  # seconds times conversion to microseconds constant

    # Advanced Settings not normally changed
    testWidth = 128
    testHeight = 80

    confCheckTime = 10

    PIRpin = 21

    pictureFolderID = '1AO_tQMMz2c6_l69s9vo9PW0PTy4nrYqi'
    confFileID='1TBLQfJHsZYPXDvcpS_ysg6asxf-5_Oku'
    dashboardFileID = '1XNmtg0NoCiU03NDZohlBwmOpFC-heHWbdRzY_tTYjhg'
    logRange = 'Log!A:A'
    msgRange = 'Zpravy!A:A'
    OAuthJSON = 'client_secret.json'

class UserConfig(BaseConfig):
    """ Extends BaseConfig class with user defined configuration

        Variables:

        mode -- mode of motion detection

    """
    mode = 'interval'
    echo = False
    interval = 1
    storage = 'gdrive'
    usePIR = False
    dropboxToken = 'MZ2iiIImvUAAAAAAAAAAzo2V-UCXSK7MUojx9f7qDKo73tiFjRwJo0J2N2zwkYgz'
    SMSNotification = False
    SMSControl = False
    authorizedNumber = 733733733

    @classmethod
    def load_config(cls, conf):
        try:
            if cls.mode == 'realtime' or 'interval' or 'batch' or 'ondemand':
                logging.error('Mode is invalid!!')
            else:
                cls.mode = conf['mode']

            cls.interval = conf['interval']
            cls.storage = conf['storage']
            cls.usePIR = conf['usePIR']
            cls.dropboxToken = conf['dropboxToken']
            cls.authorizedNumber = conf['authorizedNumber']
            cls.SMSNotification = conf['SMSNotification']
            cls.SMSControl = conf['SMSControl']
            cls.echo = conf['echo']

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
