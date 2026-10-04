# from dotenv import load_dotenv
# load_dotenv()   # MUST be before any core/ imports

# from utils.audio_processor import process_input
# from core.transcriber import transcribe_all
# from core.summarizer import summarize, generate_title
# from core.extractor import extract_action_items, extract_key_decisions, extract_questions


# source = "https://www.youtube.com/watch?v=_Q-e_nczWqM&t=223s"
# language = "english"   # "english" → Whisper, "hinglish" → Sarvam



# chunks = process_input(source)


# transcript = transcribe_all(chunks, language=language)
# print("\n" + "=" * 60)
# print("📝 TRANSCRIPT")
# print("=" * 60)
# print(transcript[:500] + "..." if len(transcript) > 500 else transcript)


# title = generate_title(transcript)
# summary = summarize(transcript)

# print("\n" + "=" * 60)
# print(f"📌 TITLE: {title}")
# print("=" * 60)
# print("\n📋 SUMMARY")
# print("-" * 60)
# print(summary)



# action_items = extract_action_items(transcript)
# decisions = extract_key_decisions(transcript)
# questions = extract_questions(transcript)

# print("\n" + "=" * 60)
# print("✅ ACTION ITEMS")
# print("=" * 60)
# print(action_items)

# print("\n" + "=" * 60)
# print("🔑 KEY DECISIONS")
# print("=" * 60)
# print(decisions)

# print("\n" + "=" * 60)
# print("❓ OPEN QUESTIONS")
# print("=" * 60)
# print(questions)
import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Load environment variables first
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# 2. Import project modules
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions

# Choose a test video URL
source = "https://www.youtube.com/watch?v=_Q-e_nczWqM"
language = "english"

print("=" * 60)
print("1. Processing Audio / Downloading...")
print("=" * 60)
chunks = process_input(source)

print("\n" + "=" * 60)
print("2. Transcribing Audio...")
print("=" * 60)
transcript = transcribe_all(chunks, language=language, source_url=source)
print(transcript[:500] + "..." if len(transcript) > 500 else transcript)

print("\n" + "=" * 60)
print("3. Generating Title & Summary...")
print("=" * 60)
title = generate_title(transcript)
summary = summarize(transcript)
print(f"📌 TITLE: {title}")
print("\n📋 SUMMARY:\n", summary)

print("\n" + "=" * 60)
print("4. Extracting Structured Knowledge...")
print("=" * 60)
action_items = extract_action_items(transcript)
decisions = extract_key_decisions(transcript)
questions = extract_questions(transcript)

print("✅ ACTION ITEMS:\n", action_items)
print("\n🔑 KEY DECISIONS:\n", decisions)
print("\n❓ OPEN QUESTIONS:\n", questions)