
#@dag(schedule_interval=None, start_date="2023-10-01", catchup=False, tags=["youtube_crawler"])
@dag
def youtube_crawler_dag():
    """
    A simple DAG to crawl YouTube videos, transcribe them, and store the results.
    """
    from airflow.sdk import dag, task, chain
    import yt_dlp

    @task 
    def fetch_video():
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

    @task 
    def transcribe_youtube_videos(video_ids, video_urls):
        import whisper
        from langchain_core.documents import Document
        import os
        from pathlib import Path
        print("🎤 Transcribing YouTube videos ...")
        os.makedirs("YouTube", exist_ok=True)
        model = whisper.load_model("tiny", device="cpu")
        youtube_docs = []

        for video_url, video_id in zip(video_urls, video_ids):
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
            print(youtube_docs[:2])

        return youtube_docs

        _fetch_video = fetch_video()
        _transcribe_youtube_videos = transcribe_youtube_videos(video_urls=_fetch_video[0], video_ids=_fetch_video[1])

        chain(
            _fetch_video,
            _transcribe_youtube_videos
        )

# Register the DAGs
from airflow.sdk import register_dag
register_dag(youtube_crawler_dag, "youtube_crawler_dag")


youtube_crawler_dag()
