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


logging.basicConfig(filename='logfile.log',level=logging.DEBUG,
                   format='%(asctime)s %(threadName)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',)

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

class GoogleHandler:
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
            'values': [line]
            }

        result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheetId, range=rangeName,
        valueInputOption="USER_ENTERED", body=body).execute()

        logging.debug('{0} cells updated.'.format(result.get('updates')));

    def upload_file(self, service, filename):

        file_metadata = {'name': filename}
        media = MediaFileUpload(filename,
                            mimetype='image/jpeg')
        file = service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
        logging.debug(file.get('id'))

class LogSender(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
             storage=None, *, daemon=None, q, gh, service):

        super().__init__(group=group, target=target, name=name,
                     daemon=daemon)
        self.q = q
        self.gh = gh
        self.service = service

        self.setName('LogSender')

    def run(self):
        while True:
            if not self.q.empty():

                self.logObject = self.q.get()

                self.msg = self.logObject.__dict__['msg']
                self.levelname = self.logObject.__dict__['levelname']
                self.threadName = self.logObject.__dict__['threadName']
                self.asctime = self.logObject.__dict__['asctime']

                self.newLine = [self.asctime, self.levelname,
                                self. threadName,  self.msg]

                print(self.logObject.__dict__)

                print(self.msg)
                self.gh.add_sheet_line(service=self.service,
                                spreadsheetId=BaseConfig.dashboardFileID,
                                rangeName=BaseConfig.msgRange,
                                line=self.newLine)
            time.sleep(1)


class SheetsLogHandler(logging.handlers.QueueHandler):
    def __init__(self,queue):
        print("initialized")
        self.queue = queue
        super().__init__(queue)

    def enqueue(self, record):
        #formatted = self.format(record)
        self.queue.put(record)
        print(record)

    def close(self):
        pass
        #self.queue.close()

class HandlerSheets(logging.Handler):
    def __init__(self, gh, srvc):
        self.gh = gh
        self.srvc = srvc

        super().__init__()

    def emit(self,record):
        print('Emituju')
        print(record)
        formatted = self.format(record)
        print(formatted)
        #self.gh.add_sheet_line(service=srvc, spreadsheetId=BaseConfig.dashboardFileID,
        #                    rangeName=BaseConfig.logRange, line=[formatted])

class SheetsLogListener(logging.handlers.QueueListener):
    def _init_(self,queue,sheetHandler):
        self.queue = queue
        self.sheetHandler = sheetHandler


q1 = queue.Queue(-1)
gh = GoogleHandler()
crd = gh.get_credentials()
print(crd)
srvc = gh.get_sheets_service(credentials=crd)
handler = logging.StreamHandler()
handler2 = SheetsLogHandler(q1)
handler2.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(threadName)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
handler2.setFormatter(formatter)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(handler2)
logging.getLogger('').addHandler(handler)

testThread = LogSender(q=q1, gh=gh, service=srvc)
testThread.start()


while True:
    logging.debug('testt')
    logging.debug('testt jeste jednou')
    logging.info('testt jeste jeste jednou')
    logging.error('chyba')
    logging.critical('kriticka chyba')
    time.sleep(5)
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
