import logging
import threading
import time
from io import StringIO
import simplejson as json
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import config

logging.basicConfig(level=logging.DEBUG,
                     format='(%(threadName)-10s) %(message)s',
                     )


class ConfFileDownloader(threading.Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        super().__init__(group=group, target=target, name=name,
                         daemon=daemon)
        self.args = args
        self.kwargs = kwargs

        return

    def run(self):
        logging.debug('Initialization... Params:', self.kwargs)
        drive = self.auth() # Authorization
        content = self.download_file(drive)
        oldconf = self.parse_json(content)
        while True:
            content = self.download_file(drive)
            newconf = self.parse_json(content)

            if (newconf != oldconf):
                oldconf = newconf
                print("Configuration changed!!")
            time.sleep(5)

        return

    def auth(self):
        gauth = GoogleAuth()
        # Try to load saved client credentials
        gauth.LoadCredentialsFile("mycreds.txt")
        if gauth.credentials is None:
            # Authenticate if they're not there
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            # Refresh them if expired
            gauth.Refresh()
        else:
            # Initialize the saved creds
            gauth.Authorize()
        # Save the current credentials to a file
        gauth.SaveCredentialsFile("mycreds.txt")

        drive = GoogleDrive(gauth)

        return drive

    def download_file(self, drive):

        conffile = drive.CreateFile({'id': '1TBLQfJHsZYPXDvcpS_ysg6asxf-5_Oku'})
        conffile.FetchMetadata()

        print('title: %s, mimeType: %s' % (conffile['title'], conffile['mimeType']))

        return conffile.GetContentString()

    def parse_json(self, jsonfile):
        return json.loads(jsonfile)

    def load_config(self, configdata):
        pass

class FileUploader():
    def GDriveUpload():
        pass



w = ConfFileDownloader(args=0, kwargs={'a': 'A', 'b': 'B'})

w.start()
