# CSV Chat 💬📊

Upload any CSV file and ask questions about your data in plain English — get instant answers, no coding or Excel formulas needed.

## What it does

Upload a spreadsheet, then ask questions like:
- "what is the average revenue?"
- "which city has the highest sales?"
- "top 3 products by revenue"
- "show a chart of revenue by product"

The app translates your question into pandas code using an LLM, runs it safely against your data, and returns the answer — as text or as an auto-generated chart.

## Tech Stack

- **Backend:** Flask
- **Data handling:** Pandas
- **AI:** Groq API (Llama models)
- **Charts:** Matplotlib

## Features

- CSV upload with data preview (rows, columns, file size)
- Natural language question answering over your data
- Automatic chart generation on request
- Persistent chat history within a session
- Safe execution of AI-generated code (sandboxed, no arbitrary access)
- Graceful handling of invalid or unclear questions

## Project Structure

CSV-into-Ai-chatbot/
├── app/
│ ├── main.py
│ └── templates/
│ ├── index.html
│ └── preview.html
├── data/ # Uploaded CSVs (gitignored)
├── utils/ # Helper functions
├── requirements.txt
├── .gitignore
└── README.md


## Setup

```bash
git clone https://github.com/humairarajar/CSV-into-Ai-chatbot
cd CSV-into-Ai-chatbot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the root folder with your Groq API key:

GROQ_API_KEY=your_key_here


Run the app:
```bash
python app/main.py
```

Then open `http://127.0.0.1:7860` in your browser.

## How it works

1. User uploads a CSV — Flask reads it into a pandas DataFrame and shows a preview
2. User asks a question — the app sends the column names, types, and question to an LLM (via Groq)
3. The LLM generates a single line of pandas code to answer the question
4. That code runs in a restricted execution environment (only `pandas` and the DataFrame are exposed)
5. The result is formatted and returned — as text, or rendered as a chart image if the question asked for one

## Status

Core features complete. Deployment is on hold (explored Hugging Face Spaces and Render, both introduced free-tier restrictions after initial setup) — actively looking into free hosting alternatives.

## Roadmap

- [x] Day 1: Project setup
- [x] Day 2: File upload
- [x] Day 3: CSV preview (rows, columns, file size)
- [x] Day 4: Chat UI
- [x] Day 5: Groq AI integration
- [x] Day 6: Question → pandas code generation
- [x] Day 7: Safe code execution
- [x] Day 8: Result formatting and error handling
- [x] Day 9: Chart generation
- [x] Day 10: Chat history
- [x] Day 11: UI polish
- [x] Day 12: Deployment (attempted, on hold)
- [x] Day 13: Testing and bug fixes
- [x] Day 14: Final documentation

## Built as part of a 14-day daily-commit challenge

Each feature was built incrementally, one day at a time, with progress tracked through daily commits.