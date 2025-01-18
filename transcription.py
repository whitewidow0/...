# transcription.py
import yt_dlp
import whisper
from transformers import pipeline
import textwrap
import os

# Initialize models
whisper_model = whisper.load_model("base")
filter_model = pipeline("text2text-generation", model="facebook/bart-large-cnn")

def get_video_metadata(video_url):
    ydl_opts = {'quiet': True, 'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
    return {
        "title": info_dict.get("title"),
        "uploader": info_dict.get("uploader"),
        "description": info_dict.get("description"),
        "duration": info_dict.get("duration"),
    }

def download_audio(video_url, output_name):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_name}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

def transcribe_audio(audio_file):
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"File {audio_file} not found.")
    result = whisper_model.transcribe(audio_file)
    return result['text']

def split_text(text, max_length=1000):
    return textwrap.wrap(text, max_length)

def filter_content(text):
    chunks = split_text(text)
    filtered = ""
    for chunk in chunks:
        filtered += filter_model(f"Summarize and refine: {chunk}", max_length=200)[0]['generated_text'] + " "
    return filtered.strip()

def process_video(video_url):
    # Step 1: Metadata
    metadata = get_video_metadata(video_url)
    print("Metadata:", metadata)

    # Step 2: Download Audio
    output_name = metadata['title'].replace(" ", "_")  # Simplified unique naming
    download_audio(video_url, output_name)

    # Step 3: Transcription
    transcription = transcribe_audio(f"{output_name}.mp3")
    print("Transcription:", transcription)

    # Step 4: Filtering
    filtered = filter_content(transcription)
    print("Filtered Content:", filtered)

    # Step 5: Save Results
    with open(f"output/{output_name}_filtered.txt", "w") as f:
        f.write(filtered)