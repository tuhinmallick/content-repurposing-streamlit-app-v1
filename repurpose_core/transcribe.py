import os
import dotenv
from openai import OpenAI
import uuid

dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _save_transcript(transcript, video_title):
    # Generate a unique directory name
    video_title = video_title if video_title else f"video_{uuid.uuid4().hex[:8]}"
    transcript_dir = f"./transcripts/{video_title}"
    os.makedirs(transcript_dir, exist_ok=True)

    # Extract text from the transcript object (assuming it has a 'text' attribute)
    transcript_text = (
        transcript.text if hasattr(transcript, "text") else str(transcript)
    )

    # Save transcript to transcript.txt in that directory
    transcript_path = os.path.join(transcript_dir, "transcript.txt")
    with open(transcript_path, "w") as f:
        f.write(transcript_text)
    return transcript_path


def transcribe_audio(audio_file, video_title=None):
    transcript = client.audio.transcriptions.create(file=audio_file, model="whisper-1")
    transcript_path = _save_transcript(transcript=transcript, video_title=video_title)
    return transcript.text, transcript_path
