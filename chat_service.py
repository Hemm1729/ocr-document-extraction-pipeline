import logging
import json
import ollama
from db import DatabaseManager
from extract_info import parse_ocr_text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def chat_with_document(doc_id: int, message: str, history: list) -> dict:
    """
    Chat with a specific document user Ollama.
    
    Args:
        doc_id: The ID of the document to chat with.
        message: The user's current message.
        history: A list of previous messages [{"role": "user", "content": "..."}, ...].
        
    Returns:
        dict: The response from the LLM.
    """
    db = DatabaseManager()
    doc = db.get_document(doc_id)
    
    if not doc:
        return {"error": "Document not found"}
        
    # Get document text
    ocr_data = doc.get('ocr_data')
    if not ocr_data:
        return {"error": "No OCR data found for this document"}
        
    document_text = parse_ocr_text(ocr_data)
    
    # Construct the system prompt with context
    system_prompt = f"""
    You are an expert contract negotiation assistant. A user is asking questions about the following contract.
    
    Contract Text:
    {document_text}
    
    Instructions:
    1. Answer the user's question based STRICTLY on the contract text provided.
    2. If the answer is not in the contract, say so.
    3. Provide helpful advice for negotiation if relevant (e.g., if a term is standard or unusual).
    4. Keep answers concise but informative.
    5. You are speaking to the user who is reviewing this contract.
    """
    
    # Prepare messages for Ollama
    messages = [{'role': 'system', 'content': system_prompt}]
    
    # Add history (ensure strictly user/assistant roles)
    for msg in history:
        role = msg.get('role')
        content = msg.get('content')
        if role in ['user', 'assistant'] and content:
            messages.append({'role': role, 'content': content})
            
    # Add current message
    messages.append({'role': 'user', 'content': message})
    
    try:
        logging.info(f"Sending chat request to Ollama for doc {doc_id}...")
        response = ollama.chat(model='llama3.2', messages=messages)
        return {"role": "assistant", "content": response['message']['content']}
    except Exception as e:
        logging.error(f"Ollama chat failed: {e}")
        return {"error": str(e)}
