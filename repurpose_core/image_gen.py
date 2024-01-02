import os
import dotenv
from openai import OpenAI
import requests
import json

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def _download_and_save_image(url, path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, "wb") as file:
            file.write(response.content)


def generate_images_for_linkedin_carousel(video_summary_path, video_title):
    # Read the video summary
    with open(video_summary_path, "r") as file:
        video_summary = file.read()

    summary_chunks = split_summary_with_openai_chat(video_summary)
    print("Summary chunks:", summary_chunks)
    # Define the directory to save images
    base_dir = os.path.dirname(video_summary_path)
    video_dir = os.path.join(
        base_dir, video_title if video_title else "LinkedIn_Carousel"
    )
    os.makedirs(video_dir, exist_ok=True)

    image_paths = []
    for chunk in summary_chunks:
        chunk_text = chunk.get("text", "")
        image_gen_prompt = f"""Generate an image based on the following chunk of text from an summary of a video. Do no add any letters or words to the images. \n\n --- \n\n #CHUNK TEXT {chunk_text} \n\n # END OF CHUNK TEXT --- \n\n Begin!"""
        response = openai_client.images.generate(
            model="dall-e-3", prompt=image_gen_prompt, n=1, size="1024x1024"
        )
        if response and response.data:
            image_url = response.data[0].url
            image_path = os.path.join(
                video_dir, f"image_{chunk.get('sequence_order')}.jpg"
            )
            _download_and_save_image(image_url, image_path)
            image_paths.append(image_path)

    print(f"Generated {len(image_paths)} images for LinkedIn carousel.")
    return image_paths


def split_summary_with_openai_chat(summary, num_chunks=3):
    """
    Splits the summary into a sequence of texts using OpenAI Chat model.

    :param summary: The video summary text.
    :param num_chunks: Number of chunks to divide the summary into.
    :return: A list of text chunks.
    """
    try:
        prompt = f"""Divide the following summary delimited by <s> tags into {num_chunks} parts that flow well together and capture the main ideas:
                    \n\n
                    --- 
                    <s>
                    # SUMMARY
                    {summary}
                    # END OF SUMMARY
                    <s>
                    ---
                    Return the chunks in the following json format:
                    {{
                    "chunks": [
                                {{"sequence_order": int, "text": string }}
                            ]   
                    }}
                """

        response = openai_client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "Please divide this text."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        if response:
            response_text = response.choices[0].message.model_dump_json()
            print(f"Response: ===== \n{response_text}")
            # Parse the JSON response
            json_string = json.loads(response_text)["content"]
            print(f"JSON String: ===== \n{json_string}")
            # Now parse the JSON string
            json_response = json.loads(json_string)
            print(f"JSON Response: ===== \n{json_response}")

            chunks = json_response.get("chunks", [])
            return chunks

    except Exception as e:
        print(f"An error occurred: {e}")
        return []
