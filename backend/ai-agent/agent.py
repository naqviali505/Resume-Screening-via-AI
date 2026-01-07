import faiss
from dotenv import load_dotenv
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from models import ResumeOutput
from tools import calculate_experience_years
from prompt import SYSTEM_PROMPT
import os
# Step 1: Configuring API Keys and Initializing the pre-request of th AI Agent
API_KEY_STORAGE = {"key": None}
VECTOR_STORE=None

def get_pre_requisites(api_key=None):
    global VECTOR_STORE
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        API_KEY_STORAGE["key"] = api_key
    elif API_KEY_STORAGE.get("key"):
        os.environ["GOOGLE_API_KEY"] = API_KEY_STORAGE["key"]
    else:
        load_dotenv()

    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", max_retries=0)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    if VECTOR_STORE is None:
        embedding_dim = len(embeddings.embed_query("hello world"))
        index = faiss.IndexFlatL2(embedding_dim)
        VECTOR_STORE = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={}
        )
    return model, VECTOR_STORE

def get_agent(model,retrieve_tool):
    agent = create_agent(
        model=model,
        tools=[calculate_experience_years,retrieve_tool],
        system_prompt=SYSTEM_PROMPT,
        response_format=ResumeOutput,
    )
    return agent