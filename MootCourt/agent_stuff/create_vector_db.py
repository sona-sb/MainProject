import os
import pandas as pd
import time

# LangChain + Google Gemini imports
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

# ========== Configuration / Setup ==========
load_dotenv()
# Ensure your Google API key is set as an environment variable
# os.getenv("GOOGLE_API_KEY")

# --- Configuration ---
EMBEDDING_MODEL = "models/gemini-embedding-001"
CSV_PATH = r"D:\MootCourt\supreme_court_judgments\consumer_laws.csv"
PERSIST_DIRECTORY = "./consumer_act_gemini_db"

print("--- Step 1: Loading CSV and Creating Documents ---")

# ========== Load CSV and Create Documents ==========
df = pd.read_csv(CSV_PATH)

docs = []
for _, row in df.iterrows():
    content = f"{row['Section_Identifier']} — {row['Section_Title']}\n{row['Section_Text']}"
    metadata = {
        "chapter_number": row["Chapter_Number"],
        "chapter_title": row["Chapter_Title"],
        "section_identifier": row["Section_Identifier"],
        "section_title": row["Section_Title"]
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
    persist_directory=PERSIST_DIRECTORY
)

# Add documents to the vector store one by one with a delay to avoid rate limiting
print("Adding documents to the vector store with delays to respect API rate limits...")
for i, doc in enumerate(docs):
    vectorstore.add_documents([doc])  # The method expects a list
    time.sleep(0.6)  # 0.6-second delay keeps us under 100 RPM
    print(f"Embedded and added document {i + 1}/{len(docs)}")

# Persist the database to disk
vectorstore.persist()

print(f"\n✅ Vector database has been successfully created and saved in: '{PERSIST_DIRECTORY}'")