
# AI-MUFTI – Islamic Q&A Bot (Web GUI)

A fully conversational web application for asking questions about the Noble Quran and Islamic history.  
Built with **Flask**, **HTML/CSS/JavaScript**, and **Google Gemini**.  
Answers are given from the **Deoband school of thought** and include **exact references** – Quranic surah/verse and **Sahih** hadith with book and number.  
The bot remembers the conversation context, so follow‑up questions like “What do you mean by …?” work naturally.

## Features

- **Conversational memory** – the bot understands context from previous exchanges (Flask session‑based)
- **Exact references** – every answer includes precise citations:
  - Quran: surah name and verse number (e.g., “Surah Al‑Baqarah, 2:255”)
  - Hadith: only Sahih (authentic) hadith with book name and number (e.g., “Sahih Bukhari, Book of Faith, Hadith 48”)
- **Beautiful, responsive UI** with AI‑MUFTI branding (book 📖 and mosque 🕌 icons)
- **Print** any Q&A card with a single click
- **Session history** – previous Q&A are displayed during the session; refreshed on page reload
- **No PDFs needed** – purely model‑knowledge based

## Project Structure

```
ai_mufti_web/
├── app.py
├── requirements.txt
├── static/
│   └── style.css
└── templates/
    └── index.html
```

## Setup Guide

### 1. Prerequisites
- Python 3.8 or higher
- A Google API key (obtain from [Google AI Studio](https://makersuite.google.com/app/apikey))

### 2. Install Python & Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Your API Key
Create a `.env` file in the project root and add:
```
GOOGLE_API_KEY=your-google-api-key-here
```

### 5. Run the Application
```bash
python app.py
```
Open your browser and go to `http://127.0.0.1:5000`.

## Usage

1. **Ask a question** in the text area and click **Ask AI‑MUFTI**.
2. The answer appears with an **exact reference** list – each entry is a Quranic verse or a Sahih hadith.
3. **Follow‑up questions** are supported – the bot remembers the conversation. Example:
   - You: “Tell me about Tawheed.”
   - Bot: “Tawheed is … [Surah Al‑Ikhlas, 112:1-4]”
   - You: “What does that surah say exactly?”
   - Bot: “It states: ‘Say, He is Allah, [Who is] One…’”
4. **Print** any answer by clicking **🖨️ Print** on its card – a clean print dialog opens.
5. Session history is displayed automatically; refreshing the page reloads it from the server.

## Code Explanation

### `app.py`
- **Conversational chain**: `RunnableWithMessageHistory` keeps the conversation history keyed by a Flask session ID.
- **System prompt**: Instructs the model to provide exact references and to stick to Sahih hadith only.
- **Routes**:
  - `/` – serves the main HTML page
  - `/ask` (POST) – processes the question, returns JSON with `answer` and `sources`
  - `/history` (GET) – returns all previous Q&A pairs as JSON
  - `/clear_history` (POST) – clears the session memory

### `templates/index.html`
- Dynamically renders Q&A cards with references.
- JavaScript functions:
  - `loadHistory()` – fetches and displays all prior exchanges
  - `askQuestion()` – sends a question, shows a “thinking” indicator, and appends the result
  - `printCard()` – opens a print‑friendly window for a single card
- References are shown as a bullet list with a 📖 icon.

### `static/style.css`
- Defines the warm, scholarly colour palette and layout.
- Styles for header, cards, references (`.sources-box`), buttons, and input area.

## Requirements

- `flask` – web framework
- `langchain` – chain orchestration
- `langchain-google-genai` – Google Gemini integration
- `python-dotenv` – loading environment variables

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `GOOGLE_API_KEY not found` | Ensure `.env` exists and contains the key without extra spaces. |
| Module import errors | Run `pip install -r requirements.txt` in the activated environment. |
| App doesn’t start (port in use) | Change `port=5000` in `app.run()` to another port. |
| History lost when server restarts | History is stored in memory; for persistence, integrate a database. |
| References not precise enough | The model may occasionally generalise; you can adjust the system prompt for stricter instructions. |

*May this tool be a source of authentic and beneficial Islamic knowledge.*
```