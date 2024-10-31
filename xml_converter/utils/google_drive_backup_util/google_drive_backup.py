import os.path
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


class GoogleDriveSync:

    secret_location: Path
    google_drive_connector = None
    local_files_location: Path
    google_drive_upload_directory_id: str = None

    # If modifying these scopes, delete the file token.json.
    scopes = ["https://www.googleapis.com/auth/drive.file"]

    def __init__(self, secret_location: Path, local_files_location, google_drive_upload_directory_id=None):
        self.secret_location = secret_location
        if not secret_location.exists():
            secret_location.mkdir()
            raise TypeError('The secret location did not exist. That probably means that it is empty.')

        if google_drive_upload_directory_id:
            self.google_drive_upload_directory_id = google_drive_upload_directory_id
        self.local_files_location = local_files_location
        self.google_drive_connector = self.create_google_drive_connector()

    def perform_upload(self):
        files_in_google_drive = self.get_files_in_g_drive_directory()
        local_files_not_in_google_drive = self.find_local_files_not_in_g_drive(self.local_files_location,
                                                                               files_in_google_drive)
        self.upload_files_to_google_drive(local_files_not_in_google_drive)

    def upload_files_to_google_drive(self, files_to_upload: list) -> None:

        if not files_to_upload:
            # There are no files to upload.
            return

        for f in files_to_upload:
            file_metadata = {'name': f.name, 'parents': [self.google_drive_upload_directory_id]}
            media = MediaFileUpload(f.__str__())
            try:
                file = (
                    self.google_drive_connector.files()
                    .create(body=file_metadata, media_body=media, fields='id')
                    .execute()
                )
            except HttpError as error:
                print(f"An error occurred while uploading files to Google Drive: {error}")
                file = None

    def get_files_in_g_drive_directory(self):
        # Call the Drive v3 API
        results = (
            self.google_drive_connector.files()
            .list(q=f'\'{self.google_drive_upload_directory_id}\' in parents', pageSize=1000,
                  fields="nextPageToken, files(id, name)")
            .execute()
        )
        items = results.get("files", [])
        return items

    def find_local_files_not_in_g_drive(self, local_dir_path: Path, g_drive_files) -> list:
        """
        Takes in the path to a local directory and all files found in a directory in Google Drive.
        It finds if there are files in the local directory that do not have a name that matches
        a file found in Google Drive. That means that the file has not been uploaded yet
        and that it should be uploaded now.
        This is done to avoid duplicate file uploads to Google Drive.
        :param local_dir_path: Path object that points to a directory of files that should be uploaded to Google Drive.
        :param g_drive_files: Files found in Google Drive.
        :return: A list of all local files whose names were missing from Google Drive.
        """
        g_drive_file_names = [f['name'] for f in g_drive_files]
        local_files = [f for f in local_dir_path.iterdir() if f.is_file()]

        local_files_not_in_g_drive = []
        for x in local_files:
            if x.name not in g_drive_file_names:
                local_files_not_in_g_drive.append(x)
        return local_files_not_in_g_drive

    def create_google_drive_connector(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        token_location = self.secret_location / 'token.json'
        credentials_location = self.secret_location / 'credentials.json'
        if not credentials_location.exists():
            raise FileNotFoundError('Google Drive credentials not found.')
        if token_location.exists():
            creds = Credentials.from_authorized_user_file(token_location.__str__(), self.scopes)
            # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_location.__str__(), self.scopes
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_location.__str__(), "w") as token:
                token.write(creds.to_json())

        service = build("drive", "v3", credentials=creds)
        return service

    def google_example_code(self):
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
        SCOPES = ["https://www.googleapis.com/auth/drive.file"]
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
            # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                  "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        try:
            service = build("drive", "v3", credentials=creds)

            # Call the Drive v3 API
            results = (
                service.files()
                .list(pageSize=10, fields="nextPageToken, files(id, name)")
                .execute()
            )
            items = results.get("files", [])

            if not items:
                print("No files found.")
                return
            print("Files:")
            for item in items:
                print(f"{item['name']} ({item['id']})")

            return service
        except HttpError as error:
            # TODO(developer) - Handle errors from drive API.
            print(f"An error occurred: {error}")


if __name__ == "__main__":
    images_folder_id = '1yalHa9ayltOYLYlaQgrTAkudZfzYUFBT'  # Images folder.
    files = Path(__file__).resolve().parent.parent.parent.parent / 'media' / 'gallery'
    location = Path(__file__).resolve().parent.parent.parent.parent / 'notemaster' / 'secrets' / 'google_drive'
    syncer = GoogleDriveSync(secret_location=location,
                             google_drive_upload_directory_id=images_folder_id,
                             local_files_location=files)

    syncer.perform_upload()
