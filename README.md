# Document Extraction & Chat App

## Prerequisites
- Python 3.8+
- Flutter SDK
- Ollama (running locally with `llama3.2` model)

## Setup

### 1. Backend (Python)
Navigate to the root directory.

```bash
# Create and activate virtual environment (if not already done)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend (Flutter)
Navigate to the frontend directory.

```bash
cd frontend_flutter
flutter pub get
```

## Running the Application

### 1. Start Support Services
Ensure Ollama is running:
```bash
ollama serve
# In a separate terminal, pull the model if you haven't:
ollama pull llama3.2
```

### 2. Start Backend Server
From the root directory:

```bash
.\venv\Scripts\activate
python api.py
```
 The server will start at `http://127.0.0.1:8000`.

### 3. Start Frontend App
From the `frontend_flutter` directory:

```bash
cd frontend_flutter
flutter run -d windows
```
