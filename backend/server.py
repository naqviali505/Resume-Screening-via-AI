from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import shutil
import os
import json
app = FastAPI()

import sys
sys.path.insert(1,r"C:\Users\smali\Desktop\Langchain\Resume-Screening-via-AI\ai-agent")
sys.path.insert(1,r"C:\Users\smali\Desktop\Langchain\Resume-Screening-via-AI\ai-agent\utils")

from helper import get_chunks
from prompt import build_query
from agent import get_pre_requisites,get_agent
from tools import create_retrieval_tool

model,vector_store = get_pre_requisites()

# Enable CORS so React can talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/process-resumes")
async def process_resumes(
    job_title: str = Form(...),
    experience: float = Form(...),
    skills: str = Form(...),
    files: List[UploadFile] = File(...)
):
    # 1. Save Files
    saved_paths = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_paths.append(file_path)

    chunks = get_chunks(list_of_resume=saved_paths)
    vector_store.add_documents(chunks)
    retrieve_tool = create_retrieval_tool(vector_store)
    resume_agent= get_agent(model=model,retreive_tool=retrieve_tool)

    # 3. Parse Skills and Build Query
    skills_list = json.loads(skills)
    query = build_query(job_title, skills_list, experience)

    # 4. Run Agent
    try:
        agent_resp = resume_agent.invoke(
            {"messages": [{"role": "user", "content": f"Find candidates for: {query}"}]})
        return {"status": "success", "candidates": agent_resp["messages"][-1]} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
