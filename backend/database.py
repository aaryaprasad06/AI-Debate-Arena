import logging
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from google.cloud import firestore
from backend import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File name for local JSON fallback database
LOCAL_DB_FILE = "debate_history.json"

# Initialize Firestore Client if credentials are configured
_db = None
if config.is_firestore_configured():
    try:
        # If running in Cloud Run, it utilizes implicit credentials automatically.
        # Otherwise, if local, it will pick up GOOGLE_APPLICATION_CREDENTIALS if set.
        if config.GOOGLE_APPLICATION_CREDENTIALS:
            _db = firestore.Client.from_service_account_json(config.GOOGLE_APPLICATION_CREDENTIALS)
        elif config.FIREBASE_PROJECT_ID:
            _db = firestore.Client(project=config.FIREBASE_PROJECT_ID)
        else:
            _db = firestore.Client()
        logger.info("Firebase Firestore database client initialized successfully.")
    except Exception as e:
        logger.error(f"Firestore initialization failed: {e}. Falling back to local storage.")
else:
    logger.warning("Firestore credentials not configured. Local JSON file storage will be used.")

def save_debate(debate_data: Dict[str, Any]) -> bool:
    """
    Saves a completed debate record to Firebase Firestore.
    Falls back to a local JSON file if Firestore is not initialized or accessible.
    """
    # Augment debate data with timestamp
    record = debate_data.copy()
    record["timestamp"] = datetime.utcnow().isoformat()
    
    # Attempt to write to Firestore
    if _db is not None:
        try:
            logger.info("Saving debate record to Firestore...")
            # We save in a collection called "debates"
            doc_ref = _db.collection("debates").document()
            doc_ref.set(record)
            logger.info(f"Debate record successfully saved to Firestore (ID: {doc_ref.id}).")
            return True
        except Exception as e:
            logger.error(f"Failed to save debate to Firestore: {e}. Attempting local fallback.")
            
    # Fallback: Save to local JSON
    return _save_to_local_db(record)

def get_debate_history() -> List[Dict[str, Any]]:
    """
    Retrieves all past debate records from Firestore, ordered by newest first.
    Falls back to the local JSON storage if Firestore is not initialized.
    """
    if _db is not None:
        try:
            logger.info("Fetching debate history from Firestore...")
            debates_ref = _db.collection("debates")
            # Order by timestamp descending
            query = debates_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(50)
            docs = query.stream()
            
            history = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                history.append(data)
                
            logger.info(f"Retrieved {len(history)} debate records from Firestore.")
            return history
        except Exception as e:
            logger.error(f"Failed to fetch debate history from Firestore: {e}. Reading from local fallback.")
            
    # Fallback: Read from local JSON
    return _get_from_local_db()

# --- Private Helper Methods for Local Fallback Storage ---

def _save_to_local_db(record: Dict[str, Any]) -> bool:
    try:
        history = _get_from_local_db()
        history.insert(0, record)  # Add new record at the top (newest first)
        
        with open(LOCAL_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Debate record successfully saved to local storage file '{LOCAL_DB_FILE}'.")
        return True
    except Exception as e:
        logger.error(f"Failed to save debate to local storage file: {e}")
        return False

def _get_from_local_db() -> List[Dict[str, Any]]:
    if not os.path.exists(LOCAL_DB_FILE):
        return []
    try:
        with open(LOCAL_DB_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
            if not isinstance(history, list):
                return []
            return history
    except Exception as e:
        logger.error(f"Failed to read local storage file: {e}")
        return []
