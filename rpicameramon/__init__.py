import logging
import config
import filemanipulation
import motion
import telemetry
import queue


from config import BaseConfig
from config import UserConfig

from filemanipulation import FileUploader
from filemanipulation import ConfFileDownloader
from motion import PiMotion
from telemetry import GoogleHandler
from telemetry import LogSender
from telemetry import TelemetrySender

# initialization of the basic logging to the file
logging.basicConfig(filename='logfile.log',level=logging.DEBUG,
                   format='%(asctime)s %(threadName)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',)

# initialization of the queue for logging
q1 = queue.Queue(-1)

# initialization of Google API handlers
gh = GoogleHandler()
gh1 = GoogleHandler()

# get credentials for Google services
crd = gh.get_credentials()
crd1 = gh1.get_credentials()

# get Google Sheet service
srvc = gh.get_sheets_service(credentials=crd)
srvc1 = gh1.get_sheets_service(credentials=crd1)

# Setup logging handlers
handler = logging.StreamHandler()
handler2 = logging.handlers.QueueHandler(q1)
handler2.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(threadName)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
handler2.setFormatter(formatter)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(handler2)
logging.getLogger('').addHandler(handler)
logging.getLogger('googleapiclient').setLevel(logging.CRITICAL)

if __name__ == '__main__':
    try:
        logging.debug('Starting program')

        # init of threads - Logsender and TelemetrySender
        try:
            logThread = LogSender(q1, gh)
            telemetryThread = TelemetrySender(gh1)
            logThread.start()
            telemetryThread.start()
            logging.debug('Log and telemtry sender started')
        except KeyboardInterrupt:
            logThread.cancel()
            telemetryThread.cancel()

        #Initialization of configuration checker threadName
        try:
            cfg = ConfFileDownloader(filename=BaseConfig.confFileID)
            cfg.start()
            logging.debug('Conf file downloader started')
        except KeyboardInterrupt:
            cfg.cancel()

        #initialization of queue for file uploader
        q = queue.Queue(maxsize=200)

        #initialization of file uploader
        try:
            w = FileUploader(storage=UserConfig.storage, q=q)
            w.start()
            logging.debug('File uploader started')
        except KeyboardInterrupt
            w.cancel()


        #initialization daylight detection threadName

        #initialization of motion detection analysis

        motion = PiMotion(verbose=False, post_capture_callback=None, q=q)
        motion.start()

    except KeyboardInterrupt:
        logging.debug('Keyboard interrupt received, exiting...')

    finally:
        #w.cancel()
        #cfg.cancel()
        #GPIO.cleanup()
        logging.debug('Exiting program')
