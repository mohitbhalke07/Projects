import os
import json
import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import Dict
from datetime import datetime
import requests
from dotenv import load_dotenv

# -------------------
# Config (from .env or defaults)
# -------------------

load_dotenv()

API_KEY = os.environ.get("API_KEY")         # Key to validate the api invoker
HF_API_KEY = os.environ.get("HF_API_KEY")
MODEL_NAME = os.environ.get("MODEL_NAME")
LOG_DIR = os.environ.get("LOG_DIR", "./logs")
LOG_FILE = os.path.join(LOG_DIR, "api.log")

if not all([API_KEY, HF_API_KEY, MODEL_NAME]):
    raise ValueError("API_KEY, HF_API_KEY, and MODEL_NAME must be set in environment or .env")

os.makedirs(LOG_DIR, exist_ok=True)

# -------------------
# Logging setup (console + file)
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

app = FastAPI(title="Sentiment Escalation API (HF API version)")

# -------------------
# Schemas
# -------------------
class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    threshold: float = Field(0.8, ge=0.0, le=1.0)

class AnalyzeResponse(BaseModel):
    text: str = Field(..., description="Original text submitted for analysis.")
    scores: Dict[str, float] = Field(..., description="Sentiment scores for the text.")
    escalate: bool = Field(..., description="Indicates if escalation is required.")
    threshold: float = Field(..., description="Threshold used for determining escalation.")
    model_name: str = Field(..., description="Name of the Hugging Face model used.")
    timestamp: str = Field(..., description="UTC timestamp (ISO 8601) when analysis was done.")

# -------------------
# Auth dependency
# -------------------
def validate_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        logger.warning("Invalid API key")
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True

# -------------------
# Hugging Face Inference API call
# -------------------
def call_hf_api(text: str):
    url = f"https://api-inference.huggingface.co/models/{MODEL_NAME}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": text}

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    try:
        resp_json = response.json()
        logger.info("HF API Response: status=%d, body=%s", response.status_code, json.dumps(resp_json, indent=2))
    except ValueError:
        # Response is not JSON
        logger.info("HF API Response: status=%d, body=%s", response.status_code, response.text)

    if response.status_code != 200:
        logger.error("HF API error: %s - %s", response.status_code, response.text)
        raise HTTPException(status_code=500, detail="Error calling Hugging Face API")
    
    data = response.json()
    # cardiffnlp/twitter-roberta-base-sentiment returns list of list of dicts
    # Example: [[{"label": "LABEL_0", "score": 0.98}, {"label": "LABEL_1", "score":0.01}, ...]]
    try:
        probs = data[0]
        LABEL_MAPPING = {"label_0": "negative", "label_1": "neutral", "label_2": "positive"}
        scores = {LABEL_MAPPING.get(item["label"].lower(), item["label"].lower()): float(item["score"]) for item in probs}
        return scores
    except Exception as e:
        logger.exception("Unexpected HF API response: %s", data)
        raise HTTPException(status_code=500, detail="Invalid HF API response")

# -------------------
# API endpoints
# -------------------

# In production we’re consuming a pre-trained Hugging Face model via their inference API, so hyperparameter tuning isn’t part of this API call. However, if we fine-tune the model on our ticket/query dataset, we’d perform hyperparameter tuning — adjusting parameters like learning rate, batch size, and epochs — to maximize performance before deployment.

@app.post("/analyze", response_model=AnalyzeResponse, dependencies=[Depends(validate_api_key)])
def analyze(req: AnalyzeRequest):
    logger.info("Request received: text_length=%d", len(req.text))

    scores = call_hf_api(req.text)
    negative_score = scores.get("negative", 0.0)
    escalate = negative_score > req.threshold

    resp = AnalyzeResponse(
        text=req.text,
        scores=scores,
        escalate=escalate,
        threshold=req.threshold,
        model_name=MODEL_NAME,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )

    logger.info("Response: %s", resp.json())
    return resp

@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME, "using": "huggingface-api"}
