import streamlit as st
import base64
from article_generator import edit_article_with_prompt

def initialize_session_state():
    """Initialize session state variables"""
    if 'generated_article' not in st.session_state:
        st.session_state.generated_article = None
    if 'article_image_base64' not in st.session_state:
        st.session_state.article_image_base64 = None
    if 'article_caption' not in st.session_state:
        st.session_state.article_caption = None


def setup_page_config():
    """Setup Streamlit page configuration"""
    st.set_page_config(page_title="🏆 Sports Video to News Generator", layout="wide")
    st.markdown("""
        <div style='margin-bottom: 2rem;'>
            <h1 style='font-size: 3rem; color: #0B5ED7; margin-bottom: 0.3rem;'>
                🏆 Sports Video ➤ News Article Generator
            </h1>
            <p style='font-size: 1.1rem; color: #555;'>
                Transform your sports footage or match details into a professional news article — instantly and effortlessly.
            </p>
            <hr style="margin-top: 1.5rem;">
        </div>
    """, unsafe_allow_html=True)


def create_input_tabs():
    """Create input tabs for video upload and raw data input"""
    tab1, tab2 = st.tabs(["📹 Video Upload", "📝 Raw Data Input"])

    with tab1:
        st.markdown("Upload a sports video, and this tool will analyze frames and audio to generate a professional news article.")
        video_file = st.file_uploader("📤 Upload Sports Video", type=["mp4", "mkv", "mov", "avi"])

        spoken_language_code = st.selectbox(
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
            format_func=lambda x: x[0]
        )[1]

        article_language = st.selectbox(
            "📰 Generate article in:",
            ["English", "Nepali", "Spanish", "Hindi", "French", "French (Canada)"]
        )

        generate_article_button = st.button("▶️ Generate Article from Video")

    with tab2:
        st.markdown("Enter raw match data manually, or upload structured JSON/timestamp files.")

        # Text input
        raw_match_data = st.text_area(
            "📝 Enter Match Data (optional if uploading a file)",
            placeholder="Enter match commentary, statistics, or structured notes...",
            height=200
        )

        # File upload input
        uploaded_data_file = st.file_uploader(
            "📁 Or upload match data file (JSON, TXT, CSV)",
            type=["json", "txt", "csv"]
        )

        generate_from_text = st.button("Generate Article from Text Data")

    return (
        video_file,
        raw_match_data,
        generate_from_text,
        uploaded_data_file,
        spoken_language_code,
        article_language
    )


def display_article_with_editor():
    """Display generated article with editing functionality"""
    if not st.session_state.generated_article:
        return

    st.subheader("📰 Generated News Article")

    if st.session_state.article_image_base64:
        try:
            image_data = base64.b64decode(st.session_state.article_image_base64)
            st.image(image_data, use_container_width=True)
            if st.session_state.article_caption:
                st.caption(st.session_state.article_caption)
        except Exception as e:
            st.error(f"Error displaying image: {str(e)}")

    st.markdown("<div style='font-size: 1.1rem;'>", unsafe_allow_html=True)
    st.write(st.session_state.generated_article)
    st.markdown("</div>", unsafe_allow_html=True)

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
            st.rerun()

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

    display_quick_edit_buttons()


def display_quick_edit_buttons():
    """Display quick edit buttons for common requests"""
    st.markdown("**Quick Edit Options:**")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📏 Make Shorter"):
            with st.spinner("Making article shorter..."):
                edited_article = edit_article_with_prompt(
                    st.session_state.generated_article,
                    "Make this article shorter and more concise while keeping the key information."
                )
                st.session_state.generated_article = edited_article
                st.rerun()

    with col2:
        if st.button("🎯 More Formal"):
            with st.spinner("Making article more formal..."):
                edited_article = edit_article_with_prompt(
                    st.session_state.generated_article,
                    "Make this article more formal and professional in tone."
                )
                st.session_state.generated_article = edited_article
                st.rerun()

    with col3:
        if st.button("⚡ More Exciting"):
            with st.spinner("Making article more exciting..."):
                edited_article = edit_article_with_prompt(
                    st.session_state.generated_article,
                    "Make this article more exciting and engaging while keeping it factual."
                )
                st.session_state.generated_article = edited_article
                st.rerun()

    with col4:
        if st.button("📊 Add Stats Focus"):
            with st.spinner("Adding statistics focus..."):
                edited_article = edit_article_with_prompt(
                    st.session_state.generated_article,
                    "Focus more on statistics and numerical data if available in the original content."
                )
                st.session_state.generated_article = edited_article
                st.rerun()
