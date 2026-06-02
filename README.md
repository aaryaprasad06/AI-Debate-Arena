# AI Debate Arena ⚖️

An elite multi-agent debate platform built in Python. The system simulates structured debates between opposing AI agents and utilizes a balanced AI Referee (Judge) to grade arguments and declare a winner, all streaming live through a premium glassmorphic web interface.

---

## 🏛️ Technology Stack

* **Frontend:** [Gradio](https://www.gradio.app/) with customized modern dark glassmorphic layout and live-streaming progress steps.
* **Backend Core:** Python 3.11+ modular services.
* **AI Orchestrator:** **Gemini 2.5 Flash** (leveraging the official `google-genai` SDK) running distinct system persona instructions (Pro Agent, Against Agent, Judge Agent).
* **Database:** **Firebase Firestore** to log debate histories, transcripts, scores, and winner standings. (Falls back automatically to a local JSON file if credentials are omitted, for instant zero-friction developer setups!)
* **Cloud Infrastructure:** **Google Cloud Run** for containerized serverless hosting.

---

## 🏗️ Folder Structure

```text
AI-Debate-Arena/
├── backend/
│   ├── __init__.py
│   ├── config.py           # Handles env settings & client initializations
│   ├── database.py         # Firestore connectors with local JSON file fallback
│   └── services/
│       ├── __init__.py
│       ├── debate_service.py # Round-robin multi-agent generator & streaming workflow
│       └── gemini_service.py # Gemini 2.5 API wrapper with mock capabilities
├── app.py                  # Gradio UI client entrypoint and custom design layout
├── requirements.txt        # Python external dependencies declaration
├── Dockerfile              # Production-optimized container build
├── .env.template           # Template detailing necessary keys
└── .gitignore              # Python source version controls
```

---

## 🚀 Quick Start (Local Run)

### 1. Set Up Virtual Environment

Open your terminal in the project root directory:

```bash
# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Credentials

Create a `.env` file in the root folder and copy variables from `.env.template`:

```env
PORT=8080
GEMINI_API_KEY=your_actual_gemini_api_key

# Optional (If using Firebase Firestore locally):
GOOGLE_APPLICATION_CREDENTIALS=path_to_your_firebase_key.json
FIREBASE_PROJECT_ID=your_firebase_project_id
```

> [!NOTE]
> If `GEMINI_API_KEY` is not supplied, the application will boot in **Mock Demonstration Mode** featuring structured static answers, allowing you to test the UI layout without charges.
> If `GOOGLE_APPLICATION_CREDENTIALS` is omitted, the app will log to a local file called `debate_history.json` and read history from there seamlessly.

### 4. Boot the Server

```bash
python app.py
```

Open `http://localhost:8080/` in your browser to experience the Arena!

---

## ☁️ Deploying to Google Cloud Run

To containerize and launch on Google Cloud Run serverless hosting:

### 1. Build and Submit Container to Google Artifact Registry

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ai-debate-arena
```

### 2. Deploy Container to Cloud Run

```bash
gcloud run deploy ai-debate-arena \
    --image gcr.io/YOUR_PROJECT_ID/ai-debate-arena \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars="GEMINI_API_KEY=your_gemini_api_key"
```

*Note: For database access on Cloud Run, ensure the Cloud Run service account has the **Cloud Datastore User** (Firestore) permission enabled in the Google Cloud Console. Cloud Run will automatically bind to the default credentials without requiring local service key JSON configurations!*
