import httplib2
import os
import random
import io
import logging
import logging.handlers
import queue
import time
import threading
import json

import psutil
from apiclient import discovery
from apiclient.http import MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from datetime import datetime

from config import BaseConfig
from config import UserConfig

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Camera security system app'

class GoogleHandler:

    def __init__(self):
        self.credentials = self.get_credentials()
        self.sheetsService = self.get_sheets_service(self.credentials)

    def get_credentials(self):
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

        return credentials

    def get_sheets_service(self, credentials):
        """Gets Google Sheets Service v4

        Returns:
                Google Sheets service object
        """

        self.credentials = credentials

        http = self.credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        service = discovery.build('sheets', 'v4', http=http,
                                  discoveryServiceUrl=discoveryUrl)
        return service

    def get_file_service(self, credentials):
        """Gets Google Drive Service v3

        Retruns:
            Google Drive service object
        """
        self.credentials = credentials

        http = credentials.authorize(httplib2.Http())
        service = discovery.build('drive', 'v3', http=http)

        return service

    def add_sheet_line(self, service=None, line=None, spreadsheetId=None,
                        rangeName=None):
        """Append a line/lines to Google Sheet.

        Args:
            service (obj): Google Sheets Service object
            line (nested list): matrix of data to be put into Google Sheet
            spreadsheetId (str): Id of spreadsheet
            rangeName (str): Range in a spreadsheet
        """

        body = {
            'values': line
            }

        result = self.sheetsService.spreadsheets().values().append(
        spreadsheetId=spreadsheetId, range=rangeName,
        valueInputOption="USER_ENTERED", body=body).execute()

        #logging.debug('{0} cells updated.'.format(result.get('updates')));

    def upload_file(self, service, filename):
        """Uploads a image/jpeg file to the Google Drive.

        Args:
            service (obj): Google Drive Service object
            filename (str): full path to the file.

        """
        file_metadata = {'name': filename}
        media = MediaFileUpload(filename,
                            mimetype='image/jpeg')
        file = service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
        logging.debug(file.get('id'))

class LogSender(threading.Thread):
    """
        LogSender class is a subclass of a Thread class.
        It provides a functionality to send a captured log to
        Google Sheets. It should be used together with the
        logging.handlers.QueueHandler class as a handler for logging.
        LogSender works only in specified time intervals,
        dequeues everything in logQueue, sends it
        to the Google Sheets and goes sleep for the amount of time
        specified by the variable fileUploadSleep

        Attributes:
            logQueue (obj): queue.Queue object with logRecord (obj)
            enqueued
            googleHandler (obj): GoogleHandler instance object

    """
    def __init__(self, logQueue, googleHandler):

        super().__init__(group=None, target=None, name=None,
                     daemon=None)

        self.logQueue = logQueue
        self.googleHandler = googleHandler

        self.setName('LogSender')

    def run(self):
        self.array = []
        while True:
            if not self.logQueue.empty():
                while not self.logQueue.empty():
                    self.record = self.logQueue.get()

                    self.newLine = [self.record.asctime, self.record.levelname,
                                    self.record.threadName,  self.record.msg]

                    self.array.append(self.newLine)

                self.googleHandler.add_sheet_line(
                                spreadsheetId=BaseConfig.dashboardFileID,
                                rangeName=BaseConfig.msgRange,
                                line=self.array)

                self.array = [] #empty the array

            time.sleep(BaseConfig.fileUploadSleep)

class TelemetrySender(threading.Thread):
    """
        Telemetry class is a subclass of a Thread class.
        It provides a functionality for sending a telemetric data to
        Google Sheets.

        Attributes:

    """
    def __init__(self, googleHandler):

        self.googleHandler = googleHandler

        super().__init__(group=None, target=None, name=None,
                     daemon=None)

        self.setName('TelemetrySender')


    def run(self):
        while True:
            self.record = self.getTelemetry()

            self.googleHandler.add_sheet_line(spreadsheetId=BaseConfig.dashboardFileID,
                                rangeName=BaseConfig.logRange,
                                line=[self.record])
            time.sleep(BaseConfig.fileUploadSleep)

    def getTelemetry(self):
        self.time = str(datetime.now())
        self.chargingStatus = "OK"
        self.batteryVoltage = random.randint(10,15)
        self.batteryTemperature = random.randint(0,40)
        self.cpuLoad = psutil.cpu_percent()
        self.ramLoad = psutil.virtual_memory().percent

        self.telemetry = [self.time, self.chargingStatus, self.batteryVoltage,
                            self.batteryTemperature, self.cpuLoad, self.ramLoad]

        return self.telemetry
