import os
import re
import tempfile
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader ,TextLoader ,UnstructuredWordDocumentLoader , UnstructuredExcelLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter


EMBED_MODEL_NAME = 'all-MiniLM-L6-v2'

# ----------------------------
# Load Vector Database

@st.cache_resource
def load_vector_db():
    """
    Initializes and caches the vector database with HuggingFace embeddings.
    """
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)
    vectordb = Chroma(embedding_function=embeddings)
    return vectordb

# ----------------------------
# PDF Processing

def process_pdf(pdf_path, doc_name,file_path):
    """
    Loads and splits PDF into text chunks with metadata.
    """
    if file_path == ".pdf":
        loader = PyPDFLoader(pdf_path)
    elif file_path == ".txt":
        loader = TextLoader(pdf_path)
    elif file_path == ".docx":
        loader = UnstructuredWordDocumentLoader(pdf_path)
    elif file_path in [".xls", ".xlsx"]:
        loader = UnstructuredExcelLoader(pdf_path)
    else:
        raise ValueError(f"Unsupported file type: {pdf_path}")

    pages = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=20,
        separators=["\n\n", "\n", ".", " "]
    )
    docs = splitter.split_documents(pages)

    for doc in docs:
        doc.metadata["source"] = doc_name

    return docs

# ----------------------------
# Embedding Documents

def embed_documents(uploaded_files, vectordb, files_to_remove=None):
    """
    Embeds new PDF files and optionally removes old ones from the vector DB.
    """
    all_docs = []
    new_files = []

    if files_to_remove:
        for file_name in files_to_remove:
            vectordb._collection.delete(where={"source": file_name})
        st.success(f"Removed {len(files_to_remove)} file(s) from the database.")

    for uploaded_file in uploaded_files:
        doc_name = uploaded_file.name
        file_path = os.path.splitext(doc_name)[1].lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_path) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        docs = process_pdf(tmp_path, doc_name, file_path)
        all_docs.extend(docs)
        new_files.append(doc_name)

    if all_docs:
        vectordb.add_documents(all_docs)

    return vectordb, len(new_files)

# ----------------------------
# Text Filtering

def has_overlap(question: str, content: str, min_overlap: int = 3) -> bool:
    """
    Checks if the content shares at least `min_overlap` words with the question.
    """
    words_q = set(re.findall(r'\w+', question.lower()))
    words_c = set(re.findall(r'\w+', content.lower()))
    return len(words_q & words_c) >= min_overlap

def filter_relevant_chunks(question, documents, min_overlap=3):
    """
    Filters relevant document chunks based on word overlap with the question.
    Returns a list of (content, source) tuples.
    """
    seen_chunks = set()
    filtered = []

    for doc in documents:
        content = doc.page_content.strip()
        if content not in seen_chunks and has_overlap(question, content, min_overlap):
            seen_chunks.add(content)
            source = doc.metadata.get("source", "Unknown")
            filtered.append((content, source))

    return filtered

def build_context(filtered_chunks):
    """
    Builds a single text context string from the list of filtered chunks.
    """
    return "\n\n".join([chunk for chunk, _ in filtered_chunks])
