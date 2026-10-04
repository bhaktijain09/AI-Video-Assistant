# from langchain_mistralai import ChatMistralAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# import os 

# def get_llm():
#     return ChatMistralAI(model = "mistral-small-latest", mistral_api_key = os.getenv("MISTRAL_API_KEY"),temperature=0.3)


# def split_transcript(transcript: str) -> list:
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size = 3000,
#         chunk_overlap = 200
#     )

#     return splitter.split_text(transcript)

# def summarize(transcript : str) -> str:
#     llm = get_llm()

#     map_prompt = ChatPromptTemplate.from_messages(
#         [
#         ("system", "Summarize this portion of a meeting transcript concisely."),
#         ("human", "{text}"),
#     ]
#     )

#     map_chain = map_prompt | llm | StrOutputParser()

#     chunks = split_transcript(transcript)

#     chunk_summaries = [map_chain.invoke({"text" : chunk}) for chunk in chunks]

#     combined = "\n\n".join(chunk_summaries)

#     combined_prompt = ChatPromptTemplate.from_messages(
#         [
#         (
#             "system",
#             "You are an expert meeting summarizer. Combine these partial summaries "
#             "into one final professional meeting summary in bullet points.",
#         ),
#         ("human", "{text}"),
#     ]
#     )

#     combined_chain = (
#         RunnablePassthrough() | RunnableLambda(lambda x:{"text":x}) | combined_prompt | llm | StrOutputParser()
#     )

#     return combined_chain.invoke(combined)

# def generate_title(transcipt : str) -> str:
#     llm = get_llm()

    

#     title_chain = (
#         RunnablePassthrough() | RunnableLambda(lambda x:{"text":x}) | 
#         ChatPromptTemplate.from_messages([
#              (
#                 "system",
#                 "Based on the meeting transcript, generate a short professional meeting title "
#                 "(max 8 words). Only return the title, nothing else.",
#             ),
#             ("human", "{text}"),
#         ])
#         | llm
#         |StrOutputParser()
#     )

#     return title_chain.invoke(transcipt[:2000])

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# Load .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing from environment variables.")

# Using Groq's available open-weights model
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="openai/gpt-oss-120b",
    temperature=0.3
)

def generate_title(transcript_text: str) -> str:
    """Generates a concise, catchy title for the video based on its transcript."""
    prompt = PromptTemplate.from_template(
        """Based on the following video transcript, generate a concise, engaging, and clear title for this content.
Output ONLY the title and nothing else.

Transcript:
{transcript}

Title:"""
    )
    chain = prompt | llm
    response = chain.invoke({"transcript": transcript_text[:4000]})
    return response.content.strip()

def summarize(transcript_text: str) -> str:
    """Generates a structured, comprehensive summary of the transcript."""
    prompt = PromptTemplate.from_template(
        """You are an expert AI video analyst. Provide a structured summary of the following transcript.
Include:
- Key Theme / Overview
- Core Takeaways (in bullet points)
- Important Explanations

Transcript:
{transcript}

Summary:"""
    )
    chain = prompt | llm
    response = chain.invoke({"transcript": transcript_text[:12000]})
    return response.content.strip()