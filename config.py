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

    PIRpin = 21

class UserConfig(BaseConfig):
    """ Extends BaseConfig class with user defined configuration

        Variables:

        mode -- mode of motion detection

    """
    def __init__(self, cfgdict):
        self.__dict__ = cfgdict

    mode = "realtime"
    echo = False
    interval = 1
    storage = "dropbox"
    google_json = ""
    usePIR = False
    dropbox_token = 'MZ2iiIImvUAAAAAAAAAAzo2V-UCXSK7MUojx9f7qDKo73tiFjRwJo0J2N2zwkYgz'
    SMSNotification = False
    SMSControl = False
    authorizedNumber = 733733733
    useDropbox = True
