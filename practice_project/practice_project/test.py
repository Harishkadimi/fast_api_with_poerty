import os
import requests
from fastapi import FastAPI

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# app = FastAPI()

flow = InstalledAppFlow.from_client_secrets_file(
    './practice_project/practice_project/inter.json',
    scopes=['https://www.googleapis.com/auth/drive']
)

# Run the flow to get a credentials object
credentials = flow.run_local_server(port=8080)

# Save the credentials object for future use
creds_file = './practice_project/practice_project/inter.json'
with open(creds_file, 'w') as f:
    f.write(credentials.to_json())

# Set up the Google Drive API client
creds = Credentials.from_authorized_user_file(creds_file, ['https://www.googleapis.com/auth/drive'])
service = build('drive', 'v3', credentials=creds)


# @app.post('/upload-video-to-drive')
def upload_video_to_drive(video_link: str):
    # Download the video from the link
    r = requests.get(video_link, stream=True)
    file_size = int(r.headers.get('Content-Length', 0))
    filename = video_link.split('/')[-1]
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(1024 * 1024):
            if chunk:
                f.write(chunk)

    # Upload the video to Google Drive
    file_metadata = {'name': filename}
    media = MediaFileUpload(filename, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f'File ID: {file.get("id")}')

    # Delete the local copy of the video
    os.remove(filename)

    return {'message': f'Video {filename} uploaded to Google Drive.'}

print(upload_video_to_drive('https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'))
