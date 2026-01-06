import os
import logging
from ocr_engine import process_directory
from extract_info import process_extraction

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Define directories
    INPUT_DIR = "input_docs"
    OUTPUT_DIR = "output_data"

    logging.info("Starting Document Extraction Pipeline...")

    # Ensure input directory exists
    if not os.path.exists(INPUT_DIR):
        logging.error(f"Input directory '{INPUT_DIR}' not found. Please create it and add PDF files.")
        return

    # Step 1: Run OCR
    logging.info("Step 1: Running OCR on documents...")
    try:
        process_directory(INPUT_DIR, OUTPUT_DIR)
    except Exception as e:
        logging.error(f"OCR process failed: {e}")
        return

    # Step 2: Extract Information
    logging.info("Step 2: Extracting information from OCR results...")
    try:
        process_extraction(OUTPUT_DIR)
    except Exception as e:
        logging.error(f"Extraction process failed: {e}")
        return

    logging.info("Pipeline completed successfully. Check 'output_data' for results.")

if __name__ == "__main__":
    main()
