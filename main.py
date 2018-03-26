import logging
import config
import filemanipulation
import motion
import telemetry

from config import BaseConfig
from config import UserConfig

from filemanipulation import FileUploader
from filemanipulation import ConfFileDownloader
from motion import PiMotion


if __name__ == '__main__':
    try:
        logging.debug('Starting program')
        #Initialization of configuration checker threadName
        cfg = ConfFileDownloader(filename=BaseConfig.confFileID)
        cfg.start()

        #initialization of queue for file uploader
        q = queue.Queue(maxsize=200)

        #initialization of file uploader
        w = FileUploader(storage=UserConfig.storage, q=q)
        w.start()

        #initialization daylight detection threadName

        #initialization of motion detection analysis
        motion = PiMotion(verbose=False, post_capture_callback=None)
        motion.start()

    finally:
        w.cancel()
        cfg.cancel()
        logging.debug('Exiting program')
