import streamlit as st
from tempfile import NamedTemporaryFile

from config import FRAMES_FOLDER, TEMP_AUDIO_FILE
from utils import image_to_base64, cleanup_files, cleanup_folder
from video_processor import extract_frame_groups
from audio_processor import transcribe_audio
from image_analyzer import find_best_frames_per_group, find_global_best_frame
from article_generator import generate_article, generate_article_from_text, generate_short_caption
from ui_components import (
    initialize_session_state,
    setup_page_config,
    create_input_tabs,
    display_article_with_editor,
)

# Default settings for spoken and article language
DEFAULT_SPOKEN_LANGUAGE_CODE = "en"
DEFAULT_ARTICLE_LANGUAGE = "English"

def process_video_upload(video_file, spoken_language_code, article_language):
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

        article = generate_article(transcript, all_frame_data, global_best_frame, article_language)

        st.session_state.generated_article = article
        if global_best_frame:
            image_base64 = image_to_base64(global_best_frame['image_path'])
            st.session_state.article_image_base64 = image_base64
            st.session_state.article_caption = generate_short_caption(global_best_frame['description'], article_language)

        cleanup_files(TEMP_AUDIO_FILE)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

    finally:
        cleanup_files(video_path)
        cleanup_folder(FRAMES_FOLDER)

def process_text_input(raw_match_data, article_language):
    if not raw_match_data.strip():
        st.warning("Please enter some match data in the text area.")
        return

    st.info("📝 Generating article...")

    try:
        article = generate_article_from_text(raw_match_data, article_language)
        st.session_state.generated_article = article
        st.session_state.article_image_base64 = None
        st.session_state.article_caption = None

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

def process_uploaded_file(uploaded_data_file, article_language):
    """Process uploaded data file"""
    if not uploaded_data_file:
        return
        
    try:
        # Read file content based on type
        if uploaded_data_file.type == "application/json":
            import json
            file_content = json.load(uploaded_data_file)
            # Convert JSON to string for processing
            raw_match_data = json.dumps(file_content, indent=2)
        elif uploaded_data_file.type == "text/csv":
            import pandas as pd
            df = pd.read_csv(uploaded_data_file)
            raw_match_data = df.to_string()
        else:  # txt file
            raw_match_data = uploaded_data_file.read().decode('utf-8')
        
        process_text_input(raw_match_data, article_language)
        
    except Exception as e:
        st.error(f"Error processing uploaded file: {str(e)}")

def main():
    initialize_session_state()
    setup_page_config()

    # Get inputs from user - match the correct return order from create_input_tabs()
    (video_file, raw_match_data, generate_from_text, 
     uploaded_data_file, spoken_language_code, article_language) = create_input_tabs()

    # Use user selections or fall back to defaults
    spoken_language_code = spoken_language_code or DEFAULT_SPOKEN_LANGUAGE_CODE
    article_language = article_language or DEFAULT_ARTICLE_LANGUAGE

    # Process video upload
    if video_file:
        if st.button("🧠 Generate Article from Video"):
            process_video_upload(video_file, spoken_language_code, article_language)

    # Process text input
    if generate_from_text:
        if raw_match_data.strip():
            process_text_input(raw_match_data, article_language)
        elif uploaded_data_file:
            process_uploaded_file(uploaded_data_file, article_language)
        else:
            st.warning("Please enter match data or upload a file.")

    # Display the article editor
    display_article_with_editor()

if __name__ == "__main__":
    main()