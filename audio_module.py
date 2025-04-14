import speech_recognition as sr
from transformers import pipeline
import torchaudio
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import librosa
from sklearn.cluster import KMeans
import numpy as np
import json
import os

# ✅ Load NLP Pipelines for Analysis
ner_pipeline = pipeline("ner", grouped_entities=True)
sentiment_pipeline = pipeline("sentiment-analysis")
emotion_pipeline = pipeline("text-classification", model="bhadresh-savani/bert-base-go-emotion")

# ✅ Convert NumPy Data Types for JSON Serialization
def convert_numpy(obj):
    """Convert NumPy data types to standard Python types for JSON serialization."""
    if isinstance(obj, np.ndarray):  
        return obj.tolist()
    elif isinstance(obj, (np.float32, np.float64)):  
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):  
        return int(obj)
    elif isinstance(obj, dict):  
        return {k: convert_numpy(v) for k, v in obj.items()}  # Convert dict values
    elif isinstance(obj, list):  
        return [convert_numpy(i) for i in obj]  # Convert list values
    return obj

# ✅ Ensure Audio is in WAV Format
def convert_to_wav(audio_path):
    """Convert non-WAV audio files to WAV format."""
    new_path = audio_path
    if not audio_path.lower().endswith(".wav"):
        new_path = audio_path.rsplit(".", 1)[0] + ".wav"
        audio = AudioSegment.from_file(audio_path)
        audio.export(new_path, format="wav")
    return new_path

# ✅ Speech-to-Text Transcription
def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
    except Exception as e:
        return f"Error in transcription: {str(e)}"

# ✅ Text Analysis (NER, Sentiment, Emotion)
def analyze_text(text):
    try:
        return {
            "NER": convert_numpy(ner_pipeline(text)),
            "Sentiment": convert_numpy(sentiment_pipeline(text)),
            "Emotion": convert_numpy(emotion_pipeline(text))
        }
    except Exception as e:
        return {"error": f"Text analysis failed: {str(e)}"}

# ✅ Audio Feature Extraction
def analyze_audio_features(audio_path):
    try:
        audio = AudioSegment.from_wav(audio_path)
        if len(audio) > 60000:  # Limit processing to 60 sec
            audio = audio[:60000]

        loudness = audio.dBFS
        nonsilent = detect_nonsilent(audio, min_silence_len=500, silence_thresh=loudness)

        waveform, sr = torchaudio.load(audio_path)
        duration = waveform.shape[1] / sr

        return {
            "Duration": float(duration),  
            "Loudness": float(loudness),
            "NonSilentSegments": convert_numpy(nonsilent)
        }
    except Exception as e:
        return {"error": f"Audio feature analysis failed: {str(e)}"}

# ✅ Speaker Diarization (Identifying Speakers)
def speaker_diarization(audio_path):
    try:
        y, sr = librosa.load(audio_path, sr=16000, duration=30)  # Process only first 30 sec
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

        kmeans = KMeans(n_clusters=2, random_state=0, n_init=10).fit(mfcc.T)
        return convert_numpy(kmeans.labels_.tolist())
    except Exception as e:
        return {"error": f"Speaker diarization failed: {str(e)}"}

# ✅ Full Audio Analysis Pipeline
def analyze_audio_inline(audio_path="outputs/recorded_audio.wav"):
    os.makedirs("outputs", exist_ok=True)
    output = {}

    try:
        # 🔹 Convert to WAV if necessary
        audio_path = convert_to_wav(audio_path)

        # 🔹 Step 1: Transcription
        transcription = transcribe_audio(audio_path)
        output["Transcription"] = transcription

        # 🔹 Step 2: Text Analysis
        output["TextAnalysis"] = analyze_text(transcription)

        # 🔹 Step 3: Audio Feature Extraction
        output["AudioFeatures"] = analyze_audio_features(audio_path)

        # 🔹 Step 4: Speaker Diarization
        output["SpeakerDiarization"] = speaker_diarization(audio_path)

        # ✅ Save JSON Output
        with open("outputs/audio_analysis.json", "w") as f:
            json.dump(output, f, indent=4, default=convert_numpy)

    except Exception as e:
        output = {"error": f"Audio processing failed: {str(e)}"}

    return output
