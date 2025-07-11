import os
import cv2
import shutil
import streamlit as st
from config import DEFAULT_FPS, DEFAULT_GROUP_SIZE

def extract_frame_groups(video_path, output_folder, fps=DEFAULT_FPS, group_size=DEFAULT_GROUP_SIZE):
    """Extract frames from video and group them"""
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)
    
    vidcap = cv2.VideoCapture(video_path)
    actual_fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(actual_fps / fps) if actual_fps > 0 else 30
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    count, saved = 0, 0
    group_index = 0
    current_group = []
    all_groups = []
    
    progress_bar = st.progress(0)
    
    success, image = vidcap.read()
    while success:
        if count % frame_interval == 0:
            frame_filename = os.path.join(output_folder, f"group{group_index}_frame{saved}.jpg")
            cv2.imwrite(frame_filename, image)
            current_group.append(frame_filename)
            saved += 1
            
            if saved == group_size:
                all_groups.append(current_group)
                current_group = []
                saved = 0
                group_index += 1
        
        success, image = vidcap.read()
        count += 1
        
        # Update progress
        progress = min(count / total_frames, 1.0)
        progress_bar.progress(progress)
    
    # Add remaining frames if any
    if current_group:
        all_groups.append(current_group)
    
    vidcap.release()
    progress_bar.empty()
    return all_groups