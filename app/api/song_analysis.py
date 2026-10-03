import os
from dotenv import load_dotenv
from google import genai
load_dotenv()
from app.schemas.song import Song, SongAnalysisBATCH
import time

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_prompt(songs):
    all_songs = "\n".join(f"{song.song_name} - {song.artist_name}" for song in songs)

    return f"""
You are a guitar instructor.

Analyze each of these songs for someone learning them on guitar:

{all_songs}

For each song, determine its tuning, overall difficulty,
rhythm difficulty, lead difficulty, solo difficulty,
tempo difficulty, important chords, important guitar techniques,
a short explanation, and your confidence.

Difficulty values must be from 1 to 10.
Confidence must be from 0.0 to 1.0.

Analyze every song in the list.
"""

def get_songs_analysis(songs: list[Song]):
    start_time = time.time()
    print(f"{time.strftime("%H:%M:%S", time.gmtime())}: start analyzing songs")

    interaction = client.interactions.create(
        model="gemini-3.5-flash-lite",
        input= get_prompt(songs),
        #generation_config= {"thinking_level": "low"},
        generation_config= {"thinking_level": "minimal"},
        response_format={
                        "type": "text",
                        "mime_type": "application/json",
                        "schema": SongAnalysisBATCH.model_json_schema(),
                        }
    )
    
    end_time = time.time()
    print(f"{time.strftime("%H:%M:%S", time.gmtime())}: finished analyzing songs in {end_time - start_time:.2f} seconds")

    return (SongAnalysisBATCH.model_validate_json(interaction.output_text)).songs