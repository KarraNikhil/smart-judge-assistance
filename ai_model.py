import json
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

try:
    model_path = "./Final"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    model.eval()

    with open("ipc_mapping.json", "r") as f:
        ipc_mapping = json.load(f)

    print("✅ Model and Tokenizer Loaded Successfully!")
    print(f"✅ IPC Mapping Loaded with {len(ipc_mapping)} sections.")

except Exception as e:
    print(f"🔥 Error during model or tokenizer loading: {e}")


def predict_ipc_section(text: str) -> str:
    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits

        predicted_label = torch.argmax(logits, dim=1).item()

        ipc_section = ipc_mapping.get(f"LABEL_{predicted_label}", "Unknown")

        print(f"✅ Prediction: {ipc_section}")
        return ipc_section

    except Exception as e:
        print(f"🔥 Error during prediction: {e}")
        return "Prediction Failed"