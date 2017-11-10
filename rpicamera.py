import picamera
import picamera.array
import datetime
import time
import logging
import dropbox
import contextlib
import numpy as np
import json
import pprint
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from fractions import Fraction

#Setup logging
logging.basicConfig(filename='logfile.log',level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',)
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

logging.debug('Libraries loaded')

#Setup Dropbox session
dbx = dropbox.Dropbox('MZ2iiIImvUAAAAAAAAAAzo2V-UCXSK7MUojx9f7qDKo73tiFjRwJo0J2N2zwkYgz')
#Check if it works
try:
    dbx.users_get_current_account()
except AuthError as err:
    logging.error('ERROR: Invalid access token; try re-generating token')

#Constants
SECONDS2MICRO = 1000000  # Constant for converting Shutter Speed in Seconds to Microseconds

# Default Settings
confFileName = "conf.json"
usePIR = False
realtime = True
dropbox_token = 'MZ2iiIImvUAAAAAAAAAAzo2V-UCXSK7MUojx9f7qDKo73tiFjRwJo0J2N2zwkYgz'
SMSNotification = True
SMSControl = True
authorizedNumber = 733733733
useDropbox = True

imageDir = "images"
imagePath = "/home/pi/pimotion/" + imageDir
imageNamePrefix = 'capture-'  # Prefix for all image file names. Eg front-
imageWidth = 640
imageHeight = 360
imageVFlip = False   # Flip image Vertically
imageHFlip = False   # Flip image Horizontally
imagePreview = False
quality = 72

numberSequence = False

threshold = 10  # How Much pixel changes
sensitivity = 100  # How many pixels change

nightISO = 800
nightShutSpeed = 2 * SECONDS2MICRO  # seconds times conversion to microseconds constant

# Advanced Settings not normally changed
testWidth = 128
testHeight = 80

def loadConfig(confFile):
    conf = json.load(open(confFile))
    usePIR = conf['use_PIR']
    useDropbox = conf['use_dropbox']
    SMSNotification = conf['SMS_notification']
    SMSControl = conf['SMS_control']
    authorizedNumber = conf['authorized_number']


def checkImagePath(imagedir):
    # Find the path of this python script and set some global variables
    mypath=os.path.abspath(__file__)
    baseDir=mypath[0:mypath.rfind("/")+1]
    baseFileName=mypath[mypath.rfind("/")+1:mypath.rfind(".")]

    # Setup imagePath and create folder if it Does Not Exist.
    imagePath = baseDir + imagedir  # Where to save the images
    # if imagePath does not exist create the folder
    if not os.path.isdir(imagePath):
        logging.warning('%s - Image Storage folder not found' % (progName))
        logging.debug('%s - Creating image storage folder %s ' % (progName, imagePath))
        os.makedirs(imagePath)
    return imagePath

def takeDayImage(imageWidth, imageHeight, filename):
    logging.debug('takeDayImage - Working .....')
    with picamera.PiCamera() as camera:
        camera.resolution = (imageWidth, imageHeight)
        # camera.rotation = cameraRotate #Note use imageVFlip and imageHFlip variables
        if imagePreview:
            camera.start_preview()
        camera.vflip = imageVFlip
        camera.hflip = imageHFlip
        # Day Automatic Mode
        camera.exposure_mode = 'auto'
        camera.awb_mode = 'auto'
        camera.capture(filename, format='jpeg', quality=quality)
    logging.debug('takeDayImage - Captured %s' % (filename))
    return filename

def takeNightImage(imageWidth, imageHeight, filename):
    logging.debug('takeNightImage - Working .....')
    with picamera.PiCamera() as camera:
        camera.resolution = (imageWidth, imageHeight)
        if imagePreview:
            camera.start_preview()
        camera.vflip = imageVFlip
        camera.hflip = imageHFlip
        # Night time low light settings have long exposure times
        # Settings for Low Light Conditions
        # Set a frame rate of 1/6 fps, then set shutter
        # speed to 6s and ISO to approx 800 per nightISO variable
        camera.framerate = Fraction(1, 6)
        camera.shutter_speed = nightShutSpeed
        camera.exposure_mode = 'off'
        camera.iso = nightISO
        # Give the camera a good long time to measure AWB
        # (you may wish to use fixed AWB instead)
        time.sleep(10)
        camera.capture(filename, format='jpeg', quality=quality, thumbnail=None)
    logging.debug('checkNightMode - Captured %s' % (filename))
    return filename

def takeMotionImage(width, height, daymode):
    with picamera.PiCamera() as camera:
        time.sleep(1)
        camera.resolution = (width, height)
        with picamera.array.PiRGBArray(camera) as stream:
            if daymode:
                camera.exposure_mode = 'auto'
                camera.awb_mode = 'auto'
            else:
                # Take Low Light image
                # Set a framerate of 1/6 fps, then set shutter
                # speed to 6s and ISO to 800
                camera.framerate = Fraction(1, 6)
                camera.shutter_speed = nightShutSpeed
                camera.exposure_mode = 'off'
                camera.iso = nightISO
                # Give the camera a good long time to measure AWB
                # (you may wish to use fixed AWB instead)
                time.sleep( 10 )
            camera.capture(stream, format='rgb')
            return stream.array

def scanIfDay():
    with picamera.PiCamera() as camera:
        time.sleep(1)
        camera.resolution = (testWidth, testHeight)
        with picamera.array.PiRGBArray(camera) as stream:
            camera.exposure_mode = 'auto'
            camera.awb_mode = 'auto'
            camera.capture(stream, format='rgb')
            pixAverage = int(np.average(stream.array[...,1]))
    logging.info("Light Meter pixAverage=%i" % pixAverage)
    if (pixAverage > 100):
        return True
    else:
        return False

def scanMotion(width, height, daymode):
    motionFound = False
    data1 = takeMotionImage(width, height, daymode)
    while not motionFound:
        data2 = takeMotionImage(width, height, daymode)
        diffCount = 0L;
        for w in range(0, width):
            for h in range(0, height):
                # get the diff of the pixel. Conversion to int
                # is required to avoid unsigned short overflow.
                diff = abs(int(data1[h][w][1]) - int(data2[h][w][1]))
                if  diff > threshold:
                    diffCount += 1
            if diffCount > sensitivity:
                break; #break outer loop.
        if diffCount > sensitivity:
            motionFound = True
        else:
            data2 = data1
    return motionFound

def getFileName(imagePath, imageNamePrefix, currentCount):
    rightNow = datetime.datetime.now()
    if numberSequence :
        filename = imagePath + "/" + imageNamePrefix + str(currentCount) + ".jpg"
    else:
        filename = "%s/%s%04d%02d%02d-%02d%02d%02d.jpg" % ( imagePath, imageNamePrefix ,rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second)
    return filename

def motionDetection():
    logging.debug('Scanning for Motion threshold=%i sensitivity=%i ......'  % (threshold, sensitivity))
    isDay = False
    currentCount= 1000
    while True:
        if scanMotion(testWidth, testHeight, isDay):
            filename = getFileName(imagePath, imageNamePrefix, currentCount)
            if numberSequence:
                currentCount += 1
            if isDay:
                takeDayImage( imageWidth, imageHeight, filename )
                logging.debug('Take day image')
            else:
                takeNightImage( imageWidth, imageHeight, filename )
                logging.debug('Take night image')
# Save photo to cloud
            saveToCloud(filename)

def saveToCloud(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    with stopwatch('upload %d bytes' % len(data)):
        try:
            dbx.files_upload(data, filename, mute=False)
            logging.info('Uploading photo %s to Dropbox' % filename)
        except dropbox.exceptions.ApiError as err:
            logging.error('*** API error %s' % err)
    f.close()

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
                saveToCloud(filename)
            else:
                takeNightImage( imageWidth, imageHeight, filename )
                saveToCloud(filename)

class vectorMotionAnalysis(picamera.array.PiMotionAnalysis):
    def analyse(self, a):
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)
        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion
        if (a > 60).sum() > 10:
            print('Motion detected!')

def downloadFile(fileName):
    # Download JSON Configuration file from Dropbpox
    with stopwatch('download'):
        try:
            md, res = dbx.files_download('/'.format(fileName))
        except dropbox.exceptions.HttpError as err:
            logging.error('*** HTTP error %s' % err)
            return None
    data = res.content
    logging.debug(len(data), 'bytes; md:', md)
    myFile = open(fileName,'w')
    myFile.write(data)

@contextlib.contextmanager
def stopwatch(message):
    # Measure how long the block of code took to process
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        logging.info('Total elapsed time for %s: %.3f' % (message, t1 - t0))

if __name__ == '__main__':
    try:
        downloadFile(confFileName)
        loadConfig(confFileName)
        if usePIR:
            PIRMotionDetection()
        else:
            motionDetection()
    finally:
        logging.debug('Exiting program')
