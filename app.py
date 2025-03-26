import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

# Load environment variables
load_dotenv()

# Configure Google Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("❌ Missing Google API Key! Check your .env file.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# Set model name
MODEL_NAME = "gemini-1.5-pro"  # Change this if the model is unavailable

# Summarization Prompt
prompt = """You are a YouTube video summarizer. 
You will take the transcript text and summarize the entire video, 
providing the important points in bullet format within 250 words.
Please provide the summary of the text given here: """

# Function to check available Gemini models
def list_available_models():
    try:
        models = genai.list_models()
        return [model.name for model in models]
    except Exception as e:
        return []

# Function to extract video ID from YouTube URL
def get_video_id(youtube_url):
    parsed_url = urlparse(youtube_url)
    if parsed_url.netloc in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed_url.query).get("v", [None])[0]
    elif parsed_url.netloc in ["youtu.be"]:
        return parsed_url.path.lstrip("/")
    return None

# Function to extract transcript
def extract_transcript_details(youtube_video_url):
    try:
        video_id = get_video_id(youtube_video_url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join(i["text"] for i in transcript_text)

        return transcript
    except Exception as e:
        return None  # Return None instead of raising an error

# Function to generate summary using Gemini
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt + transcript_text)

        # Check response format
        if hasattr(response, "text"):
            return response.text
        elif hasattr(response, "candidates") and response.candidates:
            return response.candidates[0].content
        else:
            return "❌ Failed to generate summary."

    except Exception as e:
        return f"❌ Error: {str(e)}"

# Streamlit UI
st.title("🎥 YouTube Transcript to Notes Converter")

# User input for YouTube link
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = get_video_id(youtube_link)
    if video_id:
        st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    else:
        st.error("❌ Invalid YouTube URL. Please enter a correct URL.")

# Button to get transcript and generate summary
if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        st.markdown("## 📌 Detailed Notes:")
        st.write(summary)
    else:
        st.error("⚠️ Could not extract transcript. This video may not have subtitles available.")


