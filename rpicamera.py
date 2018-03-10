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
import threading
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from fractions import Fraction

import httplib2
from apiclient import discovery
from apiclient.http import MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from datetime import datetime
from timeit import Timer


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
    myFile = open(confFile)
    conf = json.load(myFile)
    logging.info('Loading configuration file')
    usePIR = conf['use_PIR']
    storage = conf['storage']
    SMSNotification = conf['SMS_notification']
    SMSControl = conf['SMS_control']
    authorizedNumber = conf['authorized_number']
    myFile.close()

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
    isDay = True
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
            saveToCloud(filename, storage)

def intervalCapture():
    if isDay:
        takeDayImage( imageWidth, imageHeight, filename )
        logging.debug('Take day image')
    else:
        takeNightImage( imageWidth, imageHeight, filename )
        logging.debug('Take night image')

    saveToCloud(filename, storage)

def saveToDropbox(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    with stopwatch('upload %d bytes' % len(data)):
        try:
            dbx.files_upload(data, filename, mute=False)
            logging.info('Uploading photo %s to Dropbox' % filename)
        except dropbox.exceptions.ApiError as err:
            logging.error('*** API error %s' % err)
    f.close()

def saveToCloud(filename, storage): # save to cloud storage
    with open(filename, 'rb') as f:
        data = f.read()
    if ( storage=="dropbox" ):
        with stopwatch('upload %d bytes' % len(data)):
            try:
                dbx.files_upload(data, filename, mute=False)
                logging.info('Uploading photo %s to Dropbox' % filename)
            except dropbox.exceptions.ApiError as err:
                logging.error('*** API error %s' % err)

    if ( storage == "google"):
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('drive', 'v3', http=http)

        file_metadata = {'name': filename}
        media = MediaFileUpload(data,
                            mimetype='image/jpeg')
        file = service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
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
            else:
                takeNightImage( imageWidth, imageHeight, filename )
            saveToDropbox(filename)

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
            md, res = dbx.files_download('/{0}'.format(fileName))
        except dropbox.exceptions.HttpError as err:
            logging.error('*** HTTP error %s' % err)
            return None
    data = res.content
    #logging.debug(len(data), 'bytes; md:', md)
    myFile = open(fileName,'w')
    myFile.write(data)
    myFile.close()

def checkConf():
    threading.Timer(60.0, checkConf).start() # called every minute
    downloadFile(confFileName)
    loadConfig(confFileName)

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def uploadTelemetry():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1XNmtg0NoCiU03NDZohlBwmOpFC-heHWbdRzY_tTYjhg'
    rangeName = 'Log!A2:E2'
    values = [
        [
        str(datetime.now()),"OK",random.randint(10,15),random.randint(0,40)
        ]
    ]
    body = {
    'values': values
    }
    result = service.spreadsheets().values().append(
    spreadsheetId=spreadsheetId, range=rangeName,
    valueInputOption="USER_ENTERED", body=body).execute()
    print('{0} cells updated.'.format(result.get('updates')));

def saveToGDrive():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    file_metadata = {'name': 'rpizero.jpg'}
    media = MediaFileUpload('rpizero.jpg',
                        mimetype='image/jpeg')
    file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
def confFileThread():
    downloadFile(confFileName) # Download configuration file
    loadConfig(confFileName) # Load configuration
    checkConf() # Check configuration

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
        confFileThread()
        d = Timer(500.0, confFileThread())
        d.start()

        if ( mode == "interval"):
            t = Timer(interval*60.0, intervalCapture()) # Execute thread for interval capture
            t.start()

        motionDetection()
    finally:
        # t.cancel()
        # d.cancel()
        logging.debug('Exiting program')
