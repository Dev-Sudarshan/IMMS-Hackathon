import streamlit as st
import base64
import os
import time
from tempfile import NamedTemporaryFile
from gtts import gTTS

# Assuming these imports are correctly configured and available
# You might need to install these if you haven't:
# pip install streamlit gtts moviepy pydub
# pip install --upgrade google-cloud-speech  # For audio transcription if using Google Cloud
# pip install torch torchvision torchaudio  # If using local ML models for image analysis
# pip install transformers  # If using Hugging Face models for image analysis/captioning

from config import FRAMES_FOLDER, TEMP_AUDIO_FILE
from utils import image_to_base64, cleanup_files, cleanup_folder
from video_processor import extract_frame_groups
from audio_processor import transcribe_audio
from image_analyzer import find_best_frames_per_group, find_global_best_frame
from article_generator import generate_article, generate_article_from_text, generate_short_caption, edit_article_with_prompt

# Default settings for spoken and article language
DEFAULT_SPOKEN_LANGUAGE_CODE = "en"
DEFAULT_ARTICLE_LANGUAGE = "English"

def initialize_session_state():
    """Initialize session state variables"""
    if 'generated_article' not in st.session_state:
        st.session_state.generated_article = None
    if 'article_image_base64' not in st.session_state:
        st.session_state.article_image_base64 = None
    if 'article_caption' not in st.session_state:
        st.session_state.article_caption = None
    # Initialize article_language in session state
    if 'article_language' not in st.session_state:
        st.session_state.article_language = DEFAULT_ARTICLE_LANGUAGE
    # Store the original article to enable the "Reset to Original" functionality
    if 'original_article' not in st.session_state:
        st.session_state.original_article = None

def setup_page_config():
    """Setup Streamlit page configuration"""
    st.set_page_config(page_title="Sports Video to News Generator")
    st.title("🏆 Sports Video ➤ News Article Generator")
    st.markdown("Upload a sports video or provide raw match data to generate a professional news article.")

def create_input_tabs():
    """Create input tabs for video upload and raw data input"""
    tab1, tab2 = st.tabs(["📹 Video Upload", "📝 Raw Data Input"])

    video_file = None
    raw_match_data = None
    generate_from_text_button_pressed = False # Renamed to avoid conflict with function arg
    uploaded_data_file = None
    spoken_language_code_selection = None # Renamed to avoid conflict with function arg

    with tab1:
        st.markdown("Upload a sports video, and this tool will analyze frames and audio to generate a professional news article.")
        video_file = st.file_uploader("📤 Upload Sports Video", type=["mp4", "mkv", "mov", "avi"])

        spoken_language_code_selection = st.selectbox(
            "🎙️ Spoken language in the video:",
            [
                ("Auto-detect", None),
                ("English", "en"),
                ("Nepali", "ne"),
                ("Spanish", "es"),
                ("Hindi", "hi"),
                ("French", "fr"),
                ("French (Canada)", "fr")
            ],
            format_func=lambda x: x[0],
            key="spoken_lang_select_tab1" # Unique key for this selectbox
        )[1]

        # Update session state directly when this selectbox changes
        st.session_state.article_language = st.selectbox(
            "📰 Generate article in:",
            ["English", "Nepali", "Spanish", "Hindi", "French", "French (Canada)"],
            key="article_lang_select_tab1", # Unique key for this selectbox
            index=["English", "Nepali", "Spanish", "Hindi", "French", "French (Canada)"].index(st.session_state.article_language)
        )

    with tab2:
        st.markdown("Enter raw match data manually, or upload structured JSON/timestamp files.")

        raw_match_data = st.text_area(
            "📝 Enter Match Data (optional if uploading a file)",
            placeholder="Enter match commentary, statistics, or structured notes...",
            height=200
        )

        uploaded_data_file = st.file_uploader(
            "📁 Or upload match data file (JSON, TXT, CSV)",
            type=["json", "txt", "csv"]
        )

        # Update session state directly when this selectbox changes
        st.session_state.article_language = st.selectbox(
            "📰 Generate article in:",
            ["English", "Nepali", "Spanish", "Hindi", "French", "French (Canada)"],
            key="article_lang_select_tab2", # Unique key for this selectbox
            index=["English", "Nepali", "Spanish", "Hindi", "French", "French (Canada)"].index(st.session_state.article_language)
        )

        generate_from_text_button_pressed = st.button("📝 Generate Article from Text Data")

    return (
        video_file,
        raw_match_data,
        generate_from_text_button_pressed,
        uploaded_data_file,
        spoken_language_code_selection
    )

