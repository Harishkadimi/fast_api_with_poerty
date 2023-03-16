import os,requests,shutil
from fastapi import FastAPI,HTTPException

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

app = FastAPI()

# flow = InstalledAppFlow.from_client_secrets_file(
#     'inter.json',
#     scopes=['https://www.googleapis.com/auth/drive']
# )
# Run the flow to get a credentials object
# credentials = flow.run_local_server(port=0)

# Save the credentials object for future use
creds_file = 'inter.json'
# with open(creds_file, 'w') as f:
#     f.write(credentials.to_json())

# Set up the Google Drive API client
creds = Credentials.from_authorized_user_file(creds_file, ['https://www.googleapis.com/auth/drive'])
service = build('drive', 'v3', credentials=creds)


@app.post('/upload-video-to-drive')
async def upload_video_to_drive(video_link: str):
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

@app.post('/upload_file')
def fileupload_to_drive():
    
    # Save the credentials object for future use
    creds_file = 'inter.json'
    # Create a Credentials object from the saved credentials
    creds = Credentials.from_authorized_user_file(creds_file, ['https://www.googleapis.com/auth/drive'])


    # Set up the Drive API client
    service = build('drive', 'v3', credentials=creds)

    # Set up the file metadata
    file_metadata = {
        'name': 'BigBuckBunny.mp4'
    }

    # Set up the file content
    file_path = 'BigBuckBunny.mp4'
    file_mime_type = 'video/mp4'
    file = open(file_path, 'rb')
    file_content = file.read()

    # Create the file in Google Drive
    try:
        media = MediaFileUpload(file_path, mimetype=file_mime_type)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        return ('File ID: %s' % file.get('id'))
    except HttpError as error:
        return ('An error occurred: %s' % error)
        file = None


@app.get("/download")
async def download_file(url: str, folder_path: str, file_name: str):
    # Ensure that the folder path exists
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail="Folder not found")

    # Download the file from the URL
    response = requests.get(url, stream=True)

    # Raise an exception if the file could not be downloaded
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="File could not be downloaded")

    # Save the downloaded file to the specified folder with the given file name
    with open(os.path.join(folder_path, file_name), "wb") as f:
        shutil.copyfileobj(response.raw, f)

    return {"message": f"File downloaded and saved to {folder_path}/{file_name}"}



@app.get("/get_video_url")
def get_video_url(recording_id: str, access_token: str):
    # Make the GET request to the Zoom API's "Get Recording" endpoint
    response = requests.get(
        f"https://api.zoom.us/v2/meetings/{recording_id}/recordings",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"include_fields": "download_access_token"}
    )

    # Check if the request was successful
    if response.status_code != 200:
        return {"error": "Failed to retrieve recording information"}

    # Extract the download URL from the response data
    data = response.json()
    if len(data["recording_files"]) == 0:
        return {"error": "No recording files found for this meeting"}
    download_url = data["recording_files"][0]["download_url"] + "?access_token=" + data["download_access_token"]

    # Return the download URL to the client
    return {"download_url": download_url}

###########################################################################################################
# from fastapi import FastAPI, File, UploadFile
# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# import io

# app = FastAPI()

# # Load the OAuth 2.0 credentials
# creds = Credentials.from_authorized_user_file('path/to/credentials.json')

# # Create a Google Drive API client
# drive_service = build('drive', 'v3', credentials=creds)

# @app.post('/upload')
# async def upload_file(file: UploadFile):
#     try:
#         # Create the file in the user's Google Drive account
#         file_metadata = {'name': file.filename}
#         media = io.BytesIO(file.file.read())
#         file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

#         # Return the ID of the file in the user's Google Drive account
#         return {'file_id': file.get('id')}

#     except HttpError as error:
#         return {'error': str(error)}

##################################################################################################################################
# from fastapi import FastAPI
# import requests
# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from googleapiclient.http import MediaFileUpload

# app = FastAPI()

# @app.post("/upload_file_to_drive")
# async def upload_file_to_drive(file_url: str):
#     try:
#         # Download file from URL
#         file_name = file_url.split("/")[-1]
#         r = requests.get(file_url, stream=True)
#         with open(file_name, "wb") as f:
#             for chunk in r.iter_content(chunk_size=8192):
#                 f.write(chunk)

#         # Authenticate with Google Drive API
#         creds = Credentials.from_authorized_user_file("inter.json")

#         # Create Drive API client
#         service = build("drive", "v3", credentials=creds)

#         # Upload file to Google Drive
#         file_metadata = {"name": file_name}
#         media = MediaFileUpload(file_name, resumable=True)
#         file = service.files().create(
#             body=file_metadata,
#             media_body=media,
#             fields="id"
#         ).execute()

#         return {"file_id": file.get("id")}

#     except HttpError as error:
#         return {"error": f"An error occurred: {error}"}
