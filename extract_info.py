import json
import os
import logging

import time


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False
    logging.warning("ollama library not installed. Please install it with: pip install ollama")

def get_llm_extraction(text):
    if not HAS_OLLAMA:
        return {"Error": "ollama library not found"}

    
    prompt = f"""
    You are an expert document extraction AI. Your task is to extract specific financial and vehicle details from the provided OCR text of a contract.
    Please extract the following fields exactly:
    1. APR (Annual Percentage Rate) - Look for "Annual Percentage Rate" or similar.
    2. Finance_Charge - The dollar amount of the finance charge.
    3. Amount_Financed - The amount financed.
    4. Total_Sale_Price - The total sale price.
    5. VIN - The 17-character Vehicle Identification Number.
    6. Monthly_Payment - The amount of the monthly payment/installment.
    7. Graduation_Date - Expected Graduation Date (if present).
    
    you will definitely find the above values in the documents.. so deep search for the values and fill them instead of returning not found. I repeat never return NOT FOUND for any variable in any documnt.. search the whole document you will find it

    Output format:
    Return ONLY a valid JSON object. Do not include any explanation or markdown code blocks (no ```json).
    Keys: "APR", "Finance_Charge", "Amount_Financed", "Total_Sale_Price", "VIN", "Monthly_Payment", "Graduation_Date".
    If a value is not found, set it to "Not Found".
    
    Document Text:
    {text}
    """
    
    try:
        response = ollama.chat(model='llama3.2', messages=[
            {'role': 'user', 'content': prompt},
        ], format='json')
        
        response_text = response['message']['content'].strip()

        
        return json.loads(response_text)
    except Exception as e:

        logging.error(f"LLM Extraction failed: {e}")
        return {"Error": str(e)}

def parse_ocr_text(ocr_data):
    full_text = ""
    for page in ocr_data:
        if 'lines' in page:
            for entry in page['lines']:
                if 'text' in entry:
                    full_text += entry['text'] + " "
    return full_text

def process_extraction(output_dir):
    if not os.path.exists(output_dir):
        logging.error(f"Output directory {output_dir} does not exist.")
        return

    json_files = [f for f in os.listdir(output_dir) if f.endswith('_ocr.json')]
    
    if not json_files:
        logging.warning(f"No OCR results found in {output_dir}")
        return

    all_results = {}
    
    for file in json_files:
        logging.info(f"Extracting info from {file} using Ollama...")
        
        try:
            with open(os.path.join(output_dir, file), 'r') as f:
                data = json.load(f)
            

            text_content = parse_ocr_text(data)
            

            try:
                extracted_info = get_llm_extraction(text_content)
            except Exception as e:
                 logging.error(f"Ollama call failed: {e}")
                 extracted_info = {"Error": f"Ollama failed. Is Ollama running? Did you run 'ollama pull llama3.2'? Error: {e}"}


            original_name = file.replace('_ocr.json', '.pdf')
            all_results[original_name] = extracted_info
            

            logging.info(f"Finished {file}.")
            
        except Exception as e:
            logging.error(f"Error processing {file}: {e}")
            
    # Save consolidated results
    summary_path = os.path.join(output_dir, "consolidated_results_llm.json")
    with open(summary_path, 'w') as f:
        json.dump(all_results, f, indent=4)
    
    logging.info(f"Extraction complete! Results saved to {summary_path}")

if __name__ == "__main__":
    OUTPUT_DIR = "output_data"
    process_extraction(OUTPUT_DIR)
