import json
import os
import logging




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
    8. Fair_Price - The fair price which that you suggest for the vehicle based on all the detailes extracted.
    
    Additionally, analyze the FAIRNESS of the contract terms:
    9. "fairness_score": A score from 0-100 (100 being most fair to the consumer).
    10. "red_flags": A list of strings describing any unfair, predatory, or suspicious terms. IMPORTANT: You MUST include the specific values found in the text (e.g. 'Late charge of 5%' instead of just 'Late charge of %', or 'Prepayment penalty of $50'). Do NOT use placeholders.
    11. "green_flags": A list of strings describing consumer-friendly terms (e.g. low APR, no prepayment penalty, clear disclosures).
    12. "summary": A brief 1-2 sentence summary of the contract fairness.
    
    you will definitely find the above values in the documents.. so deep search for the values and fill them instead of returning not found. I repeat never return NOT FOUND for any variable in any documnt.. search the whole document you will find it

    Output format:
    Return ONLY a valid JSON object. No markdown.
    Result:
    Keys: "APR", "Finance_Charge", "Amount_Financed", "Total_Sale_Price", "VIN", "Monthly_Payment", "Graduation_Date", "Fair_Price", "fairness_score", "red_flags", "green_flags", "summary".
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


