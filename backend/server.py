import re
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
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

# Enable CORS so React can talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
API_KEY_STORAGE={}
UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/process-resumes")
async def process_resumes(
    job_title: str = Form(...),
    experience: float = Form(...),
    shortListCandidates: int = Form(...),
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
    api_key = API_KEY_STORAGE.get("key")
    model, vector_store = get_pre_requisites(api_key=api_key)    
    vector_store.add_documents(chunks)
    retrieve_tool = create_retrieval_tool(vector_store,shortListCandidates)
    resume_agent= get_agent(model,retrieve_tool)

    # 3. Parse Skills and Build Query
    skills_list = json.loads(skills)
    resume_skills = json.dumps(skills_list)
    query = build_query(job_title, resume_skills, experience)

    # 4. Run Agent
    try:
        agent_resp = resume_agent.invoke({"messages": [{"role": "user", "content": f"Find candidates for: {query}"}]})
        ranked_candidates = agent_resp['messages'][-1].content

        # pattern = r"Candidate\(\s*candidate_id=(?:'|\")(.+?)(?:'|\"),\s*matched_skills=\[(.*?)\],\s*reason='(.+?)',\s*years_experience=([\d.]+)\s*\)"
        pattern = r"""
        Candidate\(
        \s*candidate_id=(?:'|")(.+?)(?:'|"),
        \s*matched_skills=\[(.*?)\],
        \s*reason=(?:'|")(.+?)(?:'|"),
        \s*years_experience=([\d.]+)
        \s*\)
        """

        matches = re.findall(pattern, ranked_candidates, re.DOTALL | re.VERBOSE)
        result = []
        for cid, skills, reason, years in matches:
            result.append({
                "candidate_id": cid,
                "matched_skills": [s.strip().strip("'") for s in skills.split(",")],
                "reason": reason.strip(),
                "years_experience": float(years)
            })
        return {"status": "success","candidates":result} 
    except Exception as e:
        error_msg = str(e).lower()
        if "quota" in error_msg or "resourceexhausted" in error_msg or "429" in error_msg:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": (
                        "You have exceeded the free usage limit for AI requests. "
                        "Please add your own API key to continue using this feature."
                    ),
                    "action": "ENTER_API_KEY"
                }
            )

@app.post("/set-api-key")
async def set_api_key(request: Request):
    data = await request.json()
    api_key = data.get("api_key")
    if not api_key:
        return {"status": "error", "message": "API key missing"}

    API_KEY_STORAGE["key"] = api_key
    get_pre_requisites(api_key=api_key)

    return {"status": "success", "message": "API key set"}