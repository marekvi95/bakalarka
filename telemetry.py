import httplib2
import os
import random
import io
import logging
import logging.handlers
import queue

import psutil
from apiclient import discovery
from apiclient.http import MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from datetime import datetime


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

class GoogleHandler():
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

    def add_sheet_line(self, service, line=None):
        self.service = service
        self.line = line

        spreadsheetId = '1XNmtg0NoCiU03NDZohlBwmOpFC-heHWbdRzY_tTYjhg'
        rangeName = 'Log!A:A'
        values = [
                self.line
        ]
        body = {
        'values': values
        }
        result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheetId, range=rangeName,
        valueInputOption="USER_ENTERED", body=body).execute()

        print('{0} cells updated.'.format(result.get('updates')));

    def upload_file(self, service, filename):

        file_metadata = {'name': filename}
        media = MediaFileUpload(filename,
                            mimetype='image/jpeg')
        file = service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
        print(file.get('id'))

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




def gdrive():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    results = service.files().list(
        pageSize=10,fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print('{0} ({1})'.format(item['name'], item['id']))

    file_metadata = {'name': 'rpizero.jpg'}
    media = MediaFileUpload('rpizero.jpg',
                        mimetype='image/jpeg')
    file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
    print(file.get('id'))
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
print(q1.get())
print(q1.get())

#gh = GoogleHandler()
#crd = gh.get_credentials()
#print(crd)
#srvc = gh.get_sheets_service(credentials=crd)
#gh.add_sheet_line(service=srvc, line = [str(datetime.now()),"OK",random.randint(10,15),random.randint(0,40),
#psutil.cpu_percent(),psutil.virtual_memory().percent])
