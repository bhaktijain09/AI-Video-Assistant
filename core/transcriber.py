# import whisper
# import os
# import requests
# from pydub import AudioSegment

# # Sarvam's sync STT-translate API rejects audio longer than 30s.
# # We slice each chunk into 25s pieces (with a 5s safety margin) before sending.
# SARVAM_PIECE_SECONDS = 25


# WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")


# SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
# SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
# SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")

# _model = None


# def load_model():

#     global _model  

#     if _model is None: 
#         print(f"Loading Whisper model: {WHISPER_MODEL} ...")
#         _model = whisper.load_model(WHISPER_MODEL) 
#         print("Whisper model loaded.")
#     return _model 


# def transcribe_chunk_whisper(chunk_path: str) -> str:

#     model = load_model()  

#     result = model.transcribe(chunk_path, task="transcribe")  
#     return result["text"]  


# def _send_to_sarvam(piece_path: str) -> str:
#     """Send one ≤30s WAV file to Sarvam and return the English transcript."""
#     headers = {"api-subscription-key": SARVAM_API_KEY}

#     with open(piece_path, "rb") as f:
#         files = {"file": (os.path.basename(piece_path), f, "audio/wav")}
#         data = {"model": SARVAM_MODEL, "with_diarization": "false"}
#         response = requests.post(
#             SARVAM_STT_TRANSLATE_URL,
#             headers=headers,
#             files=files,
#             data=data,
#             timeout=120,
#         )

#     if not response.ok:
#         print(f"\n❌ Sarvam returned {response.status_code}")
#         print(f"Response body: {response.text}\n")
#         response.raise_for_status()

#     return response.json().get("transcript", "")


# def transcribe_chunk_sarvam(chunk_path: str) -> str:
#     """
#     Sarvam sync API only accepts ≤30s audio. We split this chunk into
#     25-second pieces, send each separately, and join the transcripts.
#     """
#     if not SARVAM_API_KEY:
#         raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

#     audio = AudioSegment.from_wav(chunk_path)
#     piece_ms = SARVAM_PIECE_SECONDS * 1000

#     full_text = ""
#     total_pieces = (len(audio) + piece_ms - 1) // piece_ms

#     for i, start in enumerate(range(0, len(audio), piece_ms)):
#         piece = audio[start: start + piece_ms]
#         piece_path = f"{chunk_path}_sv_{i}.wav"
#         piece.export(piece_path, format="wav")

#         try:
#             print(f"  → Sarvam piece {i + 1}/{total_pieces} ...")
#             full_text += _send_to_sarvam(piece_path) + " "
#         finally:
#             if os.path.exists(piece_path):
#                 os.remove(piece_path)

#     return full_text.strip()

   



# def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
#     """
#     Route one chunk to Whisper or Sarvam depending on language choice.
#     - english  → Whisper (local model)
#     - hinglish → Sarvam (translates to English while transcribing)
#     """
#     if language.lower() == "hinglish":
#         return transcribe_chunk_sarvam(chunk_path)
#     return transcribe_chunk_whisper(chunk_path)


# def transcribe_all(chunks: list, language: str = "english") -> str:

#     full_transcript = "" 

#     engine = "Sarvam AI" if language.lower() == "hinglish" else "Whisper"
#     print(f"Using {engine} for transcription.")

#     for i, chunk in enumerate(chunks):  

#         print(f"Transcribing chunk {i + 1}/{len(chunks)}...")

#         text = transcribe_chunk(chunk, language=language)  

#         full_transcript += text + " "  

#     print("Transcription complete.")

#     return full_transcript.strip()  
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from pydub import AudioSegment
from youtube_transcript_api import YouTubeTranscriptApi

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_video_id(url_or_id: str) -> str:
    """Extracts YouTube 11-char ID from various URL formats."""
    match = re.search(r"(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})", url_or_id)
    return match.group(1) if match else url_or_id

def try_youtube_captions(video_source: str) -> str | None:
    """Attempts to fetch pre-existing captions directly from YouTube."""
    try:
        vid_id = extract_video_id(video_source)
        transcript_data = YouTubeTranscriptApi.get_transcript(vid_id)
        text = " ".join([item["text"] for item in transcript_data])
        return text
    except Exception:
        return None

def compress_audio_to_mp3(file_path: str, max_size_mb: int = 24) -> str:
    """Converts bulky WAV chunks into compact 64k mono MP3 under 25MB."""
    audio = AudioSegment.from_file(file_path)
    # Convert to mono and 16kHz
    audio = audio.set_channels(1).set_frame_rate(16000)
    
    mp3_path = file_path.rsplit(".", 1)[0] + "_compressed.mp3"
    audio.export(mp3_path, format="mp3", bitrate="64k")
    return mp3_path

def transcribe_audio_file(file_path: str, language: str = "en") -> str:
    """Sends audio to Groq Whisper, ensuring it stays under the 25MB limit."""
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    target_path = file_path

    # If over 24MB or in WAV format, compress it first
    if file_size_mb > 24 or file_path.endswith(".wav"):
        target_path = compress_audio_to_mp3(file_path)

    with open(target_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(target_path), file.read()),
            model="whisper-large-v3-turbo",
            response_format="text",
            language="en" if language.lower() == "english" else None
        )
    
    # Clean up compressed temp file if created
    if target_path != file_path and os.path.exists(target_path):
        os.remove(target_path)

    return transcription

def transcribe_all(chunks, language: str = "english", source_url: str = None) -> str:
    """
    Main transcription entry point:
    1. Tries instant YouTube caption retrieval if source URL is provided.
    2. Falls back to Groq Cloud Whisper with MP3 compression.
    """
    if source_url:
        print("Checking YouTube auto-captions first...")
        caption_text = try_youtube_captions(source_url)
        if caption_text:
            print(" Captions retrieved directly from YouTube!")
            return caption_text
        print("No direct captions found. Falling back to Groq Whisper...")

    if isinstance(chunks, str):
        chunks = [chunks]

    full_transcript = []
    for idx, chunk_path in enumerate(chunks):
        print(f" -> Transcribing chunk {idx + 1}/{len(chunks)}...")
        text = transcribe_audio_file(chunk_path, language=language)
        full_transcript.append(text)

    return "\n".join(full_transcript)