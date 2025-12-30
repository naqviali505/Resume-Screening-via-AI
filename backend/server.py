import re
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


    # chunks = get_chunks(list_of_resume=saved_paths)
    # vector_store.add_documents(chunks)
    # retrieve_tool = create_retrieval_tool(vector_store,shortListCandidates)
    # resume_agent= get_agent(model,retrieve_tool)

    # # 3. Parse Skills and Build Query
    # skills_list = json.loads(skills)
    # resume_skills = json.dumps(skills_list)
    # query = build_query(job_title, resume_skills, experience)

    # 4. Run Agent
    try:
        # agent_resp = resume_agent.invoke(
        #     {"messages": [{"role": "user", "content": f"Find candidates for: {query}"}]})
        # print(agent_resp['messages'][-1])
        # return {"status": "success", "candidates":agent_resp["messages"][-1].content}
        ranked_candidates = """
        Candidate(
            candidate_id='Mahnoor Khaliq-1_250903_183755.pdf',
            matched_skills=['Python', 'JavaScript', 'AWS'],
            reason='Candidate has 1.1 years of experience as a Backend Developer, exceeding the 1.0 year requirement. Possesses strong skills in Python, JavaScript, and AWS, which are all explicitly mentioned in the resume.',
            years_experience=1.1
        ), 
        Candidate(
            candidate_id="Ahsam's Resume.pdf",
            matched_skills=['Python', 'JavaScript'],
            reason='Candidate has 2.0 years of experience as a Software Engineer, exceeding the 1.0 year requirement. Possesses strong skills in Python and JavaScript, which are explicitly mentioned in the resume.',
            years_experience=2.0
        )
        """

        pattern = r"Candidate\(\s*candidate_id=(?:'|\")(.+?)(?:'|\"),\s*matched_skills=\[(.*?)\],\s*reason='(.+?)',\s*years_experience=([\d.]+)\s*\)"
        matches = re.findall(pattern, ranked_candidates, re.DOTALL)

        result = []
        for cid, skills, reason, years in matches:
            result.append({
                "candidate_id": cid,
                "matched_skills": [s.strip().strip("'") for s in skills.split(",")],
                "reason": reason.strip(),
                "years_experience": float(years)
            })
        return {"status": "success", "candidates":result} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
