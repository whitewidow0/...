# sumarization.py
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
from prompts import DEFAULT_PROMPTS

# Debug statement
print("sumarization.py is being executed")  # Debug statement

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()

# Initialize DeepSeek client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.deepseek.com")

def select_prompt(content):
    """
    Analyzes the content and selects the appropriate prompt.
    """
    if any(keyword in content.lower() for keyword in ["trading strategy", "indicator"]):
        return DEFAULT_PROMPTS.get("TRADING_PROMPT")
    return DEFAULT_PROMPTS.get("DEFAULT_PROMPT")

def send_prompt_and_get_summary(client, prompt, content):
    """
    Send the content to DeepSeek for summarization and return the summary.
    """
    try:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": content},
        ]
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error summarizing content: {e}")
        return None

def save_summary(summary, base_name, prompt_name):
    """
    Save the summary to a file.
    """
    output_dir = os.path.join("output", prompt_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, f"{base_name}_Summary.txt")
    with open(output_file, 'w') as file:
        file.write(summary)

    logging.info(f"Summary saved to {output_file}")

def summarize_transcription(transcription_file):
    """
    Summarizes the transcription using DeepSeek.
    """
    try:
        # Read the transcription file
        with open(transcription_file, 'r') as file:
            content = file.read()

        # Select the appropriate prompt
        prompt = select_prompt(content)

        # Send the content to DeepSeek and get the summary
        summary = send_prompt_and_get_summary(client, prompt, content)

        # Save the summary
        if summary:
            base_name = os.path.splitext(os.path.basename(transcription_file))[0]
            save_summary(summary, base_name, prompt_name=prompt)
        else:
            logging.error("Failed to generate summary.")
    except Exception as e:
        logging.error(f"Error summarizing transcription: {e}")