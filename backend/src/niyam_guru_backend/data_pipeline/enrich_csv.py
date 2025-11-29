import pandas as pd
import os
import time
import signal
import sys
import fitz  # PyMuPDF

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Import configuration from settings
from niyam_guru_backend.config import (
    RAW_JUDGMENTS_DIR,
    CONSUMER_CASES_CSV,
    ENRICH_MODEL,
    API_RATE_LIMIT_SECONDS,
)

# Global variable to hold DataFrame for graceful shutdown
_df_global = None
_save_path_global = None


def save_progress():
    """Save current progress to CSV"""
    global _df_global, _save_path_global
    if _df_global is not None and _save_path_global is not None:
        _df_global.to_csv(_save_path_global, index=False)
        print(f"\n💾 Progress saved to: {_save_path_global}")


def signal_handler(signum, frame):
    """Handle interrupt signals gracefully"""
    print("\n\n⚠️  Interrupt received! Saving progress before exit...")
    save_progress()
    print("✅ Progress saved. You can resume later by running the script again.")
    sys.exit(0)


def extract_full_text_from_pdf(pdf_path, max_pages=15):
    """Extract text from PDF for LLM analysis (more pages for better context)"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for i, page in enumerate(doc):
            if i >= max_pages:
                break
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return None


def create_analysis_chain():
    """Create the LangChain chain for analyzing case documents"""
    
    llm = ChatGoogleGenerativeAI(
        model=ENRICH_MODEL,
        temperature=0.2,
    )
    
    prompt_template = PromptTemplate(
        input_variables=["case_text"],
        template="""You are a legal analyst specializing in Indian Consumer Protection law. 
Analyze the following court judgment and extract the requested information.

JUDGMENT TEXT:
{case_text}

Based on the above judgment, provide the following in JSON format:

1. "case_context": A concise summary (2-3 sentences) of the key facts of the case - who are the parties, what is the dispute about, what product/service is involved, and the main grievance.

2. "legal_reasoning": A summary (2-4 sentences) of the statutory analysis - which sections of the Consumer Protection Act or other laws were applied, any precedents cited, and the court's interpretation of the law.

3. "decision_summary": A brief summary (1-2 sentences) of the final outcome - was the appeal allowed/dismissed, what relief was granted (compensation amount, refund, replacement, etc.).

Respond ONLY with valid JSON in this exact format:
{{
    "case_context": "...",
    "legal_reasoning": "...",
    "decision_summary": "..."
}}

If any information is not available in the text, use "Not available in document" for that field.
"""
    )
    
    parser = JsonOutputParser()
    chain = prompt_template | llm | parser
    
    return chain


def enrich_csv_with_llm_analysis():
    """Main function to enrich the CSV with LLM-generated columns"""
    global _df_global, _save_path_global
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 70)
    print("ENRICHING CSV WITH LLM ANALYSIS")
    print("=" * 70)
    
    # Load existing CSV
    print(f"\n📂 Loading CSV from: {CONSUMER_CASES_CSV}")
    df = pd.read_csv(CONSUMER_CASES_CSV)
    print(f"   Found {len(df)} records")
    
    # Set global references for graceful shutdown
    _df_global = df
    _save_path_global = CONSUMER_CASES_CSV
    
    # Initialize new columns if they don't exist
    if 'case_context' not in df.columns:
        df['case_context'] = None
    if 'legal_reasoning' not in df.columns:
        df['legal_reasoning'] = None
    if 'decision_summary' not in df.columns:
        df['decision_summary'] = None
    
    # Create the analysis chain
    print(f"\n🤖 Initializing LLM: {ENRICH_MODEL}")
    print(f"   Rate limit: {API_RATE_LIMIT_SECONDS} seconds between requests")
    chain = create_analysis_chain()
    
    # Track progress
    total = len(df)
    processed = 0
    skipped = 0
    errors = 0
    
    print(f"\n🔄 Processing {total} cases...\n")
    
    for idx, row in df.iterrows():
        # Skip if already processed (successfully or with known errors)
        case_context = row.get('case_context')
        if pd.notna(case_context) and case_context not in ['', None]:
            skipped += 1
            continue
        
        pdf_file = row['PDF_File']
        folder = row['Folder']
        pdf_path = os.path.join(RAW_JUDGMENTS_DIR, str(folder), pdf_file)
        
        print(f"[{idx + 1}/{total}] Processing: {pdf_file}")
        
        # Check if PDF exists
        if not os.path.exists(pdf_path):
            print(f"   ⚠️  PDF not found, skipping")
            errors += 1
            continue
        
        # Extract text from PDF
        case_text = extract_full_text_from_pdf(pdf_path)
        if not case_text or len(case_text.strip()) < 100:
            print(f"   ⚠️  Insufficient text extracted, skipping")
            df.at[idx, 'case_context'] = "Not available in document"
            df.at[idx, 'legal_reasoning'] = "Not available in document"
            df.at[idx, 'decision_summary'] = "Not available in document"
            errors += 1
            continue
        
        # Truncate text if too long (to stay within token limits)
        max_chars = 15000
        if len(case_text) > max_chars:
            case_text = case_text[:max_chars] + "\n\n[Document truncated...]"
        
        try:
            # Call the LLM
            result = chain.invoke({"case_text": case_text})
            
            # Update DataFrame
            df.at[idx, 'case_context'] = result.get('case_context', 'Not available in document')
            df.at[idx, 'legal_reasoning'] = result.get('legal_reasoning', 'Not available in document')
            df.at[idx, 'decision_summary'] = result.get('decision_summary', 'Not available in document')
            
            processed += 1
            print(f"   ✅ Successfully analyzed")
            
            # Save after each successful record to prevent data loss
            df.to_csv(CONSUMER_CASES_CSV, index=False)
            
            # Rate limiting - configurable delay between API calls
            time.sleep(API_RATE_LIMIT_SECONDS)
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
            df.at[idx, 'case_context'] = "Error during analysis"
            df.at[idx, 'legal_reasoning'] = "Error during analysis"
            df.at[idx, 'decision_summary'] = "Error during analysis"
            errors += 1
            # Save after errors too
            df.to_csv(CONSUMER_CASES_CSV, index=False)
            # Longer delay after errors (double the normal rate)
            time.sleep(API_RATE_LIMIT_SECONDS * 2)
        
        # Progress update every 10 records
        if (processed + errors) % 10 == 0:
            print(f"\n   📊 Progress: {processed} processed, {skipped} skipped, {errors} errors\n")
    
    # Final save
    df.to_csv(CONSUMER_CASES_CSV, index=False)
    
    # Print summary
    print("\n" + "=" * 70)
    print("ENRICHMENT SUMMARY")
    print("=" * 70)
    print(f"Total records: {total}")
    print(f"Newly processed: {processed}")
    print(f"Previously processed (skipped): {skipped}")
    print(f"Errors: {errors}")
    print(f"\n✅ CSV saved: {CONSUMER_CASES_CSV}")
    print("=" * 70)
    
    # Show sample of new columns
    if processed > 0:
        print("\n📋 Sample of enriched data:")
        sample = df[df['case_context'].notna()].head(1)
        for col in ['case_context', 'legal_reasoning', 'decision_summary']:
            print(f"\n{col}:")
            print(f"  {sample[col].values[0][:200]}..." if len(str(sample[col].values[0])) > 200 else f"  {sample[col].values[0]}")


if __name__ == "__main__":
    enrich_csv_with_llm_analysis()