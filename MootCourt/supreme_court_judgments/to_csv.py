import fitz  # PyMuPDF
import re
import pandas as pd
import os

def extract_text_from_pdf(pdf_path, max_pages=5):
    """Extract text from first 5 pages (increased for better coverage)"""
    doc = fitz.open(pdf_path)
    text = ""
    for i, page in enumerate(doc):
        if i >= max_pages:
            break
        text += page.get_text()
    return text

def extract_case_title_from_filename(filename):
    """Extract case title from filename"""
    name = filename.replace('.PDF', '').replace('.pdf', '')
    name = re.sub(r'_\d+$', '', name)
    parts = name.split('_on_')
    if len(parts) > 0:
        title = parts[0].replace('_', ' ')
        return title
    return name.replace('_', ' ')

def extract_date_from_filename(filename):
    """Extract date from filename"""
    date_pattern = r'on_(\d{1,2})_(January|February|March|April|May|June|July|August|September|October|November|December)_(\d{4})'
    match = re.search(date_pattern, filename, re.IGNORECASE)
    if match:
        return f"{match.group(1)} {match.group(2)} {match.group(3)}"
    return None

def extract_date_from_text(text):
    """Extract date from text with multiple patterns"""
    # Pattern 1: DATE OF JUDGMENT: 14/03/1950
    date_pattern1 = r'DATE OF JUDGMENT:\s*(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})'
    match = re.search(date_pattern1, text, re.IGNORECASE)
    if match:
        months = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
        return f"{match.group(1)} {months[int(match.group(2))]} {match.group(3)}"
    
    # Pattern 2: 14 March, 1950 or 9 February 1951
    date_pattern2 = r'\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December),?\s+(\d{4})\b'
    match = re.search(date_pattern2, text, re.IGNORECASE)
    if match:
        return f"{match.group(1)} {match.group(2)} {match.group(3)}"
    
    return None

def extract_parties_enhanced(text):
    """Enhanced party extraction with multiple patterns"""
    petitioner = None
    respondent = None
    
    # Pattern 1: Standard PETITIONER:\n NAME format
    pet_match = re.search(r'PETITIONER:\s*\n\s*([^\n]+?)(?:\n|\s+Vs\.|\s+V/s)', text, re.IGNORECASE | re.DOTALL)
    if pet_match:
        petitioner = pet_match.group(1).strip()
        # Clean up common artifacts
        petitioner = re.sub(r'\s+', ' ', petitioner)
    
    # Pattern 2: Standard RESPONDENT:\n NAME format
    resp_match = re.search(r'RESPONDENT:\s*\n\s*([^\n]+?)(?:\n|DATE OF JUDGMENT)', text, re.IGNORECASE | re.DOTALL)
    if resp_match:
        respondent = resp_match.group(1).strip()
        respondent = re.sub(r'\s+', ' ', respondent)
    
    # Pattern 3: Try to extract from case title if not found
    if not petitioner or not respondent:
        vs_pattern = r'([^v]+?)\s+(?:vs?\.?|versus)\s+([^\n]+?)(?:\n|on\s+\d{1,2})'
        title_match = re.search(vs_pattern, text[:500], re.IGNORECASE)
        if title_match:
            if not petitioner:
                petitioner = title_match.group(1).strip()
            if not respondent:
                respondent = title_match.group(2).strip()
    
    return {
        "Petitioner": petitioner,
        "Respondent": respondent
    }

