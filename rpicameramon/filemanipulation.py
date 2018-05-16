import logging
import threading
import time
from io import StringIO
import json
import queue
import contextlib
import datetime
import re

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import dropbox

import config
from config import BaseConfig
from config import UserConfig


class ConfFileDownloader(threading.Thread):
    """
        ConfFileDownloader is a subclass of a Thread class
        First it loads the initial JSON configuration from Google drive
        and then it check if the configuration was changed. If yes, it loads it.

        Attributes:
            filename (string): file ID of JSON configuration file on Google drive
    """
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
        conf = self.parse_json(content)
        modified = self.get_timestamp(drive)

        UserConfig.load_config(conf)

        while True:
            new = self.get_timestamp(drive)

            if (new != modified):
                modified = new
                logging.info("Configuration has been changed!!")

                content = self.download_file(drive)
                conf = self.parse_json(content)

                UserConfig.load_config(conf)

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


    def get_timestamp(self, drive):

        conffile = drive.CreateFile({'id': self.filename})
        conffile.FetchMetadata(fields='modifiedDate')

        return conffile['modifiedDate']


    def parse_json(self, jsonfile):
        return json.loads(jsonfile)

    def load_config(self, configdata):
        pass

class FileUploader(threading.Thread):
    """
        This class provides a File uploader thread for uploading
        captured photos. It supports google drive and dropbox (experimental)

        Attributes:
            storage (str): storage type (gdrive or dropbox)
            q (Queue obj): queue with filenames of pictures to be uploaded
    """
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
                    if (UserConfig.mode == 'batch'):
                        dt = datetime.datetime.now()
                        if (dt.hour == BaseConfig.batchUploadWindow):
                            if not self.q.empty():
                                logging.debug('Batch upload')
                                self.gdrive_upload(filename = self.q.get()),
                                            drive = self.drive)
                    else:
                        if not self.q.empty():
                            self.gdrive_upload(filename = self.q.get(),
                                            drive = self.drive)
                else:
                    self.drive = self.gdrive_init()
                    self.gdrive_is_init = True

            time.sleep(BaseConfig.fileUploadSleep)
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
        file_upload = drive.CreateFile({"parents": [{"kind": "drive#fileLink",
                                            "id": BaseConfig.pictureFolderID}]})
        #file_upload = drive.CreateFile({'title': filename})
        # filename regex matching
        match = re.search("[^/]+$", filename)
        file = match.group(0)
        file_upload['title'] = file

        file_upload.SetContentFile(filename)

        with stopwatch('uploading file to gdrive'):
            try:
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
