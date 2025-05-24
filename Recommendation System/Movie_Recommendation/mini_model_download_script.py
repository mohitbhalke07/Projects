from sentence_transformers import SentenceTransformer
import os

model_name = "sentence-transformers/paraphrase-MiniLM-L3-v2"  # ~90MB on disk
save_path = "./local_model"

model = SentenceTransformer(model_name)
model.save(save_path)

print(f"Model saved locally to {save_path}")