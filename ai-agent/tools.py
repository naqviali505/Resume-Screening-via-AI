from collections import defaultdict
import re
from datetime import datetime
import dateparser
from langchain.tools import tool

@tool
def calculate_experience_years(resume_text: str) -> float:
    """
    Calculates total professional experience in years.
    If a work period overlaps with education, only the overlapping portion is removed.
    """
    # 1. Normalize text
    resume_text = resume_text.replace("–", "-").replace("—", "-")
    # PDFs often use special "non-breaking spaces" (\u00A0) or thin spaces to control layout
    resume_text = re.sub(r"[\u00A0\u2000-\u200B\u202F\u205F\u3000]", " ", resume_text)
    # This line finds any sequence of one or more whitespace characters (\s+) and replaces them with a single space
    resume_text = re.sub(r"\s+", " ", resume_text)

    # 2. Extract Sections with better boundaries
    # 
    work_match = re.search(r"(?:PROFESSIONAL EXPERIENCE|WORK EXPERIENCE)(.*?)(?=PROJECTS|EDUCATION|SKILLS|INTERESTS|$)", resume_text, flags=re.IGNORECASE | re.DOTALL)
    edu_match = re.search(r"(?:EDUCATION|ACADEMIC)(.*?)(?=PROFESSIONAL|WORK|PROJECTS|SKILLS|$)", resume_text, flags=re.IGNORECASE | re.DOTALL)
    
    # .group(1): Returns the text caught by the first set of parentheses.
    work_section = work_match.group(1).strip() if work_match else ""
    edu_section = edu_match.group(1).strip() if edu_match else ""

    date_pattern = r"(?P<start>(?:\d{1,2}[/-])?\d{4}|[A-Za-z]{3,}\s+\d{4})\s*(?:-|to)\s*(?P<end>Present|Now|Current|(?:\d{1,2}[/-])?\d{4}|[A-Za-z]{3,}\s+\d{4})"

    # 3. Parse Education Ranges
    education_intervals = []
    for m in re.finditer(date_pattern, edu_section, flags=re.IGNORECASE):
        s = dateparser.parse(m.group("start"), settings={"PREFER_DAY_OF_MONTH": "first"})
        e = dateparser.parse(m.group("end"), settings={"PREFER_DAY_OF_MONTH": "first"})
        if s and e:
            education_intervals.append((s.replace(day=1), e.replace(day=1)))

    # 4. Parse Work Ranges
    work_intervals = []
    now = datetime.now()
    for m in re.finditer(date_pattern, work_section, flags=re.IGNORECASE):
        s = dateparser.parse(m.group("start"), settings={"PREFER_DAY_OF_MONTH": "first"})
        end_raw = m.group("end").lower()
        e = now if end_raw in ["present", "now", "current"] else dateparser.parse(m.group("end"), settings={"PREFER_DAY_OF_MONTH": "first"})
        
        if s and e:
            s, e = (s, e) if s < e else (e, s)
            work_intervals.append([s.replace(day=1), e.replace(day=1)])

    # 5. SUBTRACTION LOGIC (The Fix)
    final_work_intervals = []
    for w_start, w_end in work_intervals:
        current_periods = [(w_start, w_end)]
        for e_start, e_end in education_intervals:
            next_periods = []
            for s, e in current_periods:
                # If there is an overlap, split the work period
                if s < e_end and e > e_start:
                    # Keep the part before education starts
                    if s < e_start:
                        next_periods.append((s, e_start))
                    # Keep the part after education ends
                    if e > e_end:
                        next_periods.append((e_end, e))
                else:
                    next_periods.append((s, e))
            current_periods = next_periods
        final_work_intervals.extend(current_periods)

    # 6. Merge & Sum
    final_work_intervals.sort()
    merged = []
    for s, e in final_work_intervals:
        if not merged or s > merged[-1][1]:
            merged.append((s, e))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))

    total_months = sum((e.year - s.year) * 12 + (e.month - s.month) for s, e in merged)
    return round(total_months / 12, 1)

# Retrieval Layer
@tool
def retrieve_ranking_resumes(query: str,vector_store,top_n_resumes: int = 4,top_k_chunks: int = 20):
    """
    Returns resumes as structured objects:
    [
      { resume_id, resume_text }
    ]
    """
    top_chunks = vector_store.similarity_search(query, k=top_n_resumes * top_k_chunks)

    grouped = defaultdict(list)
    for c in top_chunks:
        grouped[c.metadata["resume_id"]].append(c)

    resumes = []
    for resume_id, chunks in grouped.items():
        sorted_chunks = sorted(chunks, key=lambda c: c.metadata.get("chunk_id", 0))
        resumes.append({
            "resume_id": resume_id,
            "resume_text": "\n".join(c.page_content for c in sorted_chunks[:top_k_chunks])
        })

    return resumes[:top_n_resumes]