import pandas as pd
import time

# LangChain + Google Gemini imports
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Import configuration from settings
from niyam_guru_backend.config import (
    CONSUMER_CASES_CSV,
    VECTORSTORE_DIR,
    EMBEDDING_MODEL,
)

print("--- Step 1: Loading CSV and Creating Documents ---")

# ========== Load CSV and Create Documents ==========
df = pd.read_csv(CONSUMER_CASES_CSV)

docs = []
for _, row in df.iterrows():
    # Build content from case information for embedding
    case_context = row.get('case_context', '') or ''
    legal_reasoning = row.get('legal_reasoning', '') or ''
    decision_summary = row.get('decision_summary', '') or ''
    headnote = row.get('Headnote', '') or ''
    
    content = f"""Case: {row['Case Title']}
Petitioner: {row['Petitioner']} vs Respondent: {row['Respondent']}
Year: {row['Year']}

Case Context: {case_context}

Legal Reasoning: {legal_reasoning}

Decision Summary: {decision_summary}

Headnote: {headnote}"""
    
    metadata = {
        "case_title": row["Case Title"],
        "petitioner": row["Petitioner"],
        "respondent": row["Respondent"],
        "year": str(row["Year"]),
        "date_of_judgment": str(row.get("Date of Judgment", "")),
        "outcome": str(row.get("Outcome", "")),
        "citation": str(row.get("Citation", "")),
        "pdf_file": str(row.get("PDF_File", "")),
        "folder": str(row.get("Folder", ""))
    }
    docs.append(Document(page_content=content, metadata=metadata))

print(f"Loaded {len(docs)} documents from CSV.")

print("\n--- Step 2: Creating and Persisting Vector Database ---")
# ========== Create Gemini-based Embeddings & Vector Store ==========

# Initialize the embedding model
embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

# Initialize an empty Chroma vector store with a persist directory
vectorstore = Chroma(
    embedding_function=embeddings,
    persist_directory=str(VECTORSTORE_DIR)
)

# Add documents to the vector store one by one with a delay to avoid rate limiting
print("Adding documents to the vector store with delays to respect API rate limits...")
for i, doc in enumerate(docs):
    vectorstore.add_documents([doc])  # The method expects a list
    time.sleep(0.6)  # 0.6-second delay keeps us under 100 RPM
    print(f"Embedded and added document {i + 1}/{len(docs)}")

# Persist the database to disk
vectorstore.persist()

print(f"\n✅ Vector database has been successfully created and saved in: '{VECTORSTORE_DIR}'")