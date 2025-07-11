import base64
import requests
import json
import streamlit as st
from config import DEPLOYMENT_URL, HEADERS

def describe_image_with_scoring(image_path, timestamp):
    """Describe image and provide importance score"""
    with open(image_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode("utf-8")
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Analyze this football match frame and provide:\n"
                            "1. A detailed description of what's happening\n"
                            "2. An importance score (1-10) based on these criteria:\n"
                            "   CRITICAL: WE WANT THE MOMENT OF ACTION, NOT THE RESULT:\n"
                            "   - 10: Player's foot making contact with ball for a shot, player striking the ball\n"
                            "   - 9: Player in shooting motion, about to kick the ball\n"
                            "   - 8: Player preparing to shoot, ball approaching player's foot\n"
                            "   - 7: Corner kick being taken, free kick setup\n"
                            "   - 6: Regular play, passing, running\n"
                            "   - 2-3: Ball already in net, goal celebration, players celebrating\n"
                            "   - 1: Players standing, crowd shots, referee walking\n\n"
                            "ABSOLUTELY CRITICAL: If you see the ball already in the goal net or players celebrating a goal, give it a LOW score (2-3). We want the SHOOTING ACTION, not the goal result.\n\n"
                            "Format your response as:\n"
                            "DESCRIPTION: [your description]\n"
                            "SCORE: [number 1-10]\n"
                            "REASON: [why this score]"
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                    }
                ]
            }
        ],
        "max_tokens": 400
    }
    
    try:
        response = requests.post(DEPLOYMENT_URL, headers=HEADERS, data=json.dumps(payload))
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content'].strip()
            
            # Parse the response
            lines = content.split('\n')
            description = ""
            score = 1
            reason = ""
            
            for line in lines:
                if line.startswith("DESCRIPTION:"):
                    description = line.replace("DESCRIPTION:", "").strip()
                elif line.startswith("SCORE:"):
                    try:
                        score = int(line.replace("SCORE:", "").strip())
                    except:
                        score = 1
                elif line.startswith("REASON:"):
                    reason = line.replace("REASON:", "").strip()
            
            return {
                "description": description or content,
                "score": max(1, min(10, score)),  # Ensure score is between 1-10
                "reason": reason,
                "timestamp": timestamp,
                "image_path": image_path
            }
    except Exception as e:
        st.error(f"Error analyzing image: {str(e)}")
    
    return {
        "description": "[Error analyzing image]",
        "score": 1,
        "reason": "API Error",
        "timestamp": timestamp,
        "image_path": image_path
    }

def find_best_frames_per_group(frame_groups):
    """Find the best frame from each group"""
    best_frames = []
    all_frame_data = []
    
    progress_bar = st.progress(0)
    total_groups = len(frame_groups)
    
    for group_idx, group in enumerate(frame_groups):
        group_data = []
        
        # Analyze each frame in the group
        for frame_idx, frame_path in enumerate(group):
            timestamp = group_idx * 5 + frame_idx  # Approximate timestamp
            frame_data = describe_image_with_scoring(frame_path, timestamp)
            group_data.append(frame_data)
            all_frame_data.append(frame_data)
        
        # Find best frame in this group
        best_frame_in_group = max(group_data, key=lambda x: x['score'])
        best_frames.append(best_frame_in_group)
        
        # Update progress
        progress = (group_idx + 1) / total_groups
        progress_bar.progress(progress)
    
    progress_bar.empty()
    return best_frames, all_frame_data

def find_global_best_frame(best_frames):
    """Find the overall best frame from all group winners"""
    if not best_frames:
        return None
    
    # Sort by score (descending) and return the best one
    global_best = max(best_frames, key=lambda x: x['score'])
    return global_best