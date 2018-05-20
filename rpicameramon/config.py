import contextlib
import logging
import json

class BaseConfig:
    """ Basic configuration which cannot be changed online

        Attributes:
            imageDir (str):default image directory
            imagePath (str): path to the directory + imageDir
            imageWidth (int): width of taken pictures in pixels
            imageHeight (int): height of taken pictures in pixels
            imageVFlip (bool): flips image vertically if true
            imageHFlip (bool): flips image Horizontally if true
            imagePreview (bool): opens window with picture if true
            imageQuality (int): JPEG quality 0...100

            vecMagnitude (int): minimum magnitude of a motion vector
            vecCount (int): minimal number of motion vectors
            cameraFPS (int): framerate of the camera

            confCheckTime (int): how long does it take between conf file checks in sec

            PIRpin (int): GPIO pin (BCM) where is PIR sensor connected
            LEDpin (int): GPIO pin (BCM) where is LED connected
            
    """
    # Default Settings

    imageDir = "images"
    imagePath = "/home/pi/" + imageDir
    imageWidth = 640
    imageHeight = 368
    imageVFlip = False   # Flip image Vertically
    imageHFlip = False   # Flip image Horizontally
    rotation = 90 # Rotation of the image
    imagePreview = False
    imageQuality = 72

    vecMagnitude = 40  # Vector magnitude
    vecCount = 40  # How many vectors change
    cameraFPS = 10 # framerate

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

    GSMport = '/dev/ttyGSM1'
    GSMbaud = 115200
    GSMPIN = None # SIM card PIN (if any)

class UserConfig(BaseConfig):
    """ Extends BaseConfig class with user defined configuration

        Variables:

        mode -- mode of motion detection

    """
    mode = 'interval'
    echo = False
    interval = 20
    storage = 'gdrive'
    usePIR = False
    dropboxToken = 'MZ2iiIImvUAAAAAAAAAAzo2V-UCXSK7MUojx9f7qDKo73tiFjRwJo0J2N2zwkYgz'
    SMSNotification = True
    SMSControl = True
    authorizedNumber = "+420733149295"

    @classmethod
    def load_config(cls, conf):
        try:
            if conf['mode'] in ['realtime','batch','ondemand','interval']:
                cls.mode = conf['mode']
            else:
                logging.error('Mode is invalid!!')
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
