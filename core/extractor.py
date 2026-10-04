# #Actionableitems , decision , questions 

# from langchain_mistralai import ChatMistralAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.runnables import RunnablePassthrough, RunnableLambda
# import os 


# def get_llm():
#     return ChatMistralAI(model = "mistral-small-latest", mistral_api_key = os.getenv("MISTRAL_API_KEY"),temperature=0.2)



# def build_chain(system_prompt : str):
#     llm = get_llm()
#     return (
#         RunnablePassthrough() | RunnableLambda(lambda x : {"text" : x}) |ChatPromptTemplate.from_messages([
#         ("system", system_prompt),
#         ("human","{text}"),
#     ]) | llm |StrOutputParser()
#     )

# def extract_action_items(transcript:str)->str:
#     chain = build_chain(
#          "You are an expert meeting analyst. From the meeting transcript, "
#         "extract all action items. For each provide:\n"
#         "- Task description\n"
#         "- Owner (who is responsible)\n"
#         "- Deadline (if mentioned, else write 'Not specified')\n\n"
#         "Format as a numbered list. If none found say 'No action items found.'"
#     )

#     return chain.invoke(transcript)


# def extract_key_decisions(transcript: str) -> str:
#     chain = build_chain(
#         "You are an expert meeting analyst. From the meeting transcript, "
#         "extract all key decisions made. Format as a numbered list. "
#         "If none found say 'No key decisions found.'"
#     )
#     return chain.invoke(transcript)


# def extract_questions(transcript: str) -> str:
#     chain = build_chain(
#         "From the meeting transcript, extract all unresolved questions "
#         "or topics needing follow-up. Format as a numbered list. "
#         "If none found say 'No open questions found.'"
#     )
#     return chain.invoke(transcript)

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing from environment variables.")

# Use the verified Groq model
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="openai/gpt-oss-120b",
    temperature=0.2
)

def extract_action_items(transcript: str) -> str:
    """Extracts concrete, actionable steps mentioned in the transcript."""
    prompt = PromptTemplate.from_template(
        """You are an expert assistant. Analyze the video transcript below and extract all actionable tasks, recommendations, or steps to take.
Present them as a clean, bulleted checklist. If none are present, state 'No clear action items found.'

Transcript:
{transcript}

Action Items:"""
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"transcript": transcript[:12000]})


def extract_key_decisions(transcript: str) -> str:
    """Extracts major decisions, conclusions, or critical stances."""
    prompt = PromptTemplate.from_template(
        """You are an expert assistant. Review the following video transcript and identify key decisions, conclusions, or pivotal viewpoints established by the speaker.
Format them as clear bullet points.

Transcript:
{transcript}

Key Decisions:"""
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"transcript": transcript[:12000]})


def extract_questions(transcript: str) -> str:
    """Extracts open questions, unsolved issues, or audience discussion prompts."""
    prompt = PromptTemplate.from_template(
        """You are an expert assistant. From the transcript below, identify any unanswered questions, rhetorical inquiries, or open discussion points raised.
List them clearly.

Transcript:
{transcript}

Open Questions:"""
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"transcript": transcript[:12000]})