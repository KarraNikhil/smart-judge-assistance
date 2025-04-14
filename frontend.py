import streamlit as st
import requests
import json

# ------------------------ Helper Functions -------------------------

def start_new_case():
    """API call to initialize a new case and get a case ID"""
    # For now, generating a local ID (Replace with backend API call in future)
    st.session_state["case_id"] = f"CASE_{len(st.session_state.get('all_cases', [])) + 1}"
    st.session_state["party_data"] = {"Party A": [], "Party B": []}
    st.session_state["evidence_text"] = ""
    st.success(f"🎉 New Case Started: {st.session_state['case_id']}")


def analyze_video(party, witness):
    """Analyze video for selected party/witness"""
    response = requests.post("http://127.0.0.1:8000/analyze-video/")
    result = response.json()
    st.session_state["party_data"][party].append({
        "witness": witness,
        "video_analysis": result
    })
    st.success(f"Video Analysis for {party} - {witness}: {result}")


def analyze_audio(party, witness):
    """Analyze audio for selected party/witness"""
    try:
        response = requests.post("http://127.0.0.1:8000/analyze-audio/")

        # 🔹 Fix: Check if response is valid before calling `.json()`
        if response.status_code != 200:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return

        if not response.text.strip():  # If response is empty
            st.error("API Error: Received empty response from server.")
            return

        result = response.json()  # Parse only if response is valid JSON
        
        st.session_state["party_data"][party][-1]["audio_analysis"] = result
        st.success(f"Audio Analysis for {party} - {witness}: {result}")

    except requests.exceptions.RequestException as e:
        st.error(f"API Request Failed: {str(e)}")



def process_documents(uploaded_files):
    """Upload and process documents"""
    files = [("files", (file.name, file, file.type)) for file in uploaded_files]
    response = requests.post("http://127.0.0.1:8000/process-document/", files=files)
    summary = response.json().get("summary", "")
    st.session_state["evidence_text"] = summary
    st.success("Documents processed successfully!")
    #st.text_area("Extracted Case Summary", value = summary, height=200)
    


def get_ipc_prediction(summary, party_data, evidence_text):
    """Send data to backend for prediction"""
    url = "http://127.0.0.1:8000/predict/"
    payload = {
        "summary": summary,
        "party1": json.dumps(party_data["Party A"]),
        "party2": json.dumps(party_data["Party B"]),
        "video_analysis": {},  # Placeholder (detailed linking done backend side)
        "audio_analysis": {},  # Placeholder
        "evidence_text": evidence_text
    }
    response = requests.post(url, json=payload)
    return response.json()

# ------------------------ Streamlit App ----------------------------

st.set_page_config(page_title="AI Virtual Judge", layout="wide")
st.title("⚖️ AI Virtual Judge System")

# ------------------------ Sidebar Control Panel ---------------------

st.sidebar.header("📝 Case Management")

# ✅ New Case Initialization
if st.sidebar.button("➕ Start New Case"):
    start_new_case()

if "case_id" in st.session_state:
    st.sidebar.markdown(f"**Active Case ID:** `{st.session_state['case_id']}`")

    # ------------------------ Parties and Witnesses ---------------------
    st.sidebar.subheader("👥 Add Party & Witness")
    party = st.sidebar.selectbox("Select Party", ["Party A", "Party B"])
    witness_name = st.sidebar.text_input("Enter Witness Name")

    if st.sidebar.button("Add Witness"):
        if witness_name:
            st.session_state["party_data"][party].append({"witness": witness_name})
            st.success(f"Added Witness: {witness_name} to {party}")

    # ------------------------ Evidence Documents ------------------------
    st.sidebar.subheader("📄 Upload Case Documents")
    uploaded_files = st.sidebar.file_uploader("Upload PDFs, DOCX, TXT", accept_multiple_files=True)
    if st.sidebar.button("📜 Process Documents") and uploaded_files:
        process_documents(uploaded_files)

# ----------------------- Main Interaction Panel -----------------------

if "case_id" in st.session_state:

    # ------------------- Parties and Witness Action Panel -------------------
    st.subheader("👥 Parties and Witness Interaction")

    for party, witnesses in st.session_state["party_data"].items():
        st.markdown(f"### {party}")
        for idx, witness_data in enumerate(witnesses):
            witness_name = witness_data["witness"]
            st.markdown(f"#### 🎤 Witness: {witness_name}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"🎥 Analyze Video: {witness_name}", key=f"video_{party}_{idx}"):
                    analyze_video(party, witness_name)
            with col2:
                if st.button(f"🎙️ Analyze Audio: {witness_name}", key=f"audio_{party}_{idx}"):
                    analyze_audio(party, witness_name)

            # Display analysis results
            video_result = witness_data.get("video_analysis", {})
            audio_result = witness_data.get("audio_analysis", {})

            if video_result:
                st.info(f"Video Analysis: {video_result}")
            if audio_result:
                st.info(f"Audio Analysis: {audio_result}")

    # ------------------------ Final Judgment Prediction -----------------------
    st.subheader("⚖️ AI Judge Decision")

    # Show extracted summary if available
    summary_text = st.session_state.get("evidence_text", "")
   
    if st.button("🚀 Predict Final Judgment"):
        result = get_ipc_prediction(summary_text, st.session_state["party_data"], st.session_state["evidence_text"])
        st.success(f"✅ Predicted IPC Section: {result['predicted_ipc']}")
        st.json(result)

    # ------------------------ Judge Validation -------------------------------
    st.subheader("👨‍⚖️ Judge Validation")
    judge_feedback = st.radio("Was the AI's decision correct?", ("Pending", "Correct", "Incorrect"))
    if judge_feedback != "Pending":
        st.success(f"Judge Feedback Recorded: {judge_feedback}")

# ----------------------- Case Inactive -----------------------
else:
    st.info("⚙️ Please start a new case to proceed.")