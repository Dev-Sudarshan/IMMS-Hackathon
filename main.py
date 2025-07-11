import streamlit as st
import os
from tempfile import NamedTemporaryFile

# Import custom modules
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
    display_article_with_editor
)

def process_video_upload(video_file):
    """Process uploaded video file"""
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
        transcript = transcribe_audio(video_path, TEMP_AUDIO_FILE)
        
        article = generate_article(transcript, all_frame_data, global_best_frame)
        
        # Store in session state with base64 image
        st.session_state.generated_article = article
        if global_best_frame:
            # Convert image to base64 for persistent storage
            image_base64 = image_to_base64(global_best_frame['image_path'])
            st.session_state.article_image_base64 = image_base64
            st.session_state.article_caption = generate_short_caption(global_best_frame['description'])
        
        # Cleanup audio file
        cleanup_files(TEMP_AUDIO_FILE)
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    
    finally:
        # Cleanup
        cleanup_files(video_path)
        cleanup_folder(FRAMES_FOLDER)

def process_text_input(raw_match_data):
    """Process raw text input"""
    if not raw_match_data.strip():
        st.warning("Please enter some match data in the text area.")
        return
    
    st.info("📝 Generating article...")
    
    try:
        article = generate_article_from_text(raw_match_data)
        
        # Store in session state
        st.session_state.generated_article = article
        st.session_state.article_image_base64 = None
        st.session_state.article_caption = None
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

def main():
    """Main application function"""
    # Initialize session state and setup page
    initialize_session_state()
    setup_page_config()
    
    # Create input tabs
    video_file, raw_match_data, generate_from_text = create_input_tabs()
    
    # Handle video upload
    if video_file is not None:
        process_video_upload(video_file)
    
    # Handle raw text input
    if generate_from_text:
        process_text_input(raw_match_data)
    
    # Display generated article and editor
    display_article_with_editor()

if __name__ == "__main__":
    main()