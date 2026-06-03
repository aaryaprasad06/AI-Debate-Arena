# ⚖️ AI Debate Arena

An advanced multi-agent debate platform built with Python that enables intelligent, structured debates between opposing AI participants. A neutral AI Judge evaluates each side's arguments, assigns scores, and determines the winner. The entire debate unfolds in real time through a sleek, glassmorphic web interface with live progress updates.

---

## 🛠️ Core Technologies

### Frontend

* **Gradio** framework with a modern dark-themed glassmorphic design.
* Real-time debate streaming and interactive progress visualization.

### Backend

* Python 3.11+ with a modular service-oriented architecture.

### AI Engine

* Powered by **Gemini 2.5 Flash** using the official `google-genai` SDK.
* Separate AI personas:

  * **Supporting Agent**
  * **Opposing Agent**
  * **Judge Agent**

### Data Storage

* **Firebase Firestore** for storing debate transcripts, scores, winners, and historical records.
* Automatic fallback to a local JSON database when Firebase credentials are unavailable, allowing immediate development without cloud setup.

### Deployment Platform

* Containerized and hosted using **Google Cloud Run** for scalable serverless execution.

---

## 📁 Project Structure

```text
AI-Debate-Arena/
├── backend/
│   ├── __init__.py
│   ├── config.py             # Environment variables and client setup
│   ├── database.py           # Firestore integration with JSON fallback
│   └── services/
│       ├── __init__.py
│       ├── debate_service.py # Debate workflow and streaming logic
│       └── gemini_service.py # Gemini API integration and mock support
├── app.py                    # Main Gradio application entry point
├── requirements.txt          # Project dependencies
├── Dockerfile                # Container build configuration
├── .env.template             # Environment variable template
└── .gitignore                # Git exclusion rules
```

---

## 🚀 Running the Application Locally

### Step 1: Create a Virtual Environment

Navigate to the project root directory and execute:

```bash
# Create virtual environment
python -m venv venv

# Activate environment

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 2: Install Required Packages

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file and populate it using the values from `.env.template`:

```env
PORT=8080
GEMINI_API_KEY=your_gemini_api_key

# Optional Firestore Configuration
GOOGLE_APPLICATION_CREDENTIALS=path/to/firebase-key.json
FIREBASE_PROJECT_ID=your_project_id
```

### Development Notes

* If no **GEMINI_API_KEY** is provided, the application launches in **Mock Demo Mode**, generating predefined responses for testing and UI validation.
* If Firebase credentials are not configured, all debate data is automatically stored in a local file named `debate_history.json`.

### Step 4: Launch the Application

```bash
python app.py
```

Once started, open the following URL in your browser:

```text
http://localhost:8080/
```

---

## ☁️ Deployment on Google Cloud Run

### Build and Upload the Container

```bash
gcloud builds submit \
    --tag gcr.io/YOUR_PROJECT_ID/ai-debate-arena
```

### Deploy to Cloud Run

```bash
gcloud run deploy ai-debate-arena \
    --image gcr.io/YOUR_PROJECT_ID/ai-debate-arena \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars="GEMINI_API_KEY=your_gemini_api_key"
```

### Firestore Access Configuration

For production deployments using Firestore, ensure that the Cloud Run service account has the **Cloud Datastore User** role assigned within Google Cloud IAM.

When deployed on Cloud Run, the application automatically uses the platform's default service account credentials, eliminating the need to upload or manage Firebase key files manually.

---

## ✨ Key Features

* Live AI-versus-AI debates
* Independent Pro and Con agents
* Neutral AI judging and scoring system
* Real-time streaming updates
* Modern glassmorphic user interface
* Firebase Firestore integration
* Automatic local storage fallback
* Mock mode for cost-free testing
* Container-ready deployment
* Serverless scaling with Google Cloud Run
