from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)
import numpy as np
import evaluate

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Load dataset
dataset = load_dataset("csv", data_files="sentiment_train.csv")
dataset = dataset["train"].train_test_split(test_size=0.2)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=3
)

label2id = {"negative": 0, "neutral": 1, "positive": 2}
id2label = {v: k for k, v in label2id.items()}

model.config.label2id = label2id
model.config.id2label = id2label

def encode_labels(example):
    example["labels"] = label2id[example["label"]]
    return example

dataset = dataset.map(encode_labels)

def tokenize(batch):
    return tokenizer(
        batch["text"],
        truncation=True,
        padding="max_length",
        max_length=128
    )

dataset = dataset.map(tokenize, batched=True)

dataset.set_format(
    type="torch",
    columns=["input_ids", "attention_mask", "labels"]
)

metric = evaluate.load("f1")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=1)
    return metric.compute(
        predictions=preds,
        references=labels,
        average="weighted"
    )

training_args = TrainingArguments(
    output_dir="./sentiment_roberta_finetuned",
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=3,
    learning_rate=2e-5,
    logging_steps=10,
    save_total_limit=2,
    report_to="none",
    fp16=True  
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    compute_metrics=compute_metrics,
)

trainer.train()

# trainer.save_model("./finetuned_model")
# tokenizer.save_pretrained("./finetuned_model")
model.save_pretrained(
    "./model/finetuned_model",
    safe_serialization=True
)
tokenizer.save_pretrained("./finetuned_model")

