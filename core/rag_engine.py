# import os
# from langchain_mistralai import ChatMistralAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.runnables import RunnablePassthrough, RunnableLambda
# from core.vector_store import build_vector_store, load_vector_store, get_retriever

# def get_llm():
#     return ChatMistralAI(
#         model="mistral-small-latest",
#         mistral_api_key=os.getenv("MISTRAL_API_KEY"),
#         temperature=0.3,
#     )

# def format_docs(docs):
#     return "\n\n".join([doc.page_content for doc in docs])

# def build_rag_chain(transcript:str):

#     vector_store = build_vector_store(transcript)

#     retriever = get_retriever(vector_store, k = 4)

#     llm = get_llm()

#     prompt = ChatPromptTemplate.from_messages(

#         [(
#             "system",
#             """You are an expert meeting assistant. Answer the user's question 
# based ONLY on the meeting transcript context provided below.

# If the answer is not found in the context, say: 
# "I could not find this information in the meeting transcript."

# Always be concise and precise. If quoting someone, mention it clearly.

# Context from meeting transcript:
# {context}""",
#         ),
#         ("human", "{question}"),
#     ]
#     )

#     #full LCEL Rag pipeline 

#     rag_chain = (

#         {"context" : retriever | RunnableLambda(format_docs),
#          "question": RunnablePassthrough()
#          }
#          |prompt|llm|StrOutputParser()
#     )

#     return rag_chain


# def load_rag_chain():
#     vector_store = load_vector_store()
#     retriver = get_retriever()

#     llm = get_llm()
#     prompt = ChatPromptTemplate.from_messages([
#         (
#             "system",
#             """You are an expert meeting assistant. Answer the user's question 
# based ONLY on the meeting transcript context provided below.

# If the answer is not found in the context, say: 
# "I could not find this information in the meeting transcript."

# Always be concise and precise. If quoting someone, mention it clearly.

# Context from meeting transcript:
# {context}""",
#         ),
#         ("human", "{question}"),
#     ])

#     rag_chain = (
#         {
#             "context":  retriver| RunnableLambda(format_docs),
#             "question": RunnablePassthrough(),
#         }
#         | prompt
#         | llm
#         | StrOutputParser()
#     )

#     return rag_chain


# def ask_question(rag_chain, question:str) -> str:
#     print(f"Question : {question}")
#     answer = rag_chain.invoke(question)
#     print(f"answer :{answer}")
#     return answer
# import os
# from dotenv import load_dotenv
# from langchain_groq import ChatGroq
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import RunnablePassthrough
# from langchain_core.output_parsers import StrOutputParser

# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# if not GROQ_API_KEY:
#     raise ValueError("GROQ_API_KEY is missing from environment variables.")

# # Initialize Groq LLM
# llm = ChatGroq(
#     groq_api_key=GROQ_API_KEY,
#     model_name="llama-3.3-70b-versatile",
#     temperature=0.2
# )

# # RAG Prompt instructing the model to answer based strictly on video transcript context
# RAG_PROMPT_TEMPLATE = """You are an intelligent AI Video Assistant.
# Answer the user's question using ONLY the provided video transcript context below.
# If the answer cannot be found in the context, explicitly state: "This information is not discussed in the video."
# Always keep your answers clear, accurate, and concise.

# Context from video:
# {context}

# Question:
# {question}

# Answer:"""

# prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

# def format_docs(docs):
#     """Formats retrieved document chunks into a single text block."""
#     return "\n\n".join(doc.page_content for doc in docs)

# def build_rag_chain(vector_store):
#     """
#     Builds a LangChain Runnable RAG chain using the provided vector store retriever.
    
#     Args:
#         vector_store: A Chroma, FAISS, or LangChain vector store instance.
#     """
#     retriever = vector_store.as_retriever(search_kwargs={"k": 4})

#     rag_chain = (
#         {"context": retriever | format_docs, "question": RunnablePassthrough()}
#         | prompt
#         | llm
#         | StrOutputParser()
#     )
#     return rag_chain

# def ask_video(vector_store, question: str) -> str:
#     """
#     Helper function to query the RAG chain directly.
#     """
#     chain = build_rag_chain(vector_store)
#     return chain.invoke(question)

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing from environment variables.")

# Use the fast, rate-limit friendly Groq model
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="openai/gpt-oss-20b",
    temperature=0.2
)

RAG_PROMPT_TEMPLATE = """You are an intelligent AI Video Assistant.
Answer the user's question using ONLY the provided video transcript context below.
If the answer cannot be found in the context, explicitly state: "This information is not discussed in the video."
Always keep your answer clear, accurate, and grounded.

Context from video:
{context}

Question:
{question}

Answer:"""

prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

def format_docs(docs):
    """Formats retrieved document chunks into a single text block."""
    return "\n\n".join(doc.page_content for doc in docs)

def build_rag_chain(source_input):
    """
    Builds a RAG chain handling both VectorStores and raw transcript strings.
    """
    # Case 1: Vector store with retriever support
    if hasattr(source_input, "as_retriever"):
        retriever = source_input.as_retriever(search_kwargs={"k": 4})
        return (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

    # Case 2: Raw string transcript passed directly
    transcript_text = str(source_input)
    return (
        {"context": lambda _: transcript_text[:12000], "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

def ask_question(chain_or_context, question: str) -> str:
    """
    Answers questions whether passed a VectorStore, an existing chain, or a raw transcript string.
    """
    # If it's a raw string (transcript)
    if isinstance(chain_or_context, str):
        chain = (
            {"context": lambda _: chain_or_context[:12000], "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        return chain.invoke(question)

    # If it's a vector store object
    if hasattr(chain_or_context, "as_retriever"):
        chain = build_rag_chain(chain_or_context)
        return chain.invoke(question)

    # If it's already an instantiated runnable chain
    if hasattr(chain_or_context, "invoke"):
        return chain_or_context.invoke(question)

    # Fallback to direct prompt
    return (prompt | llm | StrOutputParser()).invoke({
        "context": str(chain_or_context)[:12000],
        "question": question
    })

# Backward-compatible alias
ask_video = ask_question