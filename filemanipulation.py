import logging
import threading
import time
from io import StringIO
import json
import queue

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import dropbox

import config


class ConfFileDownloader(threading.Thread):

    def __init__(self, group=None, target=None, name=None,
                 filename=None, *, daemon=None, q=None):
        super().__init__(group=group, target=target, name=name,
                         daemon=daemon)

        self.filename = filename
        self.q = q

        return

    def run(self):
        logging.debug('Initialization of Conf file checker thread ')
        drive = self.auth() # Authorization
        content = self.download_file(drive)
        oldconf = self.parse_json(content)
        while True:
            content = self.download_file(drive)
            newconf = self.parse_json(content)

            if (newconf != oldconf):
                oldconf = newconf
                logging.debug("Configuration changed!!")

            # sleep thread for some amount of time
            time.sleep(BaseConfig.confCheckTime)

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

        conffile = drive.CreateFile({'id': self.filename})
        conffile.FetchMetadata()

        logging.debug('title: %s, mimeType: %s' % (conffile['title'],
                        conffile['mimeType']))

        return conffile.GetContentString()

    def parse_json(self, jsonfile):
        return json.loads(jsonfile)

    def load_config(self, configdata):
        pass

class FileUploader(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 storage=None, *, daemon=None):
        super().__init__(group=group, target=target, name=name,
                         daemon=daemon)

        self.storage = storage
        self.storage_init = False

    def run(self):
        logging.debug('Initialization of file uploader thread')
        while True:
            if (storage == 'dropbox'):
                if storage_init:
                    if not q.empty():
                        dropbox_upload(q.get())
                else:
                    dropbox_init()
                    self.storage_init = True
            time.sleep(5)
        return

    def gdrive_init(gauth):
        return GoogleDrive(gauth)

    def gdrive_upload(filename):
        file_upload = drive.CreateFile({'title': filename})
        file_upload.Upload() # Upload the file.
        logging.debug('title: %s, id: %s' % (file_upload['title'],
                        file_upload['id']))

    def dropbox_init():
        #Setup Dropbox session
        dbx = dropbox.Dropbox(UserConfig.dropbox_token)
        #Check if it works
        try:
            dbx.users_get_current_account()
        except AuthError as err:
            logging.error('ERROR: Invalid access token; re-generate token')

        return dbx

    def dropbox_upload(filename):
        with open(filename, 'rb') as f:
            data = f.read()
        with stopwatch('upload %d bytes' % len(data)):
            try:
                dbx.files_upload(data, filename, mute=False)
                logging.info('Uploading photo %s to Dropbox' % filename)
            except dropbox.exceptions.ApiError as err:
                logging.error('*** API error %s' % err)
        f.close()






#w = ConfFileDownloader(filename='1TBLQfJHsZYPXDvcpS_ysg6asxf-5_Oku')

#w.start()
