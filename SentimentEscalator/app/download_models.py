from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODELS = {
    "roberta_twitter": "cardiffnlp/twitter-roberta-base-sentiment-latest",
    "siebert": "siebert/sentiment-roberta-large-english",
    "lxyuan": "lxyuan/distilbert-base-multilingual-cased-sentiments-student"
}

for name, model_id in MODELS.items():
    print(f"Downloading {model_id} ...")
    AutoTokenizer.from_pretrained(model_id)
    AutoModelForSequenceClassification.from_pretrained(model_id)

print("✅ All models downloaded and cached locally")
