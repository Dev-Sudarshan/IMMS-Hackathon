
import requests
import json
import streamlit as st
from config import DEPLOYMENT_URL, HEADERS

def generate_article_from_text(raw_data):
    """Generate news article from raw text data only"""
    prompt = f"""
Write a factual sports news article based on the raw match data provided below.

KEY INSTRUCTIONS:
- Only use information provided below - do not invent any details
- Structure: Headline, then 2-3 paragraphs
- Be concise but informative
- If information is unclear, say so rather than guessing
- Focus on the most important events mentioned in the data

RAW MATCH DATA:
{raw_data}

Write the article now:
"""
    
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500
    }
    
    try:
        response = requests.post(DEPLOYMENT_URL, headers=HEADERS, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"Error generating article: {str(e)}")
    
    return "[Error generating article]"

def generate_short_caption(frame_description):
    """Generate a short 1-2 line caption for the key frame"""
    prompt = f"""
Based on this detailed frame analysis, write a short 1-2 line caption that captures the main action happening in this football match moment.

Frame analysis: {frame_description}

Write a concise caption (maximum 2 lines) that describes the key action:
"""
    
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 50
    }
    
    try:
        response = requests.post(DEPLOYMENT_URL, headers=HEADERS, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        return "Key moment from the match"
    
    return "Key moment from the match"

def generate_article(transcript, all_descriptions, best_frame_data):
    """Generate news article from transcript and descriptions"""
    # Prepare descriptions text
    descriptions_text = "\n".join([
        f"Frame {i+1}: {desc['description']} (Importance: {desc['score']}/10)"
        for i, desc in enumerate(all_descriptions)
    ])
    
    prompt = f"""
Write a factual sports news article based on the transcript and image analysis below. 

KEY INSTRUCTIONS:
- Only use information provided below - do not invent any details
- Focus on the most important events (highest scored frames)
- Structure: Headline, then 2-3 paragraphs
- Be concise but informative
- If information is unclear, say so rather than guessing

AUDIO TRANSCRIPT:
{transcript}

IMAGE ANALYSIS:
{descriptions_text}

MOST IMPORTANT MOMENT:
{best_frame_data['description']} (Score: {best_frame_data['score']}/10)
Reason: {best_frame_data['reason']}

Write the article now:
"""
    
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500
    }
    
    try:
        response = requests.post(DEPLOYMENT_URL, headers=HEADERS, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"Error generating article: {str(e)}")
    
    return "[Error generating article]"

def edit_article_with_prompt(original_article, user_prompt):
    """Edit the generated article based on user's custom prompt"""
    prompt = f"""
You are a professional sports news editor. Edit the following article based on the user's specific request.

ORIGINAL ARTICLE:
{original_article}

USER'S EDITING REQUEST:
{user_prompt}

KEY INSTRUCTIONS:
- Follow the user's editing request precisely
- Maintain the factual accuracy of the original content
- Keep it professional and news-appropriate
- If the request asks for information not in the original article, politely mention that the information is not available
- Return only the edited article, no additional commentary

EDITED ARTICLE:
"""
    
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 600
    }
    
    try:
        response = requests.post(DEPLOYMENT_URL, headers=HEADERS, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"Error editing article: {str(e)}")
    
    return "[Error editing article]"