# 🚀 Installation & Setup

## 1. Clone the repository
```
git clone https://github.com/bhaktijain09/AI-Video-Assistant.git
```

Move into the project:
```
cd AI-Video-Assistant
```

---

## 2. Create a virtual environment

### Windows
```
python -m venv venv
```

Activate it:
```
venv\Scripts\activate
```

### macOS / Linux
```
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install dependencies
```
pip install -r Requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root.
```
YOUTUBE_API_KEY=your_youtube_api_key
GROQ_API_KEY=your_groq_api_key
```

---

# 🎞️ FFmpeg Setup

The project uses FFmpeg for audio/video processing.

Make sure FFmpeg is installed and available in your system PATH.

Verify the installation:
```
ffmpeg -version
```

and:
```
ffprobe -version
```

If both commands return version information, FFmpeg is configured correctly.

---

# ▶️ Run the Application

Start the Streamlit application with:
```
python -m streamlit run app.py
```

After starting, Streamlit will provide a local URL similar to:
```
http://localhost:8501
```

Open that URL in your browser.

---

# 🎯 How to Use

### 1. Provide a meeting source

Enter either:

- A YouTube video URL
- A local video/audio file path

### 2. Select the language

Choose:

- English
- Hinglish

### 3. Analyse the meeting

Click:
```
⚡ Analyse
```

The application processes the meeting and generates:

- Meeting title
- Summary
- Transcript
- Action items
- Key decisions
- Open questions

### 4. Explore the meeting

After the analysis is complete, use:
```
💬 Want to explore this meeting further?
```

to enable the Q&A interface.

You can then ask questions about the meeting transcript.

---

# 🧠 RAG-powered Q&A

The application uses Retrieval-Augmented Generation to make the meeting transcript searchable.

The general workflow is:
```
Transcript
    │
    ▼
Document Chunking
    │
    ▼
Embeddings
    │
    ▼
Vector Store
    │
    ▼
Relevant Context Retrieval
    │
    ▼
   LLM
    │
    ▼
  Answer
```

This allows users to ask questions such as:
```
What were the main decisions made?

Who was responsible for the action items?

What problems were discussed?

What are the unresolved questions?

What was the main conclusion of the meeting?
```

---

# ⚠️ Notes

- FFmpeg is required for media processing.
- The first execution of Whisper or embedding models may take additional time because models may need to be downloaded.
- Processing time depends on the length of the video and available system resources.
- YouTube availability may depend on the video and yt-dlp compatibility.

---
