# main.py
import os
import json
import logging
from transcription import process_video
from sumarization import summarize_transcription
from flask import Flask, request, jsonify

# Set up logging
logging.basicConfig(filename='logs/workflow.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Flask app for webhook handling
app = Flask(__name__)

def process_video_workflow(video_id):
    """
    Handles the transcription and summarization workflow for a given video ID.
    """
    try:
        logging.info(f"Processing video: {video_id}")

        # Step 1: Construct the video URL
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # Step 2: Transcribe the video
        process_video(video_url)

        # Step 3: Summarize the transcription
        base_name = video_id  # Use video_id as the base name
        transcription_file = f"output/{base_name}_filtered.txt"
        if os.path.exists(transcription_file):
            logging.info(f"Summarizing transcription for video {video_id}...")
            summarize_transcription(transcription_file)
        else:
            logging.warning(f"Transcription file not found for video {video_id}")

    except Exception as e:
        logging.error(f"An error occurred while processing video {video_id}: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Handles incoming webhook payloads from YouTube.
    """
    try:
        # Parse the payload
        payload = request.json
        video_id = payload.get("videoId")
        if not video_id:
            logging.error("Error: videoId not found in the payload.")
            return jsonify({"status": "error", "message": "videoId not found"}), 400

        # Process the video
        process_video_workflow(video_id)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logging.error(f"Error handling webhook payload: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def manual_trigger(video_url):
    """
    Manually triggers the workflow for a given video URL.
    """
    try:
        # Extract video ID from the URL
        video_id = video_url.split("v=")[1]
        process_video_workflow(video_id)
    except Exception as e:
        logging.error(f"Error during manual trigger: {e}")

if __name__ == "__main__":
    # Run the Flask app for webhook handling
    app.run(host="0.0.0.0", port=5000)

    # Uncomment the following lines for manual triggering
    # video_url = input("Enter the YouTube video URL: ").strip()
    # manual_trigger(video_url)