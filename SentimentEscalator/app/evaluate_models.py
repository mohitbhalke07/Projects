import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODELS = {
    "roberta_twitter": "cardiffnlp/twitter-roberta-base-sentiment-latest",
    "siebert": "siebert/sentiment-roberta-large-english",
    "lxyuan": "lxyuan/distilbert-base-multilingual-cased-sentiments-student"
}

TEST_TEXTS = [
    "My payment failed twice and nobody is responding",
    "Everything is working perfectly, thanks!",
    "This app is horrible, I want my money back",
    "Support resolved my issue quickly",
    "Service is okay but could be better"
]

def predict(model_id, texts):
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSequenceClassification.from_pretrained(model_id)
    model.eval()

    inputs = tokenizer(
        texts,
        padding=True,
        truncation=True,
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)

    return probs, model.config.id2label


for name, model_id in MODELS.items():
    print(f"\n{'='*60}")
    print(f"Model: {name} ({model_id})")
    print('='*60)

    probs, id2label = predict(model_id, TEST_TEXTS)

    for text, prob in zip(TEST_TEXTS, probs):
        label_id = prob.argmax().item()
        label = id2label[label_id]
        confidence = prob[label_id].item()

        print(f"\nText: {text}")
        print(f"Prediction: {label} ({confidence:.2f})")
