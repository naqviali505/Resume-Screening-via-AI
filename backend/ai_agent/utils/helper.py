import os
import re
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader
from langchain_core.documents import Document

# Define common resume sections
SECTION_HEADERS = [
    r'contact', r'personal details?', r'summary|objective|profile', r'education',
    r'(work )?experience|employment history', r'skills|technical skills|core competencies',
    r'projects|personal projects', r'certifications|licenses',
    r'awards|honors|achievements', r'publications', r'languages', r'interests|hobbies'
]
SECTION_PATTERNS = [re.compile(h, re.IGNORECASE) for h in SECTION_HEADERS]

def get_chunks(list_of_resumes):
    """
    Section-based chunking for resumes.
    Splits resumes by logical sections (Experience, Education, Skills, etc.).
    Each section becomes a single chunk with metadata.
    """
    all_chunks = []

    for resume_path in list_of_resumes:
        ext = os.path.splitext(resume_path)[1].lower()

        # Load the resume
        if ext == ".pdf":
            loader = PyPDFLoader(resume_path)
        elif ext in [".doc", ".docx"]:
            loader = UnstructuredWordDocumentLoader(resume_path)
        else:
            continue

        docs = loader.load()
        resume_text = "\n".join(doc.page_content for doc in docs)

        # Detect sections
        sections = detect_sections(resume_text)

        # Convert sections to chunks
        chunk_id = 0
        for section_name, section_text in sections:
            if section_text.strip():
                all_chunks.append(Document(
                    page_content=section_text.strip(),
                    metadata={
                        "resume_id": os.path.basename(resume_path),
                        "section": section_name,
                        "chunk_id": chunk_id,
                        "source": resume_path
                    }
                ))
                chunk_id += 1

    return all_chunks

def detect_sections(resume_text):
    """
    Splits resume text into sections based on SECTION_HEADERS.
    Returns list of (section_name, section_text).
    """
    lines = resume_text.split("\n")
    sections = []
    current_section = ("Unknown", [])

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue

        # Check if the line matches any known section header
        matched = False
        for pattern in SECTION_PATTERNS:
            if pattern.fullmatch(line_clean.lower()):
                matched = True
                section_name = line_clean
                # Save previous section
                if current_section[1]:
                    sections.append((current_section[0], "\n".join(current_section[1])))
                current_section = (section_name, [])
                break

        if not matched:
            current_section[1].append(line_clean)

    # Append last section
    if current_section[1]:
        sections.append((current_section[0], "\n".join(current_section[1])))

    return sections
