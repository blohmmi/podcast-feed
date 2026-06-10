name: Upload to YouTube
on:
  workflow_dispatch:
    inputs:
      file_id:
        description: 'Google Drive File ID'
        required: true
      title:
        description: 'Episode title (název souboru z Drive)'
        required: true
      episode_num:
        description: 'Episode number'
        required: true
jobs:
  upload:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install gdown google-api-python-client google-auth-oauthlib
      - name: Download audio from Drive
        run: gdown "${{ github.event.inputs.file_id }}" -O audio.mp3
      - name: Install FFmpeg
        run: |
          sudo apt-get install -y ffmpeg || (
            wget -q https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz &&
            tar xf ffmpeg-release-amd64-static.tar.xz &&
            sudo mv ffmpeg-*-amd64-static/ffmpeg /usr/local/bin/ffmpeg
          )
      - name: Create video from audio + cover
        run: |
          ffmpeg -loop 1 -i cover.jpg -i audio.mp3 \
            -c:v libx264 -tune stillimage \
            -c:a aac -b:a 192k \
            -pix_fmt yuv420p -shortest output.mp4
      - name: Upload to YouTube
        env:
          YOUTUBE_CLIENT_ID: ${{ secrets.YOUTUBE_CLIENT_ID }}
          YOUTUBE_CLIENT_SECRET: ${{ secrets.YOUTUBE_CLIENT_SECRET }}
          YOUTUBE_REFRESH_TOKEN: ${{ secrets.YOUTUBE_REFRESH_TOKEN }}
          VIDEO_TITLE: "${{ github.event.inputs.episode_num }}. Otisk: ${{ github.event.inputs.title }}"
        run: |
          echo "Titul: $VIDEO_TITLE"
          python upload_youtube.py \
            --title "$VIDEO_TITLE" \
            --file output.mp4
