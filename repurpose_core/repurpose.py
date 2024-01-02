from repurpose_core.transcribe import transcribe_audio
from repurpose_core.summarize import (
    summarize_transcription,
    map_reduce_summarize_text,
    summarize_with_gpt_4,
)
from repurpose_core.image_gen import generate_images_for_linkedin_carousel
import uuid
import os
from openai import OpenAI

import dotenv

dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _save_summary(summary, video_title):
    video_title = video_title if video_title else f"video_{uuid.uuid4().hex[:8]}"
    summary_dir = f"./summaries/{video_title}"
    os.makedirs(summary_dir, exist_ok=True)

    summary_path = os.path.join(summary_dir, "summary.txt")
    with open(summary_path, "w") as f:
        f.write(summary)
    return summary_path


def _save_post(content, post_type, video_title):
    video_title = video_title if video_title else f"video_{uuid.uuid4().hex[:8]}"
    post_dir = f"./posts/{video_title}"
    os.makedirs(post_dir, exist_ok=True)
    post_path = os.path.join(post_dir, f"{post_type}_post.txt")
    with open(post_path, "w") as f:
        f.write(content)
    return post_path


def _generate_tweet(summary_path, video_title):
    try:
        with open(summary_path, "r") as file:
            summary = file.read()

        result = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Create a concise, engaging tweet based on this summary:\n{summary}",
                }
            ],
        )
        tweet = result.choices[0].message.content
        return _save_post(tweet, "tweet", video_title)
    except Exception as e:
        return f"An error occurred: {e}"


def _generate_linkedin_post(summary_path, video_title):
    try:
        with open(summary_path, "r") as file:
            summary = file.read()

        result = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Create a professional LinkedIn post based on this summary:\n{summary}",
                }
            ],
        )
        linkedin_post = result.choices[0].message.content
        return _save_post(linkedin_post, "linkedin", video_title)
    except Exception as e:
        return f"An error occurred: {e}"


def repurpose_audio(audio_path, video_title=None):
    transcription, transcript_path = transcribe_audio(audio_path, video_title)
    summary = summarize_with_gpt_4(transcription, video_title)
    summary_path = _save_summary(summary, video_title)
    tweet_path = _generate_tweet(summary_path, video_title)
    linkedin_post_path = _generate_linkedin_post(summary_path, video_title)
    image_paths = generate_images_for_linkedin_carousel(summary_path, video_title)

    return transcript_path, summary_path, tweet_path, linkedin_post_path, image_paths


# def generate_corrected_transcript(transcript):
#     system_prompt = """
#         You are a helpful AI assistant, intended to fix any spelling or grammar mistakes in user audio transcript.
#         \nIf words appear incorrect or there are run-on word, fix the transcript the best you can.
#     """
#     response = client.chat.completions.create(
#         model="gpt-",
#         temperature=TEMP,
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": transcript},
#         ],
#     )
#     return response["choices"][0]["message"]["content"]
