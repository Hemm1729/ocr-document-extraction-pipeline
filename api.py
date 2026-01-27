import os
import logging
import json
import sys
from typing import List, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure we can import from local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_engine import extract_contract_data
from extract_info import get_llm_extraction, parse_ocr_text
from db import DatabaseManager
from vin_service import lookup_vin

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="Document Extraction API", 
    description="API for OCR and LLM extraction of documents using SQLite storage."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize Database
db = DatabaseManager()

@app.post("/process")
async def process_document(file: UploadFile = File(...)):
    """
    Upload a PDF, run OCR and LLM extraction, save to DB, and return results.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    logging.info(f"Processing file: {file.filename}")
    
    try:
        # Read file content
        file_bytes = await file.read()
        
        # 1. ORC
        logging.info("Starting OCR...")
        ocr_result = extract_contract_data(file_bytes)
        if not ocr_result:
             raise HTTPException(status_code=500, detail="OCR failed to extract data")
        
        # 2. Parse Text
        text_content = parse_ocr_text(ocr_result)
        
        # 3. LLM Extraction
        logging.info("Starting LLM Extraction...")
        extracted_info = get_llm_extraction(text_content)

        # 4. VIN Lookup
        if "VIN" in extracted_info and extracted_info["VIN"] != "Not Found":
            vin_details = lookup_vin(extracted_info["VIN"])
            if vin_details:
                extracted_info["vin_details"] = vin_details
        
        # 5. Save to DB
        doc_id = db.insert_document(file.filename, ocr_result, extracted_info)
        
        return {
            "id": doc_id,
            "filename": file.filename,
            "extraction": extracted_info
        }

    except Exception as e:
        logging.error(f"Error processing {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/results/{doc_id}")
def get_result(doc_id: int):
    """Retrieve extraction results by ID."""
    doc = db.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return doc

@app.get("/documents")
def list_documents():
    """List all processed documents."""
    return db.list_documents()

@app.delete("/documents/{doc_id}")
def delete_document(doc_id: int):
    """Delete a document."""
    success = db.delete_document(doc_id)
    if not success:
         raise HTTPException(status_code=404, detail="Document not found or could not be deleted")
    return {"message": "Document deleted"}

if __name__ == "__main__":
    import uvicorn
    # Disable PaddleOCR model check to speed up startup
    os.environ["DISABLE_MODEL_SOURCE_CHECK"] = "True"
    
    print("\n" + "="*50)
    print("Server is starting (Database Mode)!")
    print("Access the API at: http://localhost:8000")
    print("API Docs at: http://localhost:8000/docs")
    print("="*50 + "\n")

    uvicorn.run(app, host="127.0.0.1", port=8000)