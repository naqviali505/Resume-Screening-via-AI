from collections import Counter
import os
import faiss
from dotenv import load_dotenv
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from utils.retrieve_chunks import get_chunks
from models import ResumeOutput
from tools import calculate_experience_years,retrieve_ranking_resumes
from prompt import SYSTEM_PROMPT
from prompt import build_query

# Step 1: Configuring API Keys and Initializing the pre-request of th AI Agent

load_dotenv()
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

resume_folder = r"C:\Users\smali\Desktop\Langchain\Resume-Screening-via-AI\data"
list_of_resumes = [
    os.path.join(resume_folder, f)
    for f in os.listdir(resume_folder)
    if f.lower().endswith(".pdf")
]

chunks = get_chunks(list_of_resume=list_of_resumes)
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
# # This is the "Execution" step.
# # Step A (Embedding): It sends all your 800-character chunks to your embedding model and returns a list of numbers for every chunk.
# # Step B (Indexing): It inserts those numbers into the FAISS index and stores the text + metadata in the Docstore.
vector_store.add_documents(chunks)

agent = create_agent(
    model=model,
    tools=[calculate_experience_years],
    system_prompt=SYSTEM_PROMPT,
    response_format=ResumeOutput,
    checkpointer=InMemorySaver(),
)
title = "Software Engineer"
skill_reference = ["Python", "Java", "JavaScript", "C#", "Go","AWS", "Azure", "GCP", "API"]
retrieval_query = build_query(title, skill_reference)

retrieved_resumes = retrieve_ranking_resumes.invoke(retrieval_query)
final_results = []

for resume in retrieved_resumes:
    response = agent.invoke(
        {
            "messages": [{
                "role": "user",
                "content": f"""
                    Resume ID: {resume['resume_id']}

                    Resume Text:
                    {resume['resume_text']}
                    """
                }]
        },
        config={
            "configurable": {
                "thread_id": resume["resume_id"]
            }
        }
    )
    final_results.append(response["messages"][-1])
print(final_results)
