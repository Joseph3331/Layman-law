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

# Load environment variables early
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Create Flask app instance BEFORE using it
app = Flask(__name__)

# Setup CORS once, allowing your frontend domain (or use "*" if you want all)
CORS(app, origins=["https://layman-law.vercel.app"])

endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"
token = os.environ.get("GITHUB_TOKEN")
if not token:
    raise RuntimeError("GITHUB_TOKEN environment variable is not set.")

client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(token))

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"txt", "pdf", "doc", "docx"}

# Helper functions here (allowed_file, save_file, extract_text_from_file, etc.)
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

# Define your Flask routes (simplify, extract, risks, compare, qa, health) as is.

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

# (Continue adding other endpoints similarly...)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"message": "Backend is running!", "status": "success", "api_connected": True, "model": model})

if __name__ == "__main__":
    print("Starting server on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
