from collections import defaultdict
import json
import os
from dotenv import load_dotenv
import faiss
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
from tools import calculate_experience_years
load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

resume_folder=r"C:\Users\smali\Desktop\Langchain\resume-detection\data"
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

vector_store.add_documents(documents=chunks)

@tool
def retrieve_ranking_resume(query: str,top_n_resumes=4, top_k_chunks=20) -> str:
    """
    Returns top 2 FULL resumes (joined chunks).
    """
    top_chunks = vector_store.similarity_search(query, k=top_k_chunks*top_n_resumes)

    # Group by document source
    grouped = defaultdict(list)
    for c in top_chunks:
        grouped[c.metadata["resume_id"]].append(c)

    final_resumes = []
    for _, chunks in grouped.items():
        sorted_chunks = sorted(chunks, key=lambda c: c.metadata.get("chunk_id", 0))
        final_resumes.append("\n".join([c.page_content for c in sorted_chunks[:top_k_chunks]]))


    return final_resumes[:top_n_resumes]

def build_query(title, skills):
    return f"{title}. Skills: {', '.join(skills)}"

title = "Software Engineer"
requirements = """
- Bachelor’s degree in Computer Science, Software Engineering, or related field.
- 2+ years of hands-on experience in software development.
- Strong proficiency in at least one programming language (Python, Java, JavaScript, C#, or Go).
- Experience building, testing, and deploying applications or APIs.
- Familiarity with cloud environments (AWS, Azure, or GCP).
- Solid understanding of data structures, algorithms, and OOP principles.
"""

system_prompt = """
You are an AI Resume Screening Assistant.

You will:
1. Build a short search query (3–6 words).
2. Call `retrieve_ranking_resume(query)` to fetch top resumes.
3. Extract the following for each resume:
   - candidate_id
   - matched_skills
   - years_experience
4. For years_experience:
    - You MUST call the tool calculate_experience_years
    - NEVER estimate manually
    - NEVER guess years from text
    - ALWAYS pass the FULL reconstructed resume text to the tool

5. Return JSON matching the ResumeOutput model exactly.

Do NOT hallucinate. Use ONLY text present in resumes.
"""
agent = create_agent(
    model,
    tools=[retrieve_ranking_resume,calculate_experience_years],
    system_prompt=system_prompt,
    response_format=ResumeOutput,
    checkpointer=InMemorySaver()
)

skill_reference = ["Python|Java|JavaScript|C#|Go", "AWS", "Azure", "GCP", 
                   "API"]
retrieval_query = build_query(title, skill_reference)

user_query = f"""

Use the following short retrieval query when calling the resume search tool:
{retrieval_query}
"""

response = agent.invoke(
    {"messages": [{"role": "user", "content": user_query}]},
    config={"configurable": {"thread_id": "1"}}
)
print(response['messages'][-1])