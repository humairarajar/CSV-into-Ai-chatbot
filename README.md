# CSV Chat 💬📊

Upload any CSV file and ask questions about your data in plain English — get instant answers, no coding or Excel formulas needed.

## How it works
1. Upload a CSV file
2. Ask a question in natural language (e.g. "which city had the highest sales?")
3. The app uses an LLM to understand your question, generate the right pandas code, run it safely, and show you the answer

## Tech Stack
- **Backend:** Flask
- **Data handling:** Pandas
- **AI:** Google Gemini API
- **Charts:** Matplotlib

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
python app/main.py
```

Then open `http://127.0.0.1:5000` in your browser.

## Status
🚧 Under active development — building this out day by day.

## Roadmap
- [x] Day 1: Project setup
- [x] Day 2: File upload
- [x] Day 3: CSV preview (rows, columns, file size)
- [x] Day 4: Chat UI
- [x] Day 5: Groq AI integration
- [x] Day 6: Question → pandas code generation
- [ ] Day 7: Safe code execution
- [ ] Day 8: Display results in chat
- [ ] Day 9: Error handling
- [ ] Day 10: Chart generation
- [ ] Day 11: Chat history
- [ ] Day 12: UI polish
- [ ] Day 13: Deployment
- [ ] Day 14: Final docs and demo