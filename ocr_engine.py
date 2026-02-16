import os
import json
import logging
from paddleocr import PaddleOCR
from pdf2image import convert_from_path, convert_from_bytes
import numpy as np
import cv2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize PaddleOCR (OCR-only mode)
# 'use_angle_cls' disabled for speed. Enable if scans are significantly rotated.
ocr = PaddleOCR(use_angle_cls=False, lang='en', enable_mkldnn=True)

# Determine Poppler Path
USER_POPPLER_BASE = r"C:\Users\HEMANTH KUMAR\Downloads\Release-25.12.0-0\poppler-25.12.0"
POTENTIAL_PATHS = [
    os.path.join(USER_POPPLER_BASE, "Library", "bin"),
    os.path.join(USER_POPPLER_BASE, "bin"),
    USER_POPPLER_BASE, # Maybe the bin files are in the root?
    os.environ.get('POPPLER_PATH', r'C:\poppler-xx\Library\bin')
]

POPPLER_PATH = None
for path in POTENTIAL_PATHS:
    if os.path.exists(path) and os.path.isdir(path):
        # fast check for pdftoppm (poppler executable)
        if os.path.exists(os.path.join(path, 'pdftoppm.exe')):
            POPPLER_PATH = path
            logging.info(f"Examples found Poppler at: {POPPLER_PATH}")
            break

if not POPPLER_PATH:
    logging.warning(f"Poppler not found in expected paths. Using default/fallback but may fail.")
    POPPLER_PATH = POTENTIAL_PATHS[0] # Fallback


def extract_contract_data(pdf_input):
    """
    Extracts text and coordinates from a PDF using OCR.
    Args:
        pdf_input: either a file path (str) or raw bytes.
    """
    try:
        # 1. Convert PDF pages to images
        if isinstance(pdf_input, bytes):
            images = convert_from_bytes(pdf_input, dpi=150, poppler_path=POPPLER_PATH, thread_count=4)
        else:
            images = convert_from_path(pdf_input, dpi=150, poppler_path=POPPLER_PATH, thread_count=4)
    except Exception as e:
        logging.error(f"Failed to convert PDF to images: {e}")
        logging.error(f"Ensure Poppler is installed and POPPLER_PATH is set correctly. Current path: {POPPLER_PATH}")
        return None
    
    document_results = []

    for i, image in enumerate(images):
        logging.info(f"Processing page {i + 1}...")
        # Convert PIL image to format PaddleOCR expects
        img_array = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 2. Run OCR Detection and Recognition
        # This returns: [ [ [coordinates], (text, confidence) ], ... ]
        try:
            result = ocr.ocr(img_array)

        
        except Exception as e:
            logging.error(f"OCR calculation threw exception: {e}")
            result = None

        page_data = []
        # Defensive check against empty results or malformed lists
        if result and isinstance(result, list) and len(result) > 0:

             if isinstance(result[0], dict):
                 # Handle new PaddleOCR dict/struct return format
                 r = result[0]
                 keys = list(r.keys()) # Convert to list for safe printing

                 
                 if 'rec_texts' in r and 'rec_boxes' in r and 'rec_scores' in r:
                     texts = r['rec_texts']
                     boxes = r['rec_boxes']
                     scores = r['rec_scores']
                     

                     
                     for i in range(len(texts)):
                         # Convert numpy types to native python types for JSON serialization
                         box = boxes[i]
                         if hasattr(box, 'tolist'):
                             box = box.tolist()
                         
                         score = scores[i]
                         if hasattr(score, 'item'):
                             score = score.item()
                         elif hasattr(score, 'tolist'):
                             score = score.tolist()
                         else:
                             score = float(score)

                         page_data.append({
                             "text": texts[i],
                             "box": box,
                             "score": score
                         })
                 else:

                     logging.warning(f"Result[0] is dict but missing expected keys: {keys}")

             elif isinstance(result[0], list):
                 # Handle legacy list-of-lines return format
                 for line in result[0]:
                    try:
                        coords = line[0]
                        text = line[1][0]
                        conf = line[1][1]
                        
                        page_data.append({
                            "text": text,
                            "box": coords,
                            "score": conf
                        })
                    except Exception as line_e:
                        logging.warning(f"Skipping malformed line: {line} - Error: {line_e}")
             else:
                 logging.warning(f"Result[0] is unexpected type: {type(result[0])}")
        else:
            logging.info(f"No text detected or empty result on page {i+1}")
        
        document_results.append({
            "page": i + 1,
            "lines": page_data
        })
        
    return document_results

def process_directory(input_dir, output_dir):
    """
    Process all PDF files in the input directory and save OCR results to output directory.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created output directory: {output_dir}")

    files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if not files:
        logging.warning(f"No PDF files found in {input_dir}")
        return

    for file in files:
        pdf_path = os.path.join(input_dir, file)
        
        # Check if output already exists
        output_filename = f"{os.path.splitext(file)[0]}_ocr.json"
        output_path = os.path.join(output_dir, output_filename)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            logging.info(f"Skipping OCR for {file} (Output exists: {output_filename})")
            continue

        logging.info(f"Starting OCR on {file}...")
        
        ocr_result = extract_contract_data(pdf_path)
        
        if ocr_result:
            output_filename = f"{os.path.splitext(file)[0]}_ocr.json"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, "w") as f:
                json.dump(ocr_result, f, indent=4)
            logging.info(f"Success! Data saved to {output_path}")
        else:
            logging.error(f"Failed to process {file}")

if __name__ == "__main__":
    # Default paths for standalone execution
    INPUT_DIR = "input_docs"
    OUTPUT_DIR = "output_data"
    
    if os.path.exists(INPUT_DIR):
        process_directory(INPUT_DIR, OUTPUT_DIR)
    else:
        logging.error(f"Input directory '{INPUT_DIR}' not found.")