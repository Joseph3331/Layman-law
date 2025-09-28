import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import PyPDF2
import docx
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

from flask_cors import CORS
CORS(app, origins=["https://layman-law.vercel.app"])
# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"
token = os.environ.get("GITHUB_TOKEN")
if not token:
    raise RuntimeError("GITHUB_TOKEN environment variable is not set.")

client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(token))

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # CORS enabled for any origin

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"txt", "pdf", "doc", "docx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file_storage):
    filename = secure_filename(file_storage.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file_storage.save(filepath)
    return filepath

def extract_text_from_file(filepath):
    ext = filepath.rsplit(".", 1)[1].lower()
    text = ""
    if ext == "txt":
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    elif ext == "pdf":
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
    elif ext in {"doc", "docx"}:
        docc = docx.Document(filepath)
        for para in docc.paragraphs:
            text += para.text + "\n"
    return text.strip()

def extract_text_from_filestorage(file_storage):
    filepath = save_file(file_storage)
    return extract_text_from_file(filepath)

def generate_response(prompt, temperature=0.7, top_p=1, system_message=None):
    if system_message is None:
        system_message = "You are a helpful AI assistant that simplifies legal documents."
    try:
        response = client.complete(
            model=model,
            messages=[
                SystemMessage(content=system_message),
                UserMessage(content=prompt),
            ],
            temperature=temperature,
            top_p=top_p,
        )
        if response and getattr(response, "choices", None):
            choice = response.choices[0]
            if getattr(choice, "message", None) and getattr(choice.message, "content", None):
                return choice.message.content
        return ""
    except Exception as e:
        print(f"Error in generate_response: {e}")
        return f"⚠️ Error calling model: {str(e)}"

def safe_json_load(s):
    try:
        return json.loads(s)
    except Exception:
        return None

@app.route("/simplify", methods=["POST"])
def simplify():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    try:
        text = extract_text_from_filestorage(file)
        if not text:
            return jsonify({"error": "Could not extract text"}), 500

        prompt = f"Simplify the following legal text into plain English. Keep it short and sectioned.\n\n{text[:3000]}"
        simplified = generate_response(prompt)
        return jsonify({"simplified": simplified})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/extract", methods=["POST"])
def extract():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    try:
        text = extract_text_from_filestorage(file)
        if not text:
            return jsonify({"error": "Could not extract text"}), 500

        prompt = (
            "Extract the key clauses from the following contract. Return a short JSON object with keys: "
            '"Payment", "Dates", "Termination", "Liabilities", "IP". If a field is not present return an empty string.\n\n'
            f"Contract:\n{text[:3000]}"
        )
        response_text = generate_response(prompt)
        parsed = safe_json_load(response_text)
        if isinstance(parsed, dict):
            return jsonify({"clauses": parsed})
        return jsonify({"clauses": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/risks", methods=["POST"])
def risks():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    try:
        text = extract_text_from_filestorage(file)
        if not text:
            return jsonify({"error": "Could not extract text"}), 500

        system_msg = (
            "You are an expert contract reviewer. Analyze the contract and return a JSON array "
            "where each item is an object: {\"clause\": \"short clause name or excerpt\", "
            "\"severity\": \"Red|Yellow|Green\", \"details\": \"one-sentence explanation\"}.\n"
            "Return ONLY valid JSON (no extra commentary)."
        )
        prompt = f"Analyze the following contract and return JSON as described.\n\n{text[:3000]}"
        raw = generate_response(prompt, system_message=system_msg)
        parsed = safe_json_load(raw)
        if isinstance(parsed, list):
            normalized = []
            for item in parsed:
                if not isinstance(item, dict):
                    continue
                clause = item.get("clause") or item.get("title") or item.get("name") or ""
                severity = (item.get("severity") or item.get("level") or "").strip().lower()
                if severity.startswith("r"):
                    sev = "Red"
                elif severity.startswith("y"):
                    sev = "Yellow"
                elif severity.startswith("g"):
                    sev = "Green"
                else:
                    sev = "Yellow"
                details = item.get("details") or item.get("explanation") or ""
                normalized.append({"clause": clause, "severity": sev, "details": details})
            return jsonify({"risks": normalized})

        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        if lines:
            heuristics = []
            for ln in lines:
                low = ln.lower()
                if "high" in low or "red" in low or "severe" in low:
                    sev = "Red"
                elif "medium" in low or "yellow" in low or "caution" in low:
                    sev = "Yellow"
                elif "low" in low or "green" in low or "minor" in low:
                    sev = "Green"
                else:
                    sev = "Yellow"
                heuristics.append({"clause": ln[:120], "severity": sev, "details": ln})
            return jsonify({"risks": heuristics})

        return jsonify({"risks": [{"clause": "Analysis", "severity": "Yellow", "details": raw}]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/compare", methods=["POST"])
def compare():
    if "file1" not in request.files or "file2" not in request.files:
        return jsonify({"error": "Two files required: file1 and file2"}), 400
    f1 = request.files["file1"]
    f2 = request.files["file2"]
    if f1.filename == "" or f2.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    if not allowed_file(f1.filename) or not allowed_file(f2.filename):
        return jsonify({"error": "File type not allowed"}), 400

    try:
        text1 = extract_text_from_filestorage(f1)
        text2 = extract_text_from_filestorage(f2)
        if not text1 or not text2:
            return jsonify({"error": "Could not extract text from one or both files"}), 500

        prompt = f"Compare these two contracts and list the key differences in plain English. Contract A:\n\n{text1[:2000]}\n\nContract B:\n\n{text2[:2000]}"
        diff = generate_response(prompt)
        return jsonify({"differences": diff})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/qa", methods=["POST"])
def qa():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    question = request.form.get("question") or (request.json.get("question") if request.is_json else None)
    if not question:
        return jsonify({"error": "No question provided"}), 400
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    try:
        text = extract_text_from_filestorage(file)
        if not text:
            return jsonify({"error": "Could not extract text"}), 500

        prompt = f"Answer the question based on the following contract. Question: {question}\n\nContract:\n{text[:3000]}"
        answer = generate_response(prompt)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"message": "Backend is running!", "status": "success", "api_connected": True, "model": model})

if __name__ == "__main__":
    print("Starting server on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
