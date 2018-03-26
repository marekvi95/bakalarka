import logging
import threading
import time
from io import StringIO
import json
import queue
import contextlib

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import dropbox

import config
from config import BaseConfig
from config import UserConfig


class ConfFileDownloader(threading.Thread):

    def __init__(self, group=None, target=None, name=None,
                 filename=None, *, daemon=None):
        super().__init__(group=group, target=target, name=name,
                         daemon=daemon)

        self.filename = filename
        self.setName('ConfFileDownloader')

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
                logging.info("Configuration has been changed!!")
                UserConfig.load_config(newconf)

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
                 storage=None, *, daemon=None, q=None):
        super().__init__(group=group, target=target, name=name,
                         daemon=daemon)

        self.storage = storage
        self.dropbox_is_init = False
        self.gdrive_is_init = False
        self.q = q

        self.setName('FileUploader')

    def run(self):
        logging.debug('Initialization of file uploader thread')
        while True:
            if (self.storage == 'dropbox'):
                if self.dropbox_is_init:
                    if not self.q.empty():
                        self.dropbox_upload(filename = self.q.get(),
                                            dbx = self.dbx)
                else:
                    self.dbx = self.dropbox_init()
                    self.dropbox_is_init = True

            if (self.storage == 'gdrive'):
                if self.gdrive_is_init:
                    if not self.q.empty():
                        self.gdrive_upload(filename = self.q.get(),
                                            drive = self.drive)
                else:
                    self.drive = self.gdrive_init()
                    self.gdrive_is_init = True
            time.sleep(5)
        return

    def gdrive_init(self):
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

        return GoogleDrive(gauth)

    def gdrive_upload(self, filename, drive):
        file_upload = drive.CreateFile({'title': filename})
        file_upload.SetContentFile(filename)
        file_upload.Upload() # Upload the file.
        logging.debug('title: %s, id: %s' % (file_upload['title'],
                        file_upload['id']))

    def dropbox_init(self):
        #Setup Dropbox session
        dbx = dropbox.Dropbox(UserConfig.dropbox_token)
        #Check if it works
        try:
            dbx.users_get_current_account()
        except AuthError as err:
            logging.error('ERROR: Invalid access token; re-generate token')

        return dbx

    def dropbox_upload(self, filename, dbx):
        with open(filename, 'rb') as f:
            data = f.read()
        with stopwatch('upload %d bytes' % len(data)):
            try:
                dbx.files_upload(data, filename, mute=False)
                logging.info('Uploading photo %s to Dropbox' % filename)
            except dropbox.exceptions.ApiError as err:
                logging.error('*** API error %s' % err)
        f.close()


@contextlib.contextmanager
def stopwatch(message):
    # Measure how long the block of code took to process
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        logging.info('Total elapsed time for %s: %.3f' % (message, t1 - t0))
