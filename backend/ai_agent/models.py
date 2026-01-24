# --- Corrected and Consolidated Models ---
from pydantic import BaseModel, Field
from typing import List

class Candidate(BaseModel):
    candidate_id: str = Field(description="Full name, email, or filename if name not found.")
    matched_skills: List[str] = Field(description="List of skills that are explicitly mentioned in the resume and match the job requirements.")
    reason: str = Field(description="Explanation of why this candidate was selected or why fields are empty. Focus on matching skills and experience.")
    years_experience: float = Field(description="The total cumulative professional experience in years, calculated to 1 decimal place.")

class ResumeOutput(BaseModel):
    ranked_candidates: List[Candidate] = Field(description="A list of the top ranked candidates based on the job requirements.")
    