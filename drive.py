# import the required libraries
from __future__ import print_function
import pickle
import os.path
import io
import shutil
import requests
from mimetypes import MimeTypes
from googleapiclient.errors import HttpError 
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload


class DriveAPI:
    global SCOPES

    # Define the scopes
    SCOPES = ['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/presentations','https://www.googleapis.com/auth/spreadsheets']

    def __init__(self, choice):

        # Variable self.creds will
        # store the user access token.
        # If no valid token found
        # we will create one.
        self.creds = None
        self.choice = choice
        self.query = "mimeType='application/vnd.google-apps.presentation' or mimeType='application/vnd.google-apps.spreadsheet'"
        if self.choice == 1:
            self.query = "mimeType='application/vnd.google-apps.presentation'"
        elif self.choice == 2:
            self.query = "mimeType='application/vnd.google-apps.spreadsheet'"

        # The file token.pickle stores the
        # user's access and refresh tokens. It is
        # created automatically when the authorization
        # flow completes for the first time.

        # Check if file token.pickle exists
        if os.path.exists('token.pickle'):

            # Read the token from the file and
            # store it in the variable self.creds
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        # If no valid credentials are available,
        # request the user to log in.
        if not self.creds or not self.creds.valid:

            # If token is expired, it will be refreshed,
            # else, we will request a new one.
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=8080)

            # Save the access token in token.pickle
            # file for future usage
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)


        # Connect to the API service
        self.service = build('drive', 'v3', credentials=self.creds)
        results = self.service.files().list(q=self.query, pageSize=100, fields="files(id, name, mimeType)").execute()
        items = results.get('files', [])

        # print a list of files
        print("Here's a list of files: \n")
        print(*items, sep="\n", end="\n\n")

    def FileDownload(self, file_id, file_name):
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()

        # Initialise a downloader object to download the file
        downloader = MediaIoBaseDownload(fh, request, chunksize=204800)
        done = False

        try:
            # Download the data in chunks
            while not done:
                status, done = downloader.next_chunk()

            fh.seek(0)

            # Write the received data to the file
            with open(file_name, 'wb') as f:
                shutil.copyfileobj(fh, f)

            print("File Downloaded")
            # Return True if file Downloaded successfully
            return True
        except:

            # Return False if something went wrong
            print("Something went wrong.")
            return False

    def FileUpload(self, filepath):

        # Extract the file name out of the file path
        name = filepath.split('/')[-1]

        # Find the MimeType of the file
        mimetype = MimeTypes().guess_type(name)[0]

        # create file metadata
        file_metadata = {'name': name}

        try:
            media = MediaFileUpload(filepath, mimetype=mimetype)

            # Create a new file in the Drive storage
            file = self.service.files().create(
                body=file_metadata, media_body=media, fields='id').execute()

            print("File Uploaded.")

        except:

            # Raise UploadError if file is not uploaded.
            raise UploadError("Can't Upload File.")

    def copy_file(self, origin_file_id, copy_title):
        file_metadata = {'name': copy_title}
        try:
            self.service.files().copy(fileId=origin_file_id, body=file_metadata).execute()
            print(f'File coppied {copy_title}')
            return None
        except (HttpError, error):
            print('An error occurred: %s' % error)
        return None


if __name__ == "__main__":
    choice = int(input(
        "Enter your choice(number): 1 - Presentation \n2 - Spreadsheets\n3 - Both\n"))
    if choice in [1, 2, 3]:
        obj = DriveAPI(choice)
        service = obj.service
        i = int(input(
            "Enter your choice(number): 1 - Download file, 2- Upload File, 3- Copy file, 4-Exit.\n"))
        if i == 1:
            f_id = input("Enter file id: ")
            f_name = input("Enter file name: ")
            obj.FileDownload(f_id, f_name)

        elif i == 2:
            f_path = input("Enter full file path: ")
            obj.FileUpload(f_path)

        elif i == 3:
            f_id = input("Enter file id: ")
            f_name = input("Enter file name: ")
            obj.copy_file(f_id, f_name)
        else:
            exit()
    else:
        exit()
