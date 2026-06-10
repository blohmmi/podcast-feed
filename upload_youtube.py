import os
import argparse
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_video(title, file_path):
    print(f"DEBUG titul: '{title}'")
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
            'description': f"""{title}
Pravda za PR verzí. Zákulisí, drby a fakta, která veřejnost nezná — příběhy nejlepších podnikatelů světa tak, jak je Forbes nepublikoval.
Jeden příběh. Jeden „Cože?!" moment. Jedno konkrétní poučení.
🎙️ Poslouchej také na Spotify a Apple Podcasts — hledej OTISK.""",
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
    parser.add_argument('--title', required=True)
    parser.add_argument('--file', required=True)
    args = parser.parse_args()
    upload_video(args.title, args.file)
