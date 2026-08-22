from flask import Flask, request, render_template
import os
import pandas as pd

app = Flask(__name__)
UPLOAD_FOLDER = "data"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "No file part in request", 400

    file = request.files["file"]

    if file.filename == "":
        return "No file selected", 400

    if not file.filename.endswith(".csv"):
        return "Please upload a CSV file", 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # CSV ko read karein pandas se
    df = pd.read_csv(filepath)

    # Preview info nikalein
    num_rows, num_cols = df.shape
    columns = df.columns.tolist()
    preview_html = df.head().to_html(classes="preview-table", index=False)

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