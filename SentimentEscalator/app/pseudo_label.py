import pandas as pd
from transformers import pipeline
from tqdm import tqdm

# Load teacher model
teacher = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)

# Load tickets
df = pd.read_csv("tickets_raw.csv")

results = []

for _, row in tqdm(df.iterrows(), total=len(df)):
    text = row["text"]

    pred = teacher(text)[0]

    results.append({
        "id": row["id"],
        "text": text,
        "sentiment": pred["label"],
        "confidence": round(pred["score"], 4)
    })

labeled_df = pd.DataFrame(results)

# Save pseudo-labeled data
labeled_df.to_csv("tickets_pseudo_labeled.csv", index=False)

print("Saved tickets_pseudo_labeled.csv")
