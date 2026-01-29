import os
import json
import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import Dict
from datetime import datetime
from dotenv import load_dotenv

from transformers import pipeline

# -------------------
# Config
# -------------------

load_dotenv()

API_KEY = os.environ.get("API_KEY")   # API auth
# MODEL_PATH = os.environ.get(
#     "MODEL_PATH",
#     "./model/sentiment_roberta_finetuned" 
# )
MODEL_PATH = os.environ.get(
    "MODEL_PATH",
    "cardiffnlp/twitter-roberta-base-sentiment-latest"
)

LOG_DIR = os.environ.get("LOG_DIR", "./logs")
LOG_FILE = os.path.join(LOG_DIR, "api.log")

if not API_KEY:
    raise ValueError("API_KEY must be set in environment or .env")

os.makedirs(LOG_DIR, exist_ok=True)

# -------------------
# Logging setup
# -------------------

logger = logging.getLogger("sentiment-endpoint")
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(LOG_FILE, maxBytes=2*1024*1024, backupCount=3)
console_handler = logging.StreamHandler()

fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(fmt)
console_handler.setFormatter(fmt)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# -------------------
# Load fine-tuned model ONCE
# -------------------

logger.info("Loading fine-tuned sentiment model from %s", MODEL_PATH)

# sentiment_pipeline = pipeline(
#     task="text-classification",
#     model=MODEL_PATH,
#     top_k=None
# )
sentiment_pipeline = pipeline(
    task="text-classification",
    model=MODEL_PATH,
    top_k=None
)

logger.info("Model loaded successfully")

app = FastAPI(title="Sentiment Escalation API (Fine-tuned model)")

# -------------------
# Schemas
# -------------------

class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    threshold: float = Field(0.8, ge=0.0, le=1.0)

class AnalyzeResponse(BaseModel):
    text: str
    scores: Dict[str, float]
    escalate: bool
    threshold: float
    model_name: str
    timestamp: str

# -------------------
# Auth dependency
# -------------------

def validate_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        logger.warning("Invalid API key")
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True

# -------------------
# Local model inference
# -------------------

# def run_model(text: str):
#     """
#     Converts pipeline output into the same score format
#     you were returning earlier.
#     """
#     outputs = sentiment_pipeline(text, top_k=None)

#     # pipeline returns list of dicts
#     scores = {
#         item["label"].lower(): float(item["score"])
#         for item in outputs
#     }

#     return scores

def run_model(text: str):
    outputs = sentiment_pipeline(text)

    # v5 can return List[Dict] OR List[List[Dict]]
    results = outputs[0] if isinstance(outputs[0], list) else outputs

    scores = {}

    for item in results:
        label = item["label"].lower()
        scores[label] = float(item["score"])

    return scores



# -------------------
# API endpoints
# -------------------

@app.post(
    "/analyze",
    response_model=AnalyzeResponse,
    dependencies=[Depends(validate_api_key)]
)
def analyze(req: AnalyzeRequest):
    logger.info("Request received: text_length=%d", len(req.text))

    scores = run_model(req.text)
    negative_score = scores.get("negative", 0.0)
    escalate = negative_score > req.threshold

    response = AnalyzeResponse(
        text=req.text,
        scores=scores,
        escalate=escalate,
        threshold=req.threshold,
        model_name=os.path.basename(MODEL_PATH),
        timestamp=datetime.utcnow().isoformat() + "Z"
    )

    logger.info("Response: %s", response.json())
    return response

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": os.path.basename(MODEL_PATH),
        "using": "local-finetuned-model"
    }
