# AI-MUFTI – Islamic Q&A Bot (Web GUI)

A fully conversational web application for asking questions about the Noble Quran and Islamic history.  
Built with **Flask**, **HTML/CSS/JavaScript**, and **Google Gemini**.  
Answers follow the **Deoband school of thought** and include **exact references** – Quranic surah/verse and **Sahih** hadith with book name and number.  
The bot remembers the conversation, so follow‑up questions like “What do you mean by …?” work naturally.

## Features

- **Conversational memory** – the bot understands context from previous exchanges (Flask session‑based)
- **Precise references** – every answer includes:
  - Quran: surah name and verse number (e.g., “Surah Al‑Baqarah, 2:255”)
  - Hadith: only Sahih (authentic) hadith with book and number (e.g., “Sahih Bukhari, Book of Faith, Hadith 48”)
- **Beautiful, responsive UI** with a full‑screen Islamic geometric background
  - Decorative font for “AI‑MUFTI” header and calligraphic font for the subtitle
  - Custom logo image next to the header
  - Print any Q&A card with one click
- **Session history** displayed automatically – refreshed on page reload
- **No PDFs needed** – purely model‑knowledge based

## Project Structure

```
AI_MUFTI/
├── app.py
├── requirements.txt
├── readme.md
├── .env.example
├── static/
│   ├── style.css
│   ├── bg.jpg          (your background image)
│   └── logo.png        (your logo image)
└── templates/
    └── index.html
```

## Setup Guide

### 1. Prerequisites
- Python 3.8 or higher
- A Google API key (obtain from [Google AI Studio](https://makersuite.google.com/app/apikey))

### 2. Clone or download the project
```bash
git clone https://github.com/tariqnasheed/AI_MUFTI.git
cd AI_MUFTI
```

### 3. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Set your API key
Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your-google-api-key-here
```
(There is an example file `.env.example` you can copy.)

### 6. Add background and logo images (optional)
Place your own `bg.jpg` (background) and `logo.png` (header logo) inside the `static/` folder.  
If you don’t add them, the app will still work – the background will show a warm plain color and the header will display 📖🕌 emojis.

### 7. Run the application
```bash
python app.py
```
Open your browser and go to **http://127.0.0.1:5000**.

## Usage

1. **Ask a question** in the text area and click **🔍 Ask AI‑MUFTI**.
2. The answer appears in a card, with an exact reference list (Quran verse / Sahih hadith).
3. **Follow‑up questions** are supported – the bot remembers your previous conversation.
   - Example:
     - You: *Tell me about Tawheed.*
     - Bot: *Tawheed is … (Surah Al‑Ikhlas, 112:1-4)*
     - You: *What does that surah say exactly?*
     - Bot: *It says: “Say, He is Allah, [Who is] One…”*
4. **Print** any answer by clicking **🖨️ Print** on its card – a clean print dialog opens.
5. **Session history** appears automatically; refreshing the page reloads the entire conversation from the server.

## File Descriptions

### `app.py`
- Main Flask application.
- Loads the Google Gemini model and builds the LangChain chain with `RunnableWithMessageHistory` for conversational memory.
- Routes:
  - `/` → serves the HTML page.
  - `/ask` (POST) → accepts a JSON `{"question": "…"}`, invokes the chain, returns `{"answer": "…", "sources": […]}`.
  - `/history` (GET) → returns all Q&A pairs stored in the current session.
  - `/clear_history` (POST) → clears the session.
- The system prompt instructs the model to use the Deoband perspective and to provide exact, Sahih references.

### `templates/index.html`
- Frontend structure and dynamic JavaScript.
- Calls `/history` on page load to display previous chats.
- Sends new questions via `fetch` to `/ask`.
- Displays references as a styled bullet list (📖 icon).
- Includes a print button that opens a printer‑friendly window.

### `static/style.css`
- Defines the whole visual appearance.
- Uses a full‑screen background image (`bg.jpg`) with a semi‑transparent overlay for readability.
- Custom fonts: *Cinzel Decorative* for the header, *Rochester* for the subtitle, *Georgia* for body text.
- Styles for cards, references, input area, and scrollbars.

### `requirements.txt`
```
flask
langchain
langchain-google-genai
python-dotenv
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `flask` | Web framework, routing, session management |
| `langchain` | Core chain orchestration and prompt templates |
| `langchain-google-genai` | Google Gemini chat model (`gemini-3.5-flash`) |
| `python-dotenv` | Loads the API key from `.env` |

## How Conversation History Works

1. When you first load the app, Flask generates a unique `session_id` stored in a browser cookie.
2. Each time you ask a question, `RunnableWithMessageHistory` loads the previous chat history (an `InMemoryChatMessageHistory` object keyed by the session ID) and appends the new exchange.
3. The history is injected into the prompt via a `MessagesPlaceholder`, so the model sees all past messages.
4. The `/history` route reads the history and returns it to the frontend for display.

This allows follow‑up questions like “Can you elaborate?” or “What does that verse say?” because the model “remembers” what was just discussed.

## Customisation

- **Change the theological perspective**: edit the `system_prompt` variable in `app.py`.
- **Replace background**: put a new `bg.jpg` in `static/`. Adjust the CSS overlay opacity in `body::before` if needed.
- **Change fonts**: modify the Google Fonts link in `index.html` and the `font-family` properties in `style.css`.
- **Use a different Gemini model**: in `app.py`, replace `gemini-1.5-flash` with `gemini-1.5-pro` or another model.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `GOOGLE_API_KEY not found` | Make sure `.env` exists and contains `GOOGLE_API_KEY=...` without spaces. |
| Module import errors | Run `pip install -r requirements.txt` inside the virtual environment. |
| Port 5000 already in use | Change `port=5000` in `app.run()` to another port, e.g., `app.run(debug=True, port=8080)`. |
| History lost on server restart | History is stored in memory. For persistence, replace `InMemoryChatMessageHistory` with a database‑backed implementation. |
| Background image not showing | Verify `bg.jpg` is inside the `static/` folder and the filename matches exactly in the CSS. Clear your browser cache. |
| “I don’t have enough information” appears often | The model may not have relevant data in its training. Try rephrasing the question or switching to `gemini-1.5-pro` for more knowledge. |
| References not precise enough | Refine the `system_prompt` to demand stricter citations. Example: “You MUST include the surah name and verse number, and for hadith, include the book and number.” |

## Deoband Perspective

All prompts enforce the Deoband school of thought. To change this, modify the `system_prompt` in `app.py`.  
The app is intended for educational and spiritual purposes, grounded in authentic Islamic sources.

## Credits

Developed by [Tariq Nasheed](https://github.com/tariqnasheed).  
Powered by Google Gemini and the LangChain framework.

---

*May this tool be a source of authentic and beneficial Islamic knowledge.*
```