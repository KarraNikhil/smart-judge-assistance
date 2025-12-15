⚖️ Smart Justice: AI Virtual Judge System

Smart Justice is an AI-powered virtual judge designed to assist in swift, fair, and transparent resolution of low-stakes legal disputes. The system leverages multi-modal artificial intelligence—combining NLP, Machine Learning, Computer Vision, Speech Processing, and Audio Forensics—to analyze legal documents, audio/video testimonies, and digital evidence, and generate AI-assisted judicial recommendations with human oversight.
This project is built as a decision-support system, not a replacement for judges, ensuring ethical AI usage, fairness, and accountability in legal workflows




⚖️ Smart Justice: AI Virtual Judge System

Smart Justice is an AI-powered virtual judge designed to assist in swift, fair, and transparent resolution of low-stakes legal disputes. The system leverages multi-modal artificial intelligence—combining NLP, Machine Learning, Computer Vision, Speech Processing, and Audio Forensics—to analyze legal documents, audio/video testimonies, and digital evidence, and generate AI-assisted judicial recommendations with human oversight.
This project is built as a decision-support system, not a replacement for judges, ensuring ethical AI usage, fairness, and accountability in legal workflows 



🚀 Key Features

📄 Legal Document Analysis
Extracts and summarizes content from PDF, DOCX, and TXT files
Identifies key legal issues, parties involved, and relevant evidence
Generates structured case summaries using NLP (LexRank)

🧠 AI-Based Legal Reasoning
Fine-tuned BERT-based model trained on IPC sections
Predicts applicable IPC sections based on case summaries
Supports civil, consumer, family, labor, and negotiable instrument cases


🎥 Video Testimony Analysis
Facial emotion detection using DeepFace
Posture and confidence analysis via MediaPipe
Confidence scoring based on behavioral cues


🎙️ Audio & Speech Analysis
Speech-to-text transcription
Sentiment, emotion, and named entity recognition
Audio loudness, silence detection, and speaker diarization


👨‍⚖️ Human-in-the-Loop Validation
Judges review AI recommendations
Feedback is used for continuous learning and model improvement


🌐 End-to-End Web Application
Streamlit-based frontend for case management
FastAPI backend for AI inference and evidence processing
REST APIs for document, audio, video, and judgment prediction



🧩 System Architecture

Multi-Modal Pipeline

Documents / Audio / Video
        ↓
Evidence Analysis (NLP, CV, STT)
        ↓
Judgment Synthesis
        ↓
AI Recommendation (IPC Prediction)
        ↓
Judge Validation & Feedback
        ↓
Continuous Learning



🛠️ Technology Stack
Frontend
Streamlit
Backend
FastAPI
REST APIs
JSON-based case storage
AI & ML
PyTorch
Hugging Face Transformers (BERT)
NLTK, Sumy (Text Summarization)
DeepFace (Emotion Detection)
MediaPipe (Pose Estimation)
SpeechRecognition, Torchaudio, Librosa
Document Processing
pdfplumber
PyMuPDF (fallback)
python-docx


📂 Supported Inputs
📄 Legal documents: PDF, DOCX, TXT
🎙️ Audio evidence (WAV and converted formats)
🎥 Live or recorded video testimonies


🎯 Use Case
Low-stakes civil disputes
Consumer protection cases
Family and rent-related disputes
Negotiable Instruments Act (Section 138) cases
Preliminary legal analysis and case triaging

⚠️ Disclaimer
This system is not a replacement for human judges.
It serves as an AI-assisted decision-support tool, ensuring transparency, ethical compliance, and judicial oversight at every stage.
