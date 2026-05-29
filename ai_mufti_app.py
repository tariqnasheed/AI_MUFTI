# ai_mufti_app.py
# Flask web application for AI-MUFTI – Islamic Q&A Bot.
# Uses Google Gemini with conversational memory.
# Answers follows proper references (Quran surah/verses, Sahih Hadith with book/number).
# Features: session‑based chat history, print, save.

import os
import json
import uuid
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, jsonify
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# -------------------------------------------------------------------
# Load environment variables
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError("GOOGLE_API_KEY not found. Set it in .env file.")

# -------------------------------------------------------------------
# Define the JSON output model
class QuranAnswer(BaseModel):
    answer: str = Field(description="Concise answer to the user's question")
    sources: list[str] = Field(
        description="List of references with exact Quran surah/verse or Sahih Hadith book and number"
    )

parser = JsonOutputParser(pydantic_object=QuranAnswer)

# -------------------------------------------------------------------
# System prompt – Deoband perspective, precise references, conversational
system_prompt = """You are a knowledgeable Islamic scholar from the Deoband school of thought.
Answer the user's question concisely and accurately using your own knowledge of the Noble Quran and Islamic history.
When answering:
- Always provide exact references in the "sources" list.
- For Quranic references, include the surah name and verse number (e.g., "Surah Al-Baqarah, 2:255").
- For hadith, cite only Sahih (authentic) hadith from the major collections (e.g., Sahih Bukhari, Sahih Muslim).
  Include the book name, hadith number, and if possible the chapter (e.g., "Sahih Bukhari, Book of Faith, Hadith 48").
- If you are unsure about a specific hadith's authenticity, clearly state that it is not a Sahih hadith.
- Use the conversation history to understand follow‑up questions and provide coherent, context‑aware answers.
You must reply in a clean JSON object with exactly two keys:
  "answer": a string containing your answer,
  "sources": a list of strings that provide the exact references as described.
Do not include any text outside the JSON object."""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="history"),   # Will be filled by the wrapper
    ("human", "{question}")                         # Only the question needs to be provided
])

# -------------------------------------------------------------------
# Initialise the model once
model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0,
    convert_system_message_to_human=True
)

# Core chain: only needs the "question" input; history is injected automatically
core_chain = prompt | model | parser

# -------------------------------------------------------------------
# In‑memory store for chat histories (keyed by session_id)
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Retrieve or create an in‑memory chat history for a given session_id."""
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# Wrap the core chain with automatic history management
chain_with_history = RunnableWithMessageHistory(
    core_chain,
    get_session_history,
    input_messages_key="question",    # Key in the input dict that holds the human message
    history_messages_key="history"    # Key in the prompt template that receives the history
)

# -------------------------------------------------------------------
# Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)   # Required for Flask session cookies

# -------------------------------------------------------------------
# Route: home page
@app.route("/")
def index():
    return render_template("index.html")

# -------------------------------------------------------------------
# API endpoint: ask a question (with conversation memory)
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "No question provided."}), 400

    # Use a persistent session ID. If not yet set, create one.
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    session_id = session["session_id"]

    try:
        # Invoke the wrapped chain – the wrapper will load/save history automatically
        result = chain_with_history.invoke(
            {"question": question},
            config={"configurable": {"session_id": session_id}}
        )
    except Exception as e:
        result = {"answer": f"Sorry, an error occurred: {e}", "sources": []}

    return jsonify(result)

# -------------------------------------------------------------------
# API endpoint: get full conversation history (as list of Q&A pairs)
@app.route("/history")
def history():
    if "session_id" not in session:
        return jsonify([])
    session_id = session["session_id"]
    chat_history = get_session_history(session_id)
    messages = chat_history.messages
    qa_pairs = []
    i = 0
    while i < len(messages):
        if messages[i].type == "human":
            question = messages[i].content
            answer = ""
            sources = []
            # The next message should be an AI reply (JSON string)
            if i + 1 < len(messages) and messages[i + 1].type == "ai":
                try:
                    # The AI message content is a string; parse JSON
                    parsed = json.loads(messages[i + 1].content)
                    answer = parsed.get("answer", "")
                    sources = parsed.get("sources", [])
                except json.JSONDecodeError:
                    answer = messages[i + 1].content
                i += 2
            else:
                i += 1
            qa_pairs.append({
                "question": question,
                "answer": answer,
                "sources": sources
            })
        else:
            i += 1
    return jsonify(qa_pairs)

# -------------------------------------------------------------------
# API endpoint: clear conversation history
@app.route("/clear_history", methods=["POST"])
def clear_history():
    if "session_id" in session:
        session_id = session.pop("session_id")
        store.pop(session_id, None)
    return jsonify({"status": "cleared"})

# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)