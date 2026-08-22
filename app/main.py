from flask import Flask, request, render_template
import os
import pandas as pd

app = Flask(__name__)
UPLOAD_FOLDER = "data"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


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
        columns=columns,
        preview_table=preview_html,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)