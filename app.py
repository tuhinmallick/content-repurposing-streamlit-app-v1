import streamlit as st
import os
import dotenv
from repurpose_core.repurpose import repurpose_audio
import zipfile
import io
import streamlit.components.v1 as components


dotenv.load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


def display_text_with_copy_button(file_path, title):
    file_content = make_downloadable_file(file_path)
    st.subheader(title)
    st.code(file_content, language="text")

    copy_button_key = f"copy-button-{title.replace(' ', '-').lower()}"

    if copy_button := st.button("Copy to Clipboard", key=copy_button_key):
        components.html(
            f"""
            <script>
            navigator.clipboard.writeText(`{file_content}`).then(function() {{
                alert('Text copied to clipboard');
            }}, function(err) {{
                alert('Could not copy text: ', err);
            }});
            </script>
            """,
            height=0,
        )


def make_downloadable_file(file_path):
    with open(file_path, "r") as file:
        return file.read()


def make_downloadable_image(image_path):
    with open(image_path, "rb") as file:
        return file.read()


def zip_files(file_paths):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in file_paths:
            zip_file.write(file_path, os.path.basename(file_path))
    zip_buffer.seek(0)
    return zip_buffer


st.title("YouTube Audio Repurposer")

audio_file = st.file_uploader("Upload an audio file", type=["mp3", "wav"])
video_title = st.text_input("Enter a title for your video (optional):")

process_button = st.button("Process Audio")

if process_button and audio_file is not None:
    (
        transcript_path,
        summary_path,
        tweet_path,
        linkedin_post_path,
        image_paths,
    ) = repurpose_audio(audio_file, video_title)

    content_files = {
        transcript_path: "Transcription",
        summary_path: "Summary",
        tweet_path: "Generated Tweet",
        linkedin_post_path: "Generated LinkedIn Post",
    }

    for file_path, title in content_files.items():
        display_text_with_copy_button(file_path, title)

    # Display the LinkedIn Carousel
    st.subheader("LinkedIn Carousel")
    for index, image_path in enumerate(image_paths, start=1):
        st.subheader(f"Image {index}")
        st.image(image_path)
    zip_buffer = zip_files(image_paths)
    st.download_button(
        "Download Images", zip_buffer, file_name="LinkedIn_Carousel_Images.zip"
    )
