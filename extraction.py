import pymupdf as fitz  # PyMuPDF
import re
import json
import logging
import os
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directories
INPUT_DIR = "input"
OUTPUT_FILE = "data/docs.json"

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# Regex patterns for headings/subheadings (optional fallback)
heading_pattern = re.compile(r'^\d+\.\d+(\s|$)')  # Matches "1.3" format

all_data = {}

def extract_from_pdf(pdf_path):
    logger.info(f"Processing {pdf_path}...")
    data = {}
    current_heading = None
    
    try:
        doc = fitz.open(pdf_path)
        logger.info(f"Successfully opened {pdf_path} with {len(doc)} pages")
    except Exception as e:
        logger.error(f"Error opening PDF {pdf_path}: {e}")
        return {}

    # 1. Analyze font sizes to determine body text vs headings
    font_sizes = []
    sample_pages = min(50, len(doc))

    for i in range(sample_pages):
        page = doc[i]
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        text = s["text"].strip()
                        if text:
                            font_sizes.append(s["size"])

    if not font_sizes:
        logger.warning(f"No text found in {pdf_path}. Skipping.")
        return {}

    # Determine body font size
    rounded_sizes = [round(s, 1) for s in font_sizes]
    size_counts = Counter(rounded_sizes)
    body_font_size = size_counts.most_common(1)[0][0]
    
    # Threshold: Headings should be significantly larger than body text
    heading_threshold = body_font_size + 5.0 # Adjusted threshold
    
    logger.info(f"Detected body font size: {body_font_size}, Heading threshold: {heading_threshold}")

    # 2. Extract content
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    line_text_parts = []
                    max_size = 0
                    
                    for s in l["spans"]:
                        line_text_parts.append(s["text"])
                        if s["size"] > max_size:
                            max_size = s["size"]
                    
                    text = "".join(line_text_parts).strip()
                    if not text:
                        continue

                    # Detect Heading (Size based)
                    if max_size >= heading_threshold:
                        title = text
                        # Ensure unique keys
                        count = 2
                        original_title = title
                        while title in data:
                            title = f"{original_title} ({count})"
                            count += 1
                        
                        current_heading = title
                        data[current_heading] = {
                            "title": text,
                            "source": os.path.basename(pdf_path),
                            "content": [],
                            "subsections": {}
                        }
                        # logger.info(f"Found Heading: {text}")

                    # Content
                    else:
                        if current_heading:
                            data[current_heading]["content"].append(text)
                        else:
                            # Optional: Capture preamble text
                            pass

    # Cleanup: join lists into strings
    for h, hdata in data.items():
        hdata["content"] = " ".join(hdata["content"])
        
    return data

# Main processing loop
if not os.path.exists(INPUT_DIR):
    logger.error(f"Input directory '{INPUT_DIR}' does not exist.")
    exit(1)

pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]

if not pdf_files:
    logger.warning(f"No PDF files found in {INPUT_DIR}")
else:
    for pdf_file in pdf_files:
        pdf_path = os.path.join(INPUT_DIR, pdf_file)
        file_data = extract_from_pdf(pdf_path)
        
        # Merge into main dictionary, ensuring unique keys across files
        for key, value in file_data.items():
            final_key = key
            count = 2
            while final_key in all_data:
                final_key = f"{key} ({count})"
                count += 1
            all_data[final_key] = value

    # Save JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

    logger.info(f"Extraction complete. Processed {len(pdf_files)} files. Saved to {OUTPUT_FILE}. Found {len(all_data)} total headings.")



