from flask import Flask, request, render_template
import os
import io
import base64
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
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


def format_result(result):
    # Round floating point numbers to 2 decimal places for cleaner display
    if isinstance(result, float):
        return round(result, 2)
    return result


def wants_chart(question):
    # Check if the user is asking for a visual chart
    chart_keywords = ["chart", "graph", "plot", "visualize", "visualise"]
    return any(word in question.lower() for word in chart_keywords)


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

    is_chart_request = wants_chart(question)

    if is_chart_request:
        # Prompt for generating a matplotlib chart
        prompt = f"""You are a pandas and matplotlib expert. Given a DataFrame called `df` with these columns and types:
{dtypes}

Write ONLY Python code (no explanation, no markdown) using matplotlib to create a chart that answers this question:
"{question}"

Use `plt` (already imported as matplotlib.pyplot) and `df`. Do NOT call plt.show(). Do NOT save to a file. Just create the figure.

Respond with only the code, nothing else."""
    else:
        # Prompt for generating pandas code that returns a text/number answer
        prompt = f"""You are a pandas expert. Given a DataFrame called `df` with these columns and types:
{dtypes}

The user asked this question:
"{question}"

Rules:
- Short or casually phrased questions are fine (e.g. "highest value", "average", "top 5") — treat them as valid if they relate to the data in any reasonable way, even without a full sentence or question mark.
- Only write result = "INVALID_QUESTION" if the input is truly random gibberish, nonsense characters, or has absolutely nothing to do with analyzing this data.
- Otherwise, write ONLY a single line of pandas code (no explanation, no markdown) that answers the question and stores the final answer in a variable called `result`.

Respond with only the code line, nothing else."""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
    )

    generated_code = response.choices[0].message.content.strip()

    # Remove markdown code fences if the AI added them despite instructions
    generated_code = generated_code.replace("```python", "").replace("```", "").strip()

    if is_chart_request:
        # Safe execution for chart generation
        safe_globals = {"pd": pd, "df": df, "plt": plt}
        safe_locals = {}

        try:
            plt.figure(figsize=(7, 4))
            exec(generated_code, safe_globals, safe_locals)

            # Convert the chart to a base64 image string
            buf = io.BytesIO()
            plt.savefig(buf, format="png", bbox_inches="tight")
            plt.close()
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode("utf-8")

            return f'<img src="data:image/png;base64,{img_base64}" style="max-width:100%; border-radius:10px;">'
        except Exception as e:
            plt.close()
            return "Sorry, I couldn't generate that chart. Try rephrasing it."

    # Safe execution for text/number answers
    safe_globals = {"pd": pd, "df": df}
    safe_locals = {}

    try:
        exec(generated_code, safe_globals, safe_locals)
        result = safe_locals.get("result", "No result variable found")

        # Check if the AI flagged this as an invalid/unclear question
        if result == "INVALID_QUESTION":
            return "I'm not sure what you're asking. Try rephrasing your question about the data — e.g. 'what is the average of column X?'"

        result = format_result(result)
    except Exception as e:
        return "Sorry, I couldn't process that question. Try rephrasing it."

    return str(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port)