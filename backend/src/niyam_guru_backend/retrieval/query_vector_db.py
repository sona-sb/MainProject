# LangChain + Google Gemini imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
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

# Create a retriever from the loaded vector store (retrieve more cases for better context)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model=LLM_MODEL,
    temperature=0.3
)

# Custom prompt template for legal judgment prediction
legal_judgment_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are an expert legal analyst specializing in Indian Consumer Protection law. 
Your task is to analyze the user's case and predict the likely legal outcome based on similar past cases.

SIMILAR PAST CASES FROM DATABASE:
{context}

USER'S CURRENT CASE:
{question}

Based on the similar cases provided above, please provide:

1. **CASE ANALYSIS**: Briefly analyze the user's case and identify the key legal issues involved.

2. **SIMILAR CASES COMPARISON**: Compare the user's case with the retrieved similar cases. Highlight relevant precedents and how they relate to the current situation.

3. **APPLICABLE LEGAL PRINCIPLES**: Identify which sections of the Consumer Protection Act or other relevant laws would likely apply.

4. **PREDICTED OUTCOME**: Based on the patterns from similar cases, predict the most likely outcome for the user's case. Include:
   - Whether the consumer is likely to succeed
   - Potential compensation or relief that may be awarded
   - Strength of the case (Strong/Moderate/Weak)

5. **RECOMMENDATIONS**: Provide actionable advice for the consumer on how to proceed with their case.

Please be specific and cite the similar cases where relevant to support your analysis.
"""
)

# Create the RetrievalQA chain with custom prompt
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",
    return_source_documents=True,
    chain_type_kwargs={"prompt": legal_judgment_prompt}
)

print("✅ LLM and retriever are ready.")

# ========== Query Example ==========
print("\n--- Step 3: Running a Query ---")
query = """
A consumer bought a phone that exploded after 1 day of use. The seller refuses to acknowledge the issue, 
blaming the fault on the user's pattern of usage. The consumer has the purchase receipt and photos of the 
damaged phone. The phone was purchased for Rs. 25,000.

What are the chances of winning this case? What compensation can be expected?
"""
print(f"Query: {query}")

# Invoke the chain with the query
response = qa_chain.invoke({"query": query})

# ========== Display Results ==========
print("\n" + "=" * 70)
print("LEGAL JUDGMENT PREDICTION")
print("=" * 70)
print(response["result"])

print("\n" + "=" * 70)
print("SIMILAR CASES RETRIEVED")
print("=" * 70)
for i, doc in enumerate(response["source_documents"], 1):
    m = doc.metadata
    print(f"\n{i}. {m.get('case_title', 'Unknown Case')}")
    print(f"   Year: {m.get('year', 'N/A')} | Outcome: {m.get('outcome', 'N/A')}")
    print(f"   Citation: {m.get('citation', 'N/A')}")