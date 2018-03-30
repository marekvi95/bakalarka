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
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

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
        self.credentials = credentials

        http = self.credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        service = discovery.build('sheets', 'v4', http=http,
                                  discoveryServiceUrl=discoveryUrl)
        return service

    def get_file_service(self, credentials):
        self.credentials = credentials

        http = credentials.authorize(httplib2.Http())
        service = discovery.build('drive', 'v3', http=http)

        return service

    def add_sheet_line(self, service=None, line=None, spreadsheetId=None,
                        rangeName=None):

        body = {
            'values': line
            }

        result = self.sheetsService.spreadsheets().values().append(
        spreadsheetId=spreadsheetId, range=rangeName,
        valueInputOption="USER_ENTERED", body=body).execute()

        #logging.debug('{0} cells updated.'.format(result.get('updates')));

    def upload_file(self, service, filename):

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
        to the Google Sheets and goes sleep.

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

            time.sleep(1)

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
                time.sleep(5)

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




#while True:
#    logging.debug('testt')
#    logging.debug('testt jeste jednou')
#    logging.info('testt jeste jeste jednou')
#    logging.error('chyba')
#    logging.critical('kriticka chyba')
#    time.sleep(5)
#logging.info('tes2tt')



#q1 = queue.Queue(-1)
#q1.put('heejo')
#handler = SheetsLogHandler(q1)

# define a Handler which writes INFO messages or higher to the sys.stderr
#handler.setLevel(logging.INFO)
# set a format which is simpler for console use
#formatter = logging.Formatter('%(threadName)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
#handler.setFormatter(formatter)
#logging.getLogger('').addHandler(handler)
#logging.info('TESSST!!')
#logging.debug('TESST2!')
#logging.error('heej')

#print(q1.get())
#print(q1.get())
#print(q1.get())

#gh = GoogleHandler()
#crd = gh.get_credentials()
#print(crd)
#srvc = gh.get_sheets_service(credentials=crd)
#while True:
#    gh.add_sheet_line(service=srvc, spreadsheetId=BaseConfig.dashboardFileID,
#                    rangeName=BaseConfig.logRange,
#                                        line = [str(datetime.now()),
#                                        "OK",random.randint(10,15),
#                                        random.randint(0,40),
#                                        psutil.cpu_percent(),
#                                        psutil.virtual_memory().percent])
#    time.sleep(1)

#srvc2 = gh.get_file_service(crd)
#gh.upload_file(service=srvc2, filename='../../../Pictures/IMG_9210.jpg')
