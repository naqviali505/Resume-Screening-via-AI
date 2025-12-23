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

# Step 1: Configuring API Keys and Initializing the pre-request of th AI Agent

load_dotenv()
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

resume_folder = r"C:\Users\smali\Desktop\Langchain\resume-detection\data"
list_of_resumes = [
    os.path.join(resume_folder, f)
    for f in os.listdir(resume_folder)
    if f.lower().endswith(".pdf")
]

chunks = get_chunks(list_of_resume=list_of_resumes)
embedding_dim = len(embeddings.embed_query("hello world"))
index = faiss.IndexFlatL2(embedding_dim)

vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={}
)

vector_store.add_documents(chunks)

SYSTEM_PROMPT = """
You are an AI Resume Screening Assistant.

You will receive EXACTLY ONE resume.

Rules:
- You MUST call calculate_experience_years exactly once
- You MUST pass the FULL resume text to the tool
- You MUST NOT estimate or guess experience
- You MUST NOT reuse values from other resumes

Extract:
- resume_id
- matched_skills
- years_experience

Return JSON strictly matching ResumeOutput.
"""

# ------------------------------------------------------------
# CREATE AGENT (MODERN API)
# ------------------------------------------------------------
agent = create_agent(
    model=model,
    tools=[calculate_experience_years],
    system_prompt=SYSTEM_PROMPT,
    response_format=ResumeOutput,
    checkpointer=InMemorySaver(),
)

# ------------------------------------------------------------
# QUERY BUILDING
# ------------------------------------------------------------
def build_query(title, skills):
    return f"{title}. Skills: {', '.join(skills)}"

title = "Software Engineer"

skill_reference = [
    "Python", "Java", "JavaScript", "C#", "Go",
    "AWS", "Azure", "GCP", "API"
]

retrieval_query = build_query(title, skill_reference)

# ------------------------------------------------------------
# FINAL ORCHESTRATION (THIS FIXES EVERYTHING)
# ------------------------------------------------------------

# 1️⃣ Retrieve resumes ONCE
retrieved_resumes = retrieve_ranking_resumes.invoke(retrieval_query)
final_results = []

# 2️⃣ Invoke agent ONCE PER RESUME
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
# results = []
# for idx, resume in enumerate(retrieved_resumes):
#     # Ensure resume_text is a string
#     if isinstance(resume, dict):
#         resume_text = resume.get("resume_text", "")
#     else:
#         resume_text = str(resume)

#     # Skip empty resumes
#     if not resume_text.strip():
#         continue

#     # Call the tool with the correct input
#     years = calculate_experience_years.invoke({"resume_text": resume_text})

#     results.append({
#         "candidate_id": f"candidate_{idx+1}",
#         "resume_text": resume_text[:100],
#         "years_experience": years
#     })

# print("GPT.PY")
# print(results)