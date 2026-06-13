import os
import re
import json
import argparse
import urllib.request
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def generate_description(title):
    prompt = f"""Napiš popisek pro YouTube epizodu podcastu OTISK s názvem: "{title}"

Popisek musí mít přesně tuto strukturu:

1. Úvodní odstavec (3-4 věty): zákulisní/kontroverzní úhel pohledu na osobu nebo příběh. Žádné klišé, žádné chvály. Konkrétní, drsné, zajímavé.

2. Druhý odstavec (2-3 věty): co epizoda zkoumá a proč je to jinak než jinde.

3. Sekce "🎙️ V epizodě uslyšíš:" se 4-5 odrážkami (–) — konkrétní témata z příběhu osoby.

4. Jeden řádek: "📌 OTISK je podcast o lidech, kteří zanechali stopu — ať chtěli, nebo ne."

5. Hashtags: 6-8 relevantních hashtagů česky i anglicky, včetně #OTISK #Podcast #Byznys

Piš česky. Tón: přímý, novinářský, bez motivačních klišé. Žádné "inspirativní", "úžasné", "neuvěřitelné"."""

    data = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode('utf-8')

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-api-key": os.environ['ANTHROPIC_API_KEY'],
            "anthropic-version": "2023-06-01"
        }
    )

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
        return result['content'][0]['text']

def sanitize_title(title):
    title = re.sub(r'[<>]', '', title)
    title = title.strip()
    if len(title) > 100:
        title = title[:97] + '...'
    return title or 'Otisk: Epizoda'

def upload_video(title, file_path):
    title = sanitize_title(title)
    print(f"Titul: {title}")

    description = generate_description(title)
    print(f"Popisek vygenerován.")

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
    upload_video(title, args.file)
