# LangChain + Google Gemini imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_classic.chains.retrieval_qa.base import RetrievalQA

# Import configuration from settings
from niyam_guru_backend.config import (
    EMBEDDING_MODEL,
    LLM_MODEL,
    VECTORSTORE_DIR,
)

print("--- Step 1: Loading Existing Vector Database ---")
# ========== Load Embeddings and Vector Store ==========

# Initialize the embedding model
embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

# Load the persisted vector store from disk
vectorstore = Chroma(
    persist_directory=str(VECTORSTORE_DIR),
    embedding_function=embeddings
)

print(f"✅ Database loaded successfully from: '{VECTORSTORE_DIR}'")


print("\n--- Step 2: Setting up the LLM and Retriever ---")
# ========== Retriever & LLM Setup ==========

# Create a retriever from the loaded vector store
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model=LLM_MODEL,
    temperature=0.2
)

# Create the RetrievalQA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",
    return_source_documents=True
)

print("✅ LLM and retriever are ready.")

# ========== Query Example ==========
print("\n--- Step 3: Running a Query ---")
query = """
A consumer bought a phone that exploded after 1 day of use. The seller refuses acknowledge the issue blaming the fault on the users pattern of usage.
Which sections apply under the Consumer Protection Act? What legal remedies can i go for here?
"""
print(f"Query: {query}")

# Invoke the chain with the query
response = qa_chain.invoke(query)

# ========== Display Results ==========
print("\n--- LLM Answer ---\n")
print(response["result"])

print("\n--- Retrieved Sections ---\n")
for doc in response["source_documents"]:
    m = doc.metadata
    print(f"- {m['section_identifier']}: {m['section_title']} (Chapter: {m['chapter_title']})")