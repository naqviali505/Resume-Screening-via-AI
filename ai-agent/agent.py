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

# Step 1: Configuring API Keys and Initializing the pre-request of th AI Agent

def get_pre_requisites():
    load_dotenv()
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )
    # Storage Layer
    # This line programmatically determines that size (dimension) so the database knows 
    # how much "space" to allocate for each chunk.
    embedding_dim = len(embeddings.embed_query("hello world"))
    # This specific index uses Euclidean Distance (L2) to find similarity.
    # Think of it like a map. It plots every chunk as a point in a massive 1536-dimensional space.
    # When you search, it finds the "points" (chunks) that have the shortest straight-line distance to your query.

    index = faiss.IndexFlatL2(embedding_dim)
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={}
    )
    return model,vector_store
# # This is the "Execution" step.
# # Step A (Embedding): It sends all your 800-character chunks to your embedding model and returns a list of numbers for every chunk.
# # Step B (Indexing): It inserts those numbers into the FAISS index and stores the text + metadata in the Docstore.

def get_agent(model,retrieve_tool):
    agent = create_agent(
        model=model,
        tools=[calculate_experience_years,retrieve_tool],
        system_prompt=SYSTEM_PROMPT,
        response_format=ResumeOutput,
    )
    return agent