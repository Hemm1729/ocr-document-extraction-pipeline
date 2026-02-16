import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_chat():
    print("1. Listing documents...")
    try:
        resp = requests.get(f"{BASE_URL}/documents")
        if resp.status_code != 200:
            print("Failed to list documents")
            return
        
        docs = resp.json()
        if not docs:
            print("No documents found. Please upload one first via the app or curl.")
            return
            
        doc_id = docs[0]['id']
        filename = docs[0]['filename']
        print(f"   Using document ID: {doc_id} ({filename})")
        
        print("\n2. Sending chat message...")
        payload = {
            "doc_id": doc_id,
            "message": "What is the monthly payment?",
            "history": []
        }
        
        start = time.time()
        chat_resp = requests.post(f"{BASE_URL}/chat", json=payload)
        duration = time.time() - start
        
        if chat_resp.status_code == 200:
            print(f"   Success! (took {duration:.2f}s)")
            print(f"   Response: {chat_resp.json()['content']}")
        else:
            print(f"   Failed: {chat_resp.text}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Wait a bit for server to start if running immediately after
    time.sleep(2)
    test_chat()
