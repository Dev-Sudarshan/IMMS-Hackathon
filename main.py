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

def process_video_upload(video_file, spoken_language_code, article_language):
    with NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(video_file.read())
        video_path = temp_video.name

    try:
        st.info("🎞️ Extracting frames...")
        frame_groups = extract_frame_groups(video_path, FRAMES_FOLDER, fps=1, group_size=5)

        if not frame_groups:
            st.error("No frames could be extracted from the video")
            return

        st.info("🔍 Analyzing frames...")
        best_frames, all_frame_data = find_best_frames_per_group(frame_groups)

        if not best_frames:
            st.error("Could not analyze any frames")
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


def main():
    initialize_session_state()
    setup_page_config()

    # Note: this matches the create_input_tabs() from the last ui_components.py I gave you
    (
        video_file,
        spoken_language_code,
        article_language,
        generate_article_button,
        raw_match_data,
        generate_from_text,
    ) = create_input_tabs()

    # Only process video if user clicks generate button
    if video_file is not None and generate_article_button:
        process_video_upload(video_file, spoken_language_code, article_language)

    if generate_from_text:
        process_text_input(raw_match_data, article_language)

    display_article_with_editor()


if __name__ == "__main__":
    main()