# 🌐 Map UI language to gTTS language code
def get_gtts_lang_code(article_language):
    language_map = {
        "English": "en",
        "Nepali": "ne",
        "Hindi": "hi",
        "Spanish": "es",
        "French": "fr",
        "French (Canada)": "fr", # gTTS treats French (Canada) as "fr"
    }
    return language_map.get(article_language, "en")  # fallback to English

# 🔊 Text-to-Speech Function
def speak_article(article_text, lang='en'):
    try:
        tts = gTTS(text=article_text, lang=lang)
        audio_path = "article_audio.mp3"
        tts.save(audio_path)
        return audio_path
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")
        st.warning("Please ensure the selected article language is supported by the text-to-speech engine.")
        return None

def display_article_with_editor():
    """Display generated article with editing functionality and audio generation"""
    if st.session_state.generated_article:
        st.subheader("📰 Generated News Article")

        if st.session_state.article_image_base64:
            try:
                image_data = base64.b64decode(st.session_state.article_image_base64)
                st.image(image_data, use_container_width=True)
                if st.session_state.article_caption:
                    st.caption(st.session_state.article_caption)
            except Exception as e:
                st.error(f"Error displaying image: {str(e)}")

        st.write(st.session_state.generated_article)

        st.markdown("---")
        st.subheader("✏️ Edit Article")
        st.markdown("Want to modify the article? Enter your editing instructions below:")

        col1, col2 = st.columns([3, 1])

        with col1:
            edit_prompt = st.text_area(
                "Enter your editing instructions:",
                placeholder="Examples:\n• Make it more formal\n• Add more details about the players\n• Make it shorter\n• Change the tone to be more exciting\n• Focus more on the team statistics\n• Rewrite the headline",
                height=100,
                key="edit_prompt"
            )

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            edit_button = st.button("🔄 Edit Article", type="primary")

            if st.button("↩️ Reset to Original"):
                if st.session_state.original_article: # Check if original article exists
                    st.session_state.generated_article = st.session_state.original_article
                    st.success("Article reset to original version.")
                    st.rerun()
                else:
                    st.warning("No original article to reset to. Please generate an article first.")

        if edit_button and edit_prompt.strip():
            with st.spinner("✏️ Editing article..."):
                try:
                    edited_article = edit_article_with_prompt(st.session_state.generated_article, edit_prompt)
                    st.session_state.generated_article = edited_article
                    st.success("Article updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error editing article: {str(e)}")

        elif edit_button and not edit_prompt.strip():
            st.warning("Please enter your editing instructions.")

        st.markdown("**Quick Edit Options:**")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("📏 Make Shorter"):
                with st.spinner("Making article shorter..."):
                    try:
                        edited_article = edit_article_with_prompt(st.session_state.generated_article, "Make this article shorter and more concise while keeping the key information.")
                        st.session_state.generated_article = edited_article
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error making article shorter: {str(e)}")

        with col2:
            if st.button("🎯 More Formal"):
                with st.spinner("Making article more formal..."):
                    try:
                        edited_article = edit_article_with_prompt(st.session_state.generated_article, "Make this article more formal and professional in tone.")
                        st.session_state.generated_article = edited_article
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error making article more formal: {str(e)}")

        with col3:
            if st.button("⚡ More Exciting"):
                with st.spinner("Making article more exciting..."):
                    try:
                        edited_article = edit_article_with_prompt(st.session_state.generated_article, "Make this article more exciting and engaging while keeping it factual.")
                        st.session_state.generated_article = edited_article
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error making article more exciting: {str(e)}")

        with col4:
            if st.button("📊 Add Stats Focus"):
                with st.spinner("Adding statistics focus..."):
                    try:
                        edited_article = edit_article_with_prompt(st.session_state.generated_article, "Focus more on statistics and numerical data if available in the original content.")
                        st.session_state.generated_article = edited_article
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding stats focus: {str(e)}")

        st.markdown("---")
        st.subheader("🔊 Text-to-Speech")

        lang_code = get_gtts_lang_code(st.session_state.article_language)

        if st.button("🎵 Generate Audio"):
            with st.spinner("Generating audio..."):
                audio_path = speak_article(st.session_state.generated_article, lang=lang_code)

                if audio_path and os.path.exists(audio_path):
                    with open(audio_path, "rb") as audio_file:
                        audio_bytes = audio_file.read()

                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.audio(audio_bytes, format="audio/mp3")
                    with col2:
                        st.download_button("⬇ Download Audio", audio_bytes, file_name="article_audio.mp3", mime="audio/mp3")

                    time.sleep(1)
                    try:
                        os.remove(audio_path)
                    except PermissionError:
                        st.warning("⚠ Could not delete audio file immediately. It may still be in use.")
                else:
                    st.error("Failed to generate audio.")

