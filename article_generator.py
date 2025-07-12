import requests
import json
import streamlit as st
from config import DEPLOYMENT_URL, HEADERS

def generate_article_from_text(raw_data, output_language="English"):
    """Generate news article from raw text data only, in specified language"""
    prompt = f"""
You are a multilingual sports journalist.

👉 Your task is to write a professional sports news article in **{output_language}** based ONLY on the raw match data below.

📜 STRUCTURE:
- Headline
- 2–3 concise but informative paragraphs

📝 RULES:
- Use only the information provided
- Do not invent any details
- Be clear and factual
- If something is unclear or missing, dont guess, just state that

RAW MATCH DATA:
{raw_data}

Now write the full article in **{output_language}**:
"""

    payload = {
        "messages": [
            {"role": "system", "content": f"You are a professional journalist who always writes in {output_language}."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500
    }

    try:
        response = requests.post(DEPLOYMENT_URL, headers=HEADERS, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            st.error(f"API Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Error generating article: {str(e)}")

    return "[Error generating article]"


def generate_short_caption(frame_description, output_language="English"):
    """Generate a short 1-2 line caption for the key frame, in specified language"""
    prompt = f"""
You are a multilingual sports journalist.

Write a short 1–2 line caption in **{output_language}** that describes the key moment shown below in a football match.

FRAME DESCRIPTION:
{frame_description}

The caption should be concise, descriptive, and match the tone of a professional news site.
"""

    payload = {
        "messages": [
            {"role": "system", "content": f"You write captions for international sports media in {output_language}."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 70
    }

    try:
        response = requests.post(DEPLOYMENT_URL, headers=HEADERS, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.warning(f"Error generating caption: {str(e)}")

    return "Key moment from the match"


def generate_article(transcript, all_descriptions, best_frame_data, output_language="English"):
    """Generate news article from transcript and descriptions, in specified language"""
    descriptions_text = "\n".join([
        f"Frame {i+1}: {desc['description']} (Importance: {desc['score']}/10)"
        for i, desc in enumerate(all_descriptions)
    ])

    prompt = f"""
You are a multilingual sports journalist.

👉 Your task is to write a professional sports news article in **{output_language}**.

Below are the inputs. DO NOT use any information not included below. Translate factual content if needed, but always write the article entirely in **{output_language}**.

📜 STRUCTURE:
- Headline
- 2–3 concise but informative paragraphs

📝 RULES:
- Keep it factual
- Focus on the most important moments (especially high-scoring frames)
- If anything is unclear, mention that instead of guessing
- Keep the tone formal and appropriate for a sports news website

🎧 AUDIO TRANSCRIPT:
{transcript}

🖼️ IMAGE ANALYSIS:
{descriptions_text}

🌟 MOST IMPORTANT MOMENT:
{best_frame_data['description']} (Score: {best_frame_data['score']}/10)
Reason: {best_frame_data['reason']}

Now, write the article in **{output_language}**:
"""

    payload = {
        "messages": [
            {"role": "system", "content": f"You are a professional journalist who always writes in {output_language}."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500
    }

    try:
        response = requests.post(DEPLOYMENT_URL, headers=HEADERS, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            st.error(f"API Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Error generating article: {str(e)}")

    return "[Error generating article]"


def edit_article_with_prompt(original_article, user_prompt, output_language="English"):
    """Edit the generated article based on user's custom prompt, in specified language"""
    prompt = f"""
You are a multilingual sports news editor.

🛠️ Edit the following article based on the user's specific request — but keep it in **{output_language}**.

ORIGINAL ARTICLE:
{original_article}

USER'S REQUEST:
{user_prompt}

RULES:
- Follow the editing request precisely
- Keep the article factual and professional
- If something is not available in the original article, state that politely
- Return only the edited article (no extra explanations)

Now, return the fully edited article in **{output_language}**:
"""

    payload = {
        "messages": [
            {"role": "system", "content": f"You are a professional news editor fluent in {output_language}."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500
    }

    try:
        response = requests.post(DEPLOYMENT_URL, headers=HEADERS, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            st.error(f"API Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Error editing article: {str(e)}")

    return "[Error editing article]"
