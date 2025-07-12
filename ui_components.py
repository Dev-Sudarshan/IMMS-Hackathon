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
    st.set_page_config(page_title="Sports Video to News Generator")
    st.title("🏆 Sports Video ➤ News Article Generator")
    st.markdown("Upload a sports video or provide raw match data to generate a professional news article.")


import streamlit as st

def create_input_tabs():
    """Create input tabs for video upload and raw data input"""
    tab1, tab2 = st.tabs(["📹 Video Upload", "📝 Raw Data Input"])

    with tab1:
        st.markdown("Upload a sports video, and this tool will analyze frames and audio to generate a professional news article.")
        
        video_file = st.file_uploader("📤 Upload Sports Video", type=["mp4", "mkv", "mov", "avi"])

        # Spoken language selector (for Whisper)
        spoken_language_code = st.selectbox(
            "🎙️ Spoken language in the video:",
            [
                ("Auto-detect", None),
                ("English", "en"),
                ("Nepali", "ne"),
                ("Spanish", "es"),
                ("Hindi", "hi"),
                ("French", "fr"),
                ("French (Canada)", "fr")  # same code, prompt handles dialect
            ],
            format_func=lambda x: x[0]
        )[1]

        # Output language selector (for article generation)
        article_language = st.selectbox(
            "📰 Generate article in:",
            ["English", "Nepali", "Spanish", "Hindi", "French", "French (Canada)"]
        )

    with tab2:
        st.markdown("Enter raw match data, commentary, or any text information about the match to generate a news article.")
        raw_match_data = st.text_area(
            "📝 Enter Match Data",
            placeholder="Enter match commentary, statistics, player information, or any relevant match details...",
            height=200
        )
        generate_from_text = st.button("Generate Article from Text Data")

    return video_file, raw_match_data, generate_from_text, spoken_language_code, article_language



def display_article_with_editor():
    """Display generated article with editing functionality"""
    if not st.session_state.generated_article:
        return

    st.subheader("📰 Generated News Article")

    # Display image if available
    if st.session_state.article_image_base64:
        try:
            image_data = base64.b64decode(st.session_state.article_image_base64)
            st.image(image_data, use_container_width=True)
            if st.session_state.article_caption:
                st.caption(st.session_state.article_caption)
        except Exception as e:
            st.error(f"Error displaying image: {str(e)}")

    # Display the article
    st.write(st.session_state.generated_article)

    # Article Editor Section
    st.markdown("---")
    st.subheader("✏️ Edit Article")
    st.markdown("Want to modify the article? Enter your editing instructions below:")

    # Create columns for better layout
    col1, col2 = st.columns([3, 1])

    with col1:
        edit_prompt = st.text_area(
            "Enter your editing instructions:",
            placeholder="Examples:\n• Make it more formal\n• Add more details about the players\n• Make it shorter\n• Change the tone to be more exciting\n• Focus more on the team statistics\n• Rewrite the headline",
            height=100,
            key="edit_prompt"
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
        edit_button = st.button("🔄 Edit Article", type="primary")

        # Reset button to restore original
        if st.button("↩️ Reset to Original"):
            st.rerun()

    # Handle article editing
    if edit_button and edit_prompt.strip():
        with st.spinner("✏️ Editing article..."):
            try:
                edited_article = edit_article_with_prompt(st.session_state.generated_article, edit_prompt)

                # Update session state with edited article
                st.session_state.generated_article = edited_article

                # Show success message and rerun to display updated article
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


def main():
    """Main application function"""
    initialize_session_state()
    setup_page_config()
    
    # Create input interface
    video_file, raw_match_data, generate_from_text = create_input_tabs()
    
    # Display article editor if article exists
    display_article_with_editor()


if __name__ == "__main__":
    main()