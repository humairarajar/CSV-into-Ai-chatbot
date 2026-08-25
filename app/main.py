from flask import Flask, request, render_template
import os
import pandas as pd
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Folder where uploaded CSV files are temporarily stored
UPLOAD_FOLDER = "data"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Initialize Groq client for AI features
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


@app.route("/")
def home():
    # Render the homepage with the upload form
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    # Check if a file was included in the request
    if "file" not in request.files:
        return "No file part in request", 400

    file = request.files["file"]

    # Check if a file was actually selected
    if file.filename == "":
        return "No file selected", 400

    # Only allow CSV files
    if not file.filename.endswith(".csv"):
        return "Please upload a CSV file", 400

    # Save the uploaded file to the data folder
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # Read the uploaded CSV file into a pandas DataFrame
    df = pd.read_csv(filepath)

    # Edge case: reject empty CSV files
    if df.empty:
        return "The uploaded CSV is empty!", 400

    # Get file size in KB
    file_size_kb = round(os.path.getsize(filepath) / 1024, 2)

    # Extract preview info: total rows, columns, and column names
    num_rows, num_cols = df.shape
    columns = df.columns.tolist()
    preview_html = df.head().to_html(classes="preview-table", index=False)

    # Render the preview page with the extracted data
    return render_template(
        "preview.html",
        filename=file.filename,
        num_rows=num_rows,
        num_cols=num_cols,
        file_size_kb=file_size_kb,
        columns=columns,
        preview_table=preview_html,
    )


@app.route("/list-models")
def list_models():
    # List all models available to this API key - helps debug 404 model errors
    models = client.models.list()
    model_ids = [m.id for m in models.data]
    return "<br>".join(model_ids)


@app.route("/test-ai")
def test_ai():
    # Simple test to confirm Groq connection works
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": "Say hello in one short sentence."}],
    )
    return response.choices[0].message.content


@app.route("/ask", methods=["POST"])
def ask():
    # Get the question and filename from the request
    question = request.form.get("question")
    filename = request.form.get("filename")

    if not question or not filename:
        return "Missing question or filename", 400

    # Load the CSV to get its structure for context
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    df = pd.read_csv(filepath)
    columns = df.columns.tolist()
    dtypes = df.dtypes.astype(str).to_dict()

    # Build a prompt that gives the AI context about the data
    prompt = f"""You are a pandas expert. Given a DataFrame called `df` with these columns and types:
{dtypes}

Write ONLY a single line of pandas code (no explanation, no markdown) that answers this question:
"{question}"

The code should store the final answer in a variable called `result`."""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
    )

    generated_code = response.choices[0].message.content.strip()

    # Remove markdown code fences if the AI added them despite instructions
    generated_code = generated_code.replace("```python", "").replace("```", "").strip()

    # Safe execution: only allow access to pandas and the dataframe itself
    safe_globals = {"pd": pd, "df": df}
    safe_locals = {}

    try:
        exec(generated_code, safe_globals, safe_locals)
        result = safe_locals.get("result", "No result variable found")
    except Exception as e:
        return f"Sorry, I couldn't process that question. Error: {str(e)}"

    return str(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)