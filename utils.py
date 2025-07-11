import base64
import os
import streamlit as st

def image_to_base64(image_path):
    """Convert image to base64 string for storage"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Error converting image to base64: {str(e)}")
        return None

def cleanup_files(*file_paths):
    """Clean up temporary files"""
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)

def cleanup_folder(folder_path):
    """Clean up temporary folder"""
    if os.path.exists(folder_path):
        import shutil
        shutil.rmtree(folder_path)