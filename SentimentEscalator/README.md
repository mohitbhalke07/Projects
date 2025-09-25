# 🧠 Sentiment Analysis API (FastAPI + Hugging Face)

This project provides a **REST API built with FastAPI** for analyzing sentiment of customer support tickets.  
The system uses **Hugging Face’s pre-trained model** (`cardiffnlp/twitter-roberta-base-sentiment`) via API inference, making it easy to integrate into any language or platform (PHP, Node, Python, etc.).

---

## 🚀 Features
- Exposes a **POST API** (`/analyze`) to analyze sentiment of a text.
- Returns **sentiment scores** (positive, negative, neutral).
- Supports a **threshold mechanism** → triggers `escalate=True` if negative sentiment > threshold.
- Logs every request & response (console + rotating log file).
- Secure with a simple **API Key validation**.
- Ready for **integration with CRM / ticketing systems**.

---

## 🛠️ Tech Stack
- [FastAPI](https://fastapi.tiangolo.com/) – high-performance Python API framework
- [Hugging Face Inference API](https://huggingface.co/inference-api) – pre-trained sentiment model
- [Python Logging](https://docs.python.org/3/library/logging.html) – rotating log file handler
- [Pydantic](https://docs.pydantic.dev/) – request/response validation

---

## 📂 Project Structure

sentiment-endpoint/
├── app/
│ └── main.py # FastAPI main application
├── logs/
│ └── app.log # API logs (auto-created)
├── .env # Environment variables
├── requirements.txt # Dependencies
└── README.md # Documentation