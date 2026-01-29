import pandas as pd

df = pd.read_csv("tickets_pseudo_labeled.csv")

THRESHOLD = 0.7

filtered = df[df["confidence"] >= THRESHOLD]

# Only keep text + label (required for fine-tuning)
train_df = filtered[["text", "sentiment"]]
train_df.columns = ["text", "label"]

train_df.to_csv("sentiment_train.csv", index=False)

print(f"Training samples: {len(train_df)}")
