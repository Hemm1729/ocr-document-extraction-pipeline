# Task 2: LLM-based Document Extraction

This project is a clone of Task 1 but replaces the Regex-based extraction with an LLM-based approach (using Google Gemini).

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set API Key**:
    You need a Google Gemini API Key. Set it as an environment variable:
    
    **Windows (PowerShell)**:
    ```powershell
    $env:GOOGLE_API_KEY = "your_api_key_here"
    ```
    
    **Windows (CMD)**:
    ```cmd
    set GOOGLE_API_KEY=your_api_key_here
    ```

3.  **Run the Pipeline**:
    ```bash
    python main.py
    ```

## Structure
-   `input_docs/`: Place PDF files here.
-   `output_data/`: OCR results and extracted JSONs will appear here.
-   `ocr_engine.py`: Handles PDF-to-Image and OCR (PaddleOCR).
-   `extract_info.py`: Sends OCR text to the LLM for extraction.
-   `main.py`: Orchestrates the flow.

## Notes
-   The extraction logic uses `gemini-1.5-flash` model. You can change this in `extract_info.py`.
-   If you don't have an API key, the script will log an error.
