import os
from dotenv import load_dotenv
from google import genai
load_dotenv()
from app.schemas.song import Song, SongAnalysis

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_prompt(artist_name, song_name):
    return f"""
You are a guitar instructor analyzing songs for guitar students.

Analyze the standard/original guitar arrangement of:

Song: "{song_name}"
Artist: "{artist_name}"

Evaluate what a guitarist would need to play a recognizable and
reasonably faithful version of the song.

Use a difficulty scale from 1 to 10:

1-2: suitable for a complete beginner
3-4: beginner
5-6: intermediate
7-8: advanced
9-10: expert

Evaluate:

- overall_difficulty:
  Overall difficulty of learning the song on guitar.

- rhythm_difficulty:
  Difficulty of the rhythm guitar parts, including timing,
  strumming patterns, chord changes, and riffs.

- lead_difficulty:
  Difficulty of lead guitar parts and melodic guitar lines.

- solo_difficulty:
  Difficulty of the guitar solo.
  Use 1 if the song has no meaningful guitar solo.

- tempo_difficulty:
  How much the song's speed makes it difficult to perform.

- tuning:
  Give the commonly used guitar tuning for the original recording,
  such as "E Standard", "Eb Standard", "Drop D", or "Drop C".

- required_chords:
  List the important chord names or chord types required to play
  the song. Do not attempt to list every passing chord.

- techniques:
  List the important guitar techniques required and assign each
  technique a difficulty from 1 to 10.

- explanation:
  In 2-4 sentences, explain the main reasons for the difficulty
  rating and what a guitarist should be comfortable with before
  learning the song.

- confidence:
  A number from 0.0 to 1.0 representing your confidence that the
  analysis is accurate.

Do not invent unusual techniques simply to fill the response.
If information about the exact guitar arrangement is uncertain,
reflect that uncertainty in the confidence score.
"""

def get_song_analysis(song: Song):
    print(f"starting ai analysis for {song.song_name}")
    interaction = client.interactions.create(
        model="gemini-3.1-flash-lite",
        input= get_prompt(song.artist_name, song.song_name),
        response_format={
                        "type": "text",
                        "mime_type": "application/json",
                        "schema": SongAnalysis.model_json_schema(),
                        }
    )
    print(f"ended ai analsis")

    return SongAnalysis.model_validate_json(interaction.output_text)