def fetch_video():
    import yt_dlp
    ydl_opts = {
        'ignoreerrors': True,
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': False,
    }
    # Channel Details
    CHANNEL_ID = "UCrrqGYx98H1dPdZsNb1i9-g"
    CHANNEL_URL = f"https://www.youtube.com/channel/{CHANNEL_ID}"
    print("🎬 YouTube Crawler started ...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(CHANNEL_URL, download=False)
        video_urls, video_ids = [], []

        if 'entries' in result:
            for entry in result['entries']:
                if entry and 'id' in entry:
                    video_ids.append(entry['id'])
                    video_urls.append(f"https://www.youtube.com/watch?v={entry['id']}")
                    print("url", entry['id'], "appended.")

    print(f"✅ Found {len(video_ids)} videos on channel: {CHANNEL_URL}")
    return video_ids, video_urls

def crawler_youtube(max_videos=100):
    import whisper
    from langchain_core.documents import Document
    import os
    from pathlib import Path

    video_ids, video_urls = fetch_video()

    print("🎤 Transcribing YouTube videos ...")
    os.makedirs("YouTube", exist_ok=True)
    model = whisper.load_model("tiny", device="cpu")
    youtube_docs = []

    counter = 0
    for video_url, video_id in zip(video_urls, video_ids):
        if counter >= max_videos:
            break
        counter += 1
        print(f"📥 Processing: {video_id}")
        output_file = f"YouTube/{video_id}.mp3"

        # Download .mp3 if not already downloaded
        if not Path(output_file).exists():
            ret = os.system(f'yt-dlp -x --audio-format mp3 -o "{output_file}" {video_url}')
            if ret != 0:
                print(f"❌ Failed to download: {video_url}")
                continue

        try:
            result = model.transcribe(output_file)
            print(f"📝 Transcribed: {video_id}")
            doc = Document(
                page_content=result["text"],
                metadata={
                    "source": video_url,
                    "video_id": video_id,
                    "type": "YouTube"
                }
            )
            youtube_docs.append(doc)
        except Exception as e:
            print(f"⚠️ Transcription failed for {video_id}: {e}")

        print(f"\n✅ Completed. Total documents created: {len(youtube_docs)}")

    return youtube_docs

