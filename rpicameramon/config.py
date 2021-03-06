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

            pictureFolderID (str): Google Drive ID of folder with pictures
            confFileID (str): Google Drive ID of JSON configuration files
            dashboardFileID (str): Google Drive ID of dashboard panel

            logRange (str): Range in sheets for telemetry messages
            msgRange (str): Range in sheets for log messages
            OAuthJSON (str): Name of the JSON file for Google OAuth authentication

            fileUploadSleep (int): Sleep time in seconds for file uploader thread
            batchUploadWindow (int): Allowed hour for file uploads in batch mode

            GSMport (str): Device address of a GSM Module
            GSMbaud (int): Baud rate for communication with the GSM module
            GSMPIN (int): PIN for unlocking the SIM card
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
    dropboxToken = ''

    # File uploader sleep time in seconds
    fileUploadSleep = 5
    batchUploadWindow = 23

    GSMport = '/dev/ttyGSM1'
    GSMbaud = 115200
    GSMPIN = None # SIM card PIN (if any)

class UserConfig(BaseConfig):
    """ Extends BaseConfig class with the user defined configuration.
        This configuration can be updated from the external JSON.

        Attributes:

            mode (str): default runtime mode (realtime, interval, batch, ondemand)
            echo (boolean): echo mode
            interval (int): default interval time in seconds for interval mode
            storage (str): gdrive or dropbox. Dropbox is only experimental
            usePIR (boolean): use PIR sensor
            SMSNotification (boolean): SMS SMSNotification
            SMSControl (boolean): Allow control via SMS messages
            authorizedNumber (int): Authorized number for control and notifications
    """
    mode = 'realtime'
    echo = False
    interval = 20
    storage = 'gdrive'
    usePIR = False
    SMSNotification = True
    SMSControl = True
    authorizedNumber = "+420733149295"

    @classmethod
    def load_config(cls, conf):
        """ This method loads configuration to UserConfig class from the JSON file.

        Raises:
            KeyError: If JSON cannot be parsed

        """
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
