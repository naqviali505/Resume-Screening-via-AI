import os
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader
from langchain_text_splitters import CharacterTextSplitter
# Ingestion Layer
def get_chunks(list_of_resume, chunk_size=800, chunk_overlap=180):
    """
    Loads resumes and splits them into fixed-size chunks using CharacterTextSplitter.
    Supports both PDF and DOCX files.
    Ensures each document is kept separate via metadata.
    """
    all_docs = []

    for resume_path in list_of_resume:
        ext = os.path.splitext(resume_path)[1].lower()

        # Load the resume file
        if ext == ".pdf":
            loader = PyPDFLoader(resume_path)
        elif ext in [".doc", ".docx"]:
            loader = UnstructuredWordDocumentLoader(resume_path)
        else:
            continue

        docs = loader.load()
        
        # Add metadata so each resume is kept separate
        for doc in docs:
            doc.metadata["resume_id"] = os.path.basename(resume_path)
        all_docs.extend(docs)

    chunker = CharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,  
    )

    # Apply chunking to all docs
    chunks = chunker.split_documents(all_docs)
    for i, c in enumerate(chunks):
        c.metadata["chunk_id"] = i

    return chunks