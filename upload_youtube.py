import os
import re
import argparse
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def sanitize_title(title):
    title = re.sub(r'[<>]', '', title)
    title = title.strip()
    if len(title) > 100:
        title = title[:97] + '...'
    return title or 'Otisk: Epizoda'

def upload_video(title, description, file_path):
    title = sanitize_title(title)
    print(f"Titul: {title}")
    print(f"Popisek: {description[:100]}...")

    creds = Credentials(
        token=None,
        refresh_token=os.environ['YOUTUBE_REFRESH_TOKEN'],
        client_id=os.environ['YOUTUBE_CLIENT_ID'],
        client_secret=os.environ['YOUTUBE_CLIENT_SECRET'],
        token_uri='https://oauth2.googleapis.com/token',
        scopes=['https://www.googleapis.com/auth/youtube.upload']
    )
    creds.refresh(Request())

    youtube = build('youtube', 'v3', credentials=creds)

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': [
                'OTISK', 'podcast', 'podnikání', 'byznys', 'podnikatel',
                'příběhy', 'motivace', 'česky', 'startup', 'úspěch'
            ],
            'categoryId': '22'
        },
        'status': {
            'privacyStatus': 'public'
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    response = request.execute()
    print(f"✅ Video nahráno: https://www.youtube.com/watch?v={response['id']}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    args = parser.parse_args()
    title = os.environ.get('VIDEO_TITLE', '').strip() or 'Otisk: Epizoda'
    description = os.environ.get('VIDEO_DESCRIPTION', '').strip() or 'OTISK je podcast o lidech, kteří zanechali stopu — ať chtěli, nebo ne.'
    upload_video(title, description, args.file)