def extract_bench(text):
    """Extract bench composition"""
    # Pattern: BENCH:\nJUDGE NAMES or Judge: Name
    bench_pattern = r'BENCH:\s*\n\s*([^\n]+(?:\n[A-Z][^\n]+)*?)(?:\n\s*\n|CITATION|ACT:)'
    match = re.search(bench_pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        bench = match.group(1).strip()
        # Clean and return first 200 chars
        bench = re.sub(r'\s+', ' ', bench)
        return bench[:200] if len(bench) > 200 else bench
    return None

def extract_consumer_case_type(text):
    """Extract specific consumer case type"""
    # Check for specific consumer law terms
    if re.search(r'deficiency\s+(?:in|of)\s+service', text, re.IGNORECASE):
        return "Deficiency in Service"
    elif re.search(r'unfair\s+trade\s+practice', text, re.IGNORECASE):
        return "Unfair Trade Practice"
    elif re.search(r'product\s+liability', text, re.IGNORECASE):
        return "Product Liability"
    elif re.search(r'medical\s+negligence', text, re.IGNORECASE):
        return "Medical Negligence"
    elif re.search(r'National Consumer Disputes Redressal Commission|NCDRC', text, re.IGNORECASE):
        return "NCDRC Appeal"
    elif re.search(r'State Consumer Disputes Redressal Commission|SCDRC|State Commission', text, re.IGNORECASE):
        return "SCDRC Appeal"
    elif re.search(r'District Consumer Disputes Redressal Commission|DCDRC|District (?:Forum|Commission)', text, re.IGNORECASE):
        return "DCDRC Appeal"
    elif re.search(r'consumer\s+dispute', text, re.IGNORECASE):
        return "Consumer Dispute"
    elif re.search(r'Consumer Protection Act', text, re.IGNORECASE):
        return "Consumer Protection"
    return None

def extract_statutes_enhanced(text):
    """Extract all statute references"""
    statutes = []
    
    # Pattern 1: Section X of Consumer Protection Act
    pattern1 = re.finditer(r'Section\s+(\d{1,3}(?:\([a-z0-9]+\))?)\s+of\s+(?:the\s+)?(?:Consumer Protection Act|CPA)(?:,?\s+(?:19\d{2}|20\d{2}))?', text, re.IGNORECASE)
    for match in pattern1:
        statutes.append(match.group(0))
    
    # Pattern 2: CPA 1986/2019 references
    pattern2 = re.finditer(r'(?:Consumer Protection Act|CPA),?\s+(19\d{2}|20\d{2})', text, re.IGNORECASE)
    for match in pattern2:
        statutes.append(match.group(0))
    
    # Pattern 3: Article references
    pattern3 = re.finditer(r'Article\s+\d{1,3}(?:\([a-z0-9]+\))?', text, re.IGNORECASE)
    for match in pattern3:
        statutes.append(match.group(0))
    
    # Remove duplicates and return joined string
    statutes = list(set(statutes))
    return "; ".join(statutes[:5]) if statutes else None  # Limit to 5 most relevant

def extract_outcome_enhanced(text):
    """Enhanced outcome extraction with more patterns"""
    # Look in the last 2000 chars where judgment usually appears
    relevant_text = text[-2000:]
    
    # Pattern 1: Appeal allowed/dismissed
    outcome_patterns = [
        r'(?:appeal|petition|complaint|writ petition)\s+(?:is\s+)?(?:allowed|dismissed|allowed in part|partly allowed|dismissed as withdrawn|dismissed as infructuous)',
        r'appeal\s+(?:succeeds|fails|stands dismissed|stands allowed)',
        r'(?:we|court)\s+(?:allow|dismiss|partly allow)\s+(?:the\s+)?(?:appeal|petition|complaint)',
        r'compensation\s+(?:of\s+)?[₹Rs\.]+\s*\d+[,\d]*(?:\s*(?:lakhs?|crores?))?',
        r'(?:allowed|dismissed)\s+with\s+costs?',
        r'no\s+order\s+as\s+to\s+costs',
        r'set\s+aside|quashed|upheld|confirmed|modified|remanded',
    ]
    
    for pattern in outcome_patterns:
        match = re.search(pattern, relevant_text, re.IGNORECASE)
        if match:
            outcome = match.group(0).strip()
            # Clean up and return
            outcome = re.sub(r'\s+', ' ', outcome)
            return outcome[:150]
    
    return None

def extract_citation_enhanced(text):
    """Extract all citation formats"""
    citations = []
    
    # Pattern 1: AIR YEAR SC/SUPREME COURT NUMBER
    pattern1 = re.finditer(r'(?:AIR|A\.I\.R\.)\s+(\d{4})\s+(?:SC|SUPREME COURT|Supreme Court)\s+(\d+)', text, re.IGNORECASE)
    for match in pattern1:
        citations.append(f"AIR {match.group(1)} SC {match.group(2)}")
    
    # Pattern 2: YEAR AIR NUMBER
    pattern2 = re.finditer(r'(\d{4})\s+AIR\s+(\d+)', text, re.IGNORECASE)
    for match in pattern2:
        citations.append(f"{match.group(1)} AIR {match.group(2)}")
    
    # Pattern 3: YEAR SCR NUMBER (Supreme Court Reports)
    pattern3 = re.finditer(r'(\d{4})\s+SCR\s+(\d+)', text, re.IGNORECASE)
    for match in pattern3:
        citations.append(f"{match.group(1)} SCR {match.group(2)}")
    
    # Pattern 4: YEAR SCC NUMBER (Supreme Court Cases)
    pattern4 = re.finditer(r'(\d{4})\s+SCC\s+(\d+)', text, re.IGNORECASE)
    for match in pattern4:
        citations.append(f"{match.group(1)} SCC {match.group(2)}")
    
    # Remove duplicates
    citations = list(set(citations))
    return "; ".join(citations[:3]) if citations else None  # Limit to 3 main citations

def extract_headnote(text):
    """Extract headnote/summary if present"""
    headnote_pattern = r'HEADNOTE:\s*\n\s*([^\n]+(?:\n[^\n]+){0,5})'
    match = re.search(headnote_pattern, text, re.IGNORECASE)
    if match:
        headnote = match.group(1).strip()
        headnote = re.sub(r'\s+', ' ', headnote)
        return headnote[:300] if len(headnote) > 300 else headnote
    return None

def extract_case_info(pdf_path, filename, year_folder):
    """Enhanced extraction function"""
    text = extract_text_from_pdf(pdf_path, max_pages=5)
    
    # Extract basic info
    case_title = extract_case_title_from_filename(filename)
    date = extract_date_from_filename(filename)
    if not date:
        date = extract_date_from_text(text)
    
    # Extract parties
    parties = extract_parties_enhanced(text)
    
    # Extract other fields
    case_type = extract_consumer_case_type(text)
    statutes = extract_statutes_enhanced(text)
    outcome = extract_outcome_enhanced(text)
    citation = extract_citation_enhanced(text)
    bench = extract_bench(text)
    headnote = extract_headnote(text)
    
    return {
        "Case Title": case_title,
        "Petitioner": parties["Petitioner"],
        "Respondent": parties["Respondent"],
        "Date of Judgment": date,
        "Bench": bench,
        "Case Type": case_type,
        "Statutes Referenced": statutes,
        "Citation": citation,
        "Outcome": outcome,
        "Headnote": headnote,
        "FullText_Sample": text[:1500]  # Increased sample size
    }

# Main execution
primary_dir = r"D:\MootCourt\supreme_court_judgments"
records = []
total_pdfs = 0
skipped = 0

print("="*70)
print("ENHANCED CASE EXTRACTION - Consumer Protection Cases")
print("="*70)
print("\nStarting extraction process...\n")

# Walk through each year folder and process all PDFs
for year_folder in sorted(os.listdir(primary_dir)):
    year_path = os.path.join(primary_dir, year_folder)
    if os.path.isdir(year_path) and year_folder.isdigit():
        print(f"📁 Processing year: {year_folder}")
        year_pdfs = 0
        
        for pdf_file in os.listdir(year_path):
            if pdf_file.endswith(".pdf") or pdf_file.endswith(".PDF"):
                total_pdfs += 1
                year_pdfs += 1
                pdf_path = os.path.join(year_path, pdf_file)
                
                try:
                    info = extract_case_info(pdf_path, pdf_file, year_folder)
                    
                    # Extract year
                    year_val = None
                    if info['Date of Judgment']:
                        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', info['Date of Judgment'])
                        if year_match:
                            year_val = int(year_match.group(0))
                    
                    if not year_val:
                        year_val = int(year_folder)
                    
                    info["Year"] = year_val
                    info["PDF_File"] = pdf_file
                    info["Folder"] = year_folder
                    
                    records.append(info)
                
                except Exception as e:
                    skipped += 1
                    print(f"  ⚠️  Error processing {pdf_file}: {str(e)}")
        
        print(f"   ✓ Processed {year_pdfs} cases from {year_folder}")

print(f"\n{'='*70}")
print("EXTRACTION SUMMARY")
print("="*70)
print(f"Total PDFs processed: {total_pdfs}")
print(f"Successful extractions: {len(records)}")
print(f"Skipped (errors): {skipped}")
print(f"Success rate: {len(records)/total_pdfs*100:.1f}%")

# Create DataFrame and save
df = pd.DataFrame(records)

# Reorder columns for better readability
column_order = ['Case Title', 'Petitioner', 'Respondent', 'Year', 'Date of Judgment',
                'Bench', 'Case Type', 'Statutes Referenced', 'Citation', 'Outcome',
                'Headnote', 'PDF_File', 'Folder', 'FullText_Sample']
df = df[column_order]

output_file = "consumer_cases_extracted.csv"
df.to_csv(output_file, index=False)
print(f"\n✅ CSV saved: {output_file} with {len(df)} rows")

# Print detailed statistics
print(f"\n{'='*70}")
print("DATA QUALITY REPORT")
print("="*70)
print(f"{'Field':<25} {'Count':>8} {'Percentage':>12}")
print("-"*70)
print(f"{'Case Title':<25} {df['Case Title'].notna().sum():>8} {df['Case Title'].notna().sum()/len(df)*100:>11.1f}%")
print(f"{'Petitioner':<25} {df['Petitioner'].notna().sum():>8} {df['Petitioner'].notna().sum()/len(df)*100:>11.1f}%")
print(f"{'Respondent':<25} {df['Respondent'].notna().sum():>8} {df['Respondent'].notna().sum()/len(df)*100:>11.1f}%")
print(f"{'Date of Judgment':<25} {df['Date of Judgment'].notna().sum():>8} {df['Date of Judgment'].notna().sum()/len(df)*100:>11.1f}%")
print(f"{'Bench':<25} {df['Bench'].notna().sum():>8} {df['Bench'].notna().sum()/len(df)*100:>11.1f}%")
print(f"{'Case Type':<25} {df['Case Type'].notna().sum():>8} {df['Case Type'].notna().sum()/len(df)*100:>11.1f}%")
print(f"{'Statutes Referenced':<25} {df['Statutes Referenced'].notna().sum():>8} {df['Statutes Referenced'].notna().sum()/len(df)*100:>11.1f}%")
print(f"{'Citation':<25} {df['Citation'].notna().sum():>8} {df['Citation'].notna().sum()/len(df)*100:>11.1f}%")
print(f"{'Outcome':<25} {df['Outcome'].notna().sum():>8} {df['Outcome'].notna().sum()/len(df)*100:>11.1f}%")
print(f"{'Headnote':<25} {df['Headnote'].notna().sum():>8} {df['Headnote'].notna().sum()/len(df)*100:>11.1f}%")

# Show case type distribution
print(f"\n{'='*70}")
print("CASE TYPE DISTRIBUTION")
print("="*70)
case_type_dist = df['Case Type'].value_counts()
for case_type, count in case_type_dist.items():
    print(f"{case_type:<40} {count:>5} ({count/len(df)*100:>5.1f}%)")

print(f"\n{'='*70}")
print("✨ Enhanced extraction complete!")
print("="*70)
