
from __future__ import print_function
import httplib2
import os
from apiclient import errors
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

#Get Google credentials

print('Get Google credentials')

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'


def get_credentials():
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
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():

#Establish connection to Drive API

    print('Establish connection to Drive API')
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v3', http=http)


#Search for folder

    print('Search for folder')
    folder_exist = None
    page_token = None
    while True:
        response = drive_service.files().list(q="mimeType='application/vnd.google-apps.folder' and fullText contains 'Invoices' and trashed = false",
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name)',
                                              pageToken=page_token).execute()
        for file in response.get('files', []):
            # Process change
            print('Found file: %s (%s)' % (file.get('name'), file.get('id')))
            folder_exist = True
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break;

# Create new folder
    if folder_exist is None:
        print('Create new folder')
        file_metadata = {
            'name': 'Invoices',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = drive_service.files().create(body=file_metadata,
                                  fields='id').execute()
        print('Folder ID: %s' % file.get('id'))

#TO DO
# Need to implement search folder permission, so we can enable permission for new users or deny permissions for disabled users


#Grant folder permissions

    #TO DO
    #Replace folder exist with permission exist
    if folder_exist is None:
        print('Grant folder permissions')
        file_id = file.get('id')

        def callback(request_id, response, exception):
            if exception:
                # Handle error
                print
                exception
            else:
                print
                "Permission Id: %s" % response.get('id')

        batch = drive_service.new_batch_http_request(callback=callback)
        user_permission = {
            'type': 'user',
            'role': 'reader',
            'emailAddress': 'matanius@gmail.com'
        }
        batch.add(drive_service.permissions().create(
            fileId=file_id,
            body=user_permission,
            fields='id',
        ))
        batch.execute()


#drive properties

    print('drive properties')

    results = drive_service.files().list(
        pageSize=10,fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print('{0} ({1})'.format(item['name'], item['id']))

if __name__ == '__main__':
    main()