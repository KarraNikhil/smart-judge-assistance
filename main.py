from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import shutil
import os
import json
from fastapi.encoders import jsonable_encoder

from ai_model import predict_ipc_section
from case_storage import save_case, load_cases
from document_verification import process_and_summarize_documents
from document_verification import save_summary_to_file
from video_module import analyze_video_inline
from audio_module import analyze_audio_inline

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "✅ AI Virtual Judge Backend Running!"}

@app.post("/analyze-video/")
def analyze_video_api():
    try:
        result = analyze_video_inline()
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/analyze-audio/")
def analyze_audio_api():
    try:
        result = analyze_audio_inline()  # Call your function

        # 🔹 Ensure JSON serialization compatibility
        return jsonable_encoder(result)

    except Exception as e:
        return {"error": f"Audio processing failed: {str(e)}"}
        
@app.post("/process-document/")
async def process_document(files: List[UploadFile] = File(...)):
    saved_paths = []
    try:
        os.makedirs("uploads", exist_ok=True)

        for uploaded_file in files:
            file_path = f"uploads/{uploaded_file.filename}"
            with open(file_path, "wb") as f:
                shutil.copyfileobj(uploaded_file.file, f)
            saved_paths.append(file_path)

        summary = process_and_summarize_documents(saved_paths)

        print(f"🚀 Generated Summary:\n{summary}")  # ✅ Add log

        save_summary_to_file(summary, "case_summary.txt")

        response = {
            "summary": summary,
            "message": "✅ Summary saved to case_summary.txt"
        }
        print(f"✅ Sending Response: {response}")  # ✅ Add log

        for file_path in saved_paths:
            os.remove(file_path)

        return response

    except Exception as e:
        print(f"❌ Error in process_document: {e}")
        return {"error": str(e)}



@app.post("/predict/")
def predict(data: Dict):
    try:
        summary = data.get("summary", "")
        ipc_section = predict_ipc_section(summary)
        return {"predicted_ipc": ipc_section}
    except Exception as e:
        return {"error": str(e)}

@app.post("/save-case/")
def save_case_api(case_data: Dict):
    try:
        save_case(case_data)
        return {"status": "✅ Case saved successfully!"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/load-cases/")
def load_cases_api():
    try:
        return {"cases": load_cases()}
    except Exception as e:
        return {"error": str(e)}