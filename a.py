import os
import pdfplumber
import docx
import re
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

# Download required NLTK data
nltk.download("punkt")


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file"""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text


def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file"""
    doc = docx.Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text


def extract_text_from_txt(txt_path):
    """Extract text from a TXT file"""
    with open(txt_path, "r", encoding="utf-8") as file:
        text = file.read()
    return text


def clean_text(text):
    """Remove unnecessary links, references, and extra spaces"""
    text = re.sub(r'http\S+', '', text)  # Remove links
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces and newlines
    return text.strip()


def extract_case_details(case_text):
    """Extract Case Title and Parties Involved from the text"""
    # Extract first 10 words as case title
    words = case_text.split()
    case_title = " ".join(words[:10]) if len(words) >= 10 else "Unknown Case Title"

    # Extract plaintiff vs defendant
    match = re.search(r"([\w\s]+)\s+vs\.?\s+([\w\s]+)", case_text, re.IGNORECASE)
    if match:
        plaintiff, defendant = match.groups()
        parties = f"{plaintiff.strip()} vs {defendant.strip()}"
    else:
        parties = "[Unknown Parties]"

    return case_title, parties


def extract_text(file_paths):
    """Extract and clean text from multiple files"""
    combined_text = ""
    for file_path in file_paths:
        _, ext = os.path.splitext(file_path)
        if ext.lower() == ".pdf":
            combined_text += extract_text_from_pdf(file_path) + "\n\n"
        elif ext.lower() == ".docx":
            combined_text += extract_text_from_docx(file_path) + "\n\n"
        elif ext.lower() == ".txt":
            combined_text += extract_text_from_txt(file_path) + "\n\n"
        else:
            print(f"Warning: Unsupported file format for {file_path}, skipping...")

    return clean_text(combined_text)


def generate_case_summary(case_text, num_sentences=10):
    """Generate a structured case summary from multiple legal documents"""
    parser = PlaintextParser.from_string(case_text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary_sentences = summarizer(parser.document, num_sentences)

    summary_text = "\n".join([str(sentence) for sentence in summary_sentences])

    # Extract key legal issues
    legal_issues = []
    if "breach" in case_text.lower():
        legal_issues.append("Breach of Contract")
    if "fraud" in case_text.lower():
        legal_issues.append("Fraudulent Activity")
    if "negligence" in case_text.lower():
        legal_issues.append("Negligence & Duty of Care")
    if "agreement" in case_text.lower():
        legal_issues.append("Agreement Violation")
    if not legal_issues:
        legal_issues.append("General Civil Dispute")

    # Extract case details
    case_title, parties_involved = extract_case_details(case_text)

    # Generate structured summary
    structured_summary = (
            f"### Comprehensive Case Summary ###\n\n"
            f"*Case Title:* {case_title}\n"
            f"*Parties Involved:* {parties_involved}\n\n"
            f"*Summary of Legal Documents (Including Proofs & Evidence):*\n"
            f"{summary_text}\n\n"
            f"*Key Legal Issues:*\n"
            + "\n".join(f"- {issue}" for issue in legal_issues) +
            "\n\n"
            "*Possible Verdict Considerations:*\n"
            "- The court may consider whether the defendant fulfilled their obligations.\n"
            "- Review of agreements, promissory notes, or mortgage deeds.\n"
            "- Examination of whether statutory limitations have expired.\n"
            "- Witness statements and past rulings may play a role in the verdict.\n"
    )

    return structured_summary


def save_summary_to_file(summary, output_file="case_summary.txt"):
    """Save the structured summary to a text file"""
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(summary)
    print(f"\n✅ Comprehensive case summary saved successfully: {output_file}")


# Main Execution
if __name__ == "__main__":
    file_paths = input("Enter the paths of all case-related documents (separated by commas): ").strip().split(",")

    try:
        case_text = extract_text(file_paths)
        if case_text:
            print("\nGenerating Comprehensive Case Summary...\n")
            structured_summary = generate_case_summary(case_text)

            # Save structured output to a file
            save_summary_to_file(structured_summary)
        else:
            print("Error: No text extracted from the documents!")
    except Exception as e:
        print(f"Error: {e}")