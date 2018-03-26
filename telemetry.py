import httplib2
import os
import random
import io
import logging
import logging.handlers
import queue
import time

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

class SheetsLogHandler(logging.handlers.QueueHandler):
    def __init__(self,queue):
        print("initialized")
        self.queue = queue
        super().__init__(queue)

    def enqueue(self, record):
        self.queue.put(record)
        print(record)

    def close(self):
        pass
        #self.queue.close()

q1 = queue.Queue(-1)
#q1.put('heejo')
handler = SheetsLogHandler(q1)

# define a Handler which writes INFO messages or higher to the sys.stderr
handler.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(threadName)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
handler.setFormatter(formatter)
logging.getLogger('').addHandler(handler)
logging.info('TESSST!!')
logging.debug('TESST2!')
logging.error('heej')

print(q1.get())
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
