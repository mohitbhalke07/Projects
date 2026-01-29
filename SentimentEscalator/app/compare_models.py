from transformers import pipeline

base_model = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)

finetuned_model = pipeline(
    "sentiment-analysis",
    model="./finetuned_model"
)

test_texts = [
    "My payment failed twice and nobody is responding",
    "Service is okay but could be better",
    "Support resolved my issue quickly",
    "I want a refund immediately"
]

print("\n=== BASE MODEL ===")
for text in test_texts:
    print(text)
    print(base_model(text)[0])

print("\n=== FINETUNED MODEL ===")
for text in test_texts:
    print(text)
    print(finetuned_model(text)[0])
