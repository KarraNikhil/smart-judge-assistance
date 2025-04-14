import os
import re
import pdfplumber
import fitz  # PyMuPDF
import docx
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

nltk.download("punkt")


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdfplumber; fallback to PyMuPDF if empty."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"pdfplumber failed for {pdf_path}: {e}")

    # Fallback if text is still empty
    if not text.strip():
        print(f"Falling back to PyMuPDF for {pdf_path}")
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text("text") + "\n"
    return text


def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])


def extract_text_from_txt(txt_path):
    with open(txt_path, "r", encoding="utf-8") as file:
        return file.read()


def clean_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_case_details(case_text):
    words = case_text.split()
    case_title = " ".join(words[:10]) if len(words) >= 10 else "Unknown Case Title"
    match = re.search(r"([\w\s]+)\s+vs\.?\s+([\w\s]+)", case_text, re.IGNORECASE)
    parties = f"{match.group(1).strip()} vs {match.group(2).strip()}" if match else "[Unknown Parties]"
    return case_title, parties


def generate_proof_documents(legal_issues):
    proof_docs = {
        "Breach of Contract": ["Signed Contract", "Emails", "Receipts"],
        "Fraudulent Activity": ["Financial Records", "Chats", "Audit Report"],
        "Negligence & Duty of Care": ["Medical Reports", "Witness Statements", "Incident Photos"],
        "Agreement Violation": ["Original Agreement", "Communication Records", "Legal Notices"],
        "General Civil Dispute": ["Court Filings", "Affidavits", "Correspondence"]
    }
    proofs = []
    for issue in legal_issues:
        proofs.extend(proof_docs.get(issue, ["General Evidence Documents"]))
    return list(set(proofs))[:3]


def generate_case_summary(case_text, num_sentences=20):
    if not case_text.strip():
        return "❗ No valid text extracted from documents."

    parser = PlaintextParser.from_string(case_text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary_sentences = summarizer(parser.document, num_sentences)
    if not summary_sentences:
        return "❗ Unable to generate summary — possibly due to text formatting or sentence structure issues."

    summary = "\n".join([str(sentence) for sentence in summary_sentences])

    legal_issues = []
    for keyword, issue in {
        "breach": "Breach of Contract",
        "fraud": "Fraudulent Activity",
        "negligence": "Negligence & Duty of Care",
        "agreement": "Agreement Violation"
    }.items():
        if keyword in case_text.lower():
            legal_issues.append(issue)
    if not legal_issues:
        legal_issues.append("General Civil Dispute")

    case_title, parties = extract_case_details(case_text)
    required_proofs = generate_proof_documents(legal_issues)

    structured_summary = (
        f"### Case Summary ###\n\n"
        f"*Case Title:* {case_title}\n"
        f"*Parties Involved:* {parties}\n\n"
        f"*Summary of Facts:*\n{summary}\n\n"
        f"*Key Legal Issues Identified:*\n" + "\n".join(f"- {issue}" for issue in legal_issues) + "\n\n"
        f"*Suggested Proof Documents:*\n" + "\n".join(f"- {doc}" for doc in required_proofs) + "\n"
    )
    return structured_summary


def extract_text(file_paths):
    combined_text = ""
    for file_path in file_paths:
        _, ext = os.path.splitext(file_path)
        if ext.lower() == ".pdf":
            extracted = extract_text_from_pdf(file_path)
            print(f"PDF Extracted text length ({file_path}): {len(extracted)}")
            combined_text += extracted + "\n"
        elif ext.lower() == ".docx":
            extracted = extract_text_from_docx(file_path)
            print(f"DOCX Extracted text length ({file_path}): {len(extracted)}")
            combined_text += extracted + "\n"
        elif ext.lower() == ".txt":
            extracted = extract_text_from_txt(file_path)
            print(f"TXT Extracted text length ({file_path}): {len(extracted)}")
            combined_text += extracted + "\n"
        else:
            print(f"Unsupported file type: {file_path}")
    return clean_text(combined_text)


def process_and_summarize_documents(file_paths):
    case_text = extract_text(file_paths)
    print(f"=== Full combined extracted text length: {len(case_text)} ===")
    print(f"=== Extracted Text Preview ===\n{case_text[:500]}")
    summary = generate_case_summary(case_text)
    print(f"=== Generated Summary Preview ===\n{summary[:500]}")
    return summary


def save_summary_to_file(summary, output_file="case_summary.txt"):
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(summary)
    print(f"✅ Summary saved to {output_file}")