def process_video_upload(video_file, spoken_language_code):
    with NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(video_file.read())
        video_path = temp_video.name

    try:
        st.info("🎞️ Extracting frames...")
        frame_groups = extract_frame_groups(video_path, FRAMES_FOLDER, fps=1, group_size=5)

        if not frame_groups:
            st.error("No frames could be extracted from the video.")
            return

        st.info("🔍 Analyzing frames...")
        best_frames, all_frame_data = find_best_frames_per_group(frame_groups)

        if not best_frames:
            st.error("Could not analyze any frames.")
            return

        global_best_frame = find_global_best_frame(best_frames)

        st.info("🎧 Transcribing audio...")
        transcript = transcribe_audio(video_path, TEMP_AUDIO_FILE, spoken_language_code)

        article = generate_article(transcript, all_frame_data, global_best_frame, st.session_state.article_language)

        st.session_state.generated_article = article
        st.session_state.original_article = article # Store the original for reset

        if global_best_frame:
            image_base64 = image_to_base64(global_best_frame['image_path'])
            st.session_state.article_image_base64 = image_base64
            st.session_state.article_caption = generate_short_caption(global_best_frame['description'], st.session_state.article_language)

        cleanup_files(TEMP_AUDIO_FILE)
        st.success("🎉 Article generated successfully!")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

    finally:
        cleanup_files(video_path)
        cleanup_folder(FRAMES_FOLDER)

def process_text_input(raw_match_data):
    if not raw_match_data.strip():
        st.warning("Please enter some match data in the text area.")
        return

    st.info("📝 Generating article...")

    try:
        article = generate_article_from_text(raw_match_data, st.session_state.article_language)
        st.session_state.generated_article = article
        st.session_state.original_article = article # Store the original for reset
        st.session_state.article_image_base64 = None
        st.session_state.article_caption = None
        st.success("🎉 Article generated successfully!")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

def process_uploaded_file(uploaded_data_file):
    """Process uploaded data file"""
    if not uploaded_data_file:
        return

    try:
        if uploaded_data_file.type == "application/json":
            import json
            file_content = json.load(uploaded_data_file)
            raw_match_data = json.dumps(file_content, indent=2)
        elif uploaded_data_file.type == "text/csv":
            import pandas as pd
            df = pd.read_csv(uploaded_data_file)
            raw_match_data = df.to_string()
        else:
            raw_match_data = uploaded_data_file.read().decode('utf-8')

        process_text_input(raw_match_data)

    except Exception as e:
        st.error(f"Error processing uploaded file: {str(e)}")

def main():
    initialize_session_state()
    setup_page_config()

    (video_file, raw_match_data, generate_from_text_button_pressed,
     uploaded_data_file, spoken_language_code_selection) = create_input_tabs()

    spoken_language_code = spoken_language_code_selection or DEFAULT_SPOKEN_LANGUAGE_CODE

    if video_file:
        if st.button("🧠 Generate Article from Video", key="generate_video_article_btn"):
            process_video_upload(video_file, spoken_language_code)

    if generate_from_text_button_pressed:
        if raw_match_data.strip():
            process_text_input(raw_match_data)
        elif uploaded_data_file:
            process_uploaded_file(uploaded_data_file)
        else:
            st.warning("Please enter match data or upload a file.")

    display_article_with_editor()

if __name__ == "__main__":
    main()