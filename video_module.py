import cv2
import mediapipe as mp
from deepface import DeepFace
import json
import time
from collections import Counter
import sounddevice as sd
import soundfile as sf
import threading
import os

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

def record_audio(duration=60, filename="outputs/recorded_audio.wav", samplerate=44100):
    os.makedirs("outputs", exist_ok=True)
    audio_recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=2, dtype='int16')
    sd.wait()
    sf.write(filename, audio_recording, samplerate)

def analyze_video_inline(duration=60, lean_threshold=0.1):
    os.makedirs("outputs", exist_ok=True)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return {"error": "Webcam not accessible."}

    audio_thread = threading.Thread(target=record_audio, args=(duration,))
    audio_thread.start()

    confidence_score = 100
    start_time = time.time()
    next_analysis_time = start_time + 5
    emotion_list = []
    analysis_snapshots = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        current_time = time.time()

        if current_time >= next_analysis_time:
            emotion = DeepFace.analyze(frame, actions=["emotion"], enforce_detection=False)[0].get("dominant_emotion", "Unknown")
            emotion_list.append(emotion)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frame_rgb)
            posture = "Upright"
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                shoulder_diff = abs(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y - landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y)
                posture = "Leaning" if shoulder_diff > lean_threshold else "Upright"

            if emotion in ["fear", "sad", "angry"] or posture == "Leaning":
                confidence_score = max(0, confidence_score - 10)
            else:
                confidence_score = min(100, confidence_score + 5)

            analysis_snapshots.append({
                "timestamp": current_time,
                "emotion": emotion,
                "posture": posture,
                "confidence_score": confidence_score
            })
            next_analysis_time = current_time + 5

        if current_time - start_time >= duration:
            break

    cap.release()
    audio_thread.join()

    dominant_emotion = Counter(emotion_list).most_common(1)[0][0] if emotion_list else "Unknown"
    average_confidence = sum([x['confidence_score'] for x in analysis_snapshots]) / len(analysis_snapshots) if analysis_snapshots else 0

    final_result = {
        "session_summary": {
            "final_dominant_emotion": dominant_emotion,
            "average_confidence_score": average_confidence
        },
        "snapshots": analysis_snapshots
    }

    with open("outputs/video_analysis.json", "w") as f:
        json.dump(final_result, f, indent=4)

    return final_result