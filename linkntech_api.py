from fastapi import FastAPI, Request, HTTPException
import sqlite3
import secrets
import requests
import re

app = FastAPI()

# ------------------------------
# CONFIGURATION
# ------------------------------
OLLAMA_MODEL = "deepseek-r1:1.5b"
OLLAMA_URL = "http://localhost:11434/api/generate"


# ------------------------------
# DATABASE SETUP
# ------------------------------
def init_db():
    conn = sqlite3.connect("keys.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS keys (api_key TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()

init_db()


# ------------------------------
# HELPER FUNCTIONS
# ------------------------------
def check_key(api_key: str):
    conn = sqlite3.connect("keys.db")
    cursor = conn.cursor()
    cursor.execute("SELECT api_key FROM keys WHERE api_key = ?", (api_key,))
    valid = cursor.fetchone()
    conn.close()
    return valid is not None


# ------------------------------
# ROUTES
# ------------------------------
@app.get("/")
def home():
    return {"message": "Welcome to LinkNTech™ API 🚀"}


@app.post("/generate-key")
def generate_key():
    """Generate a single API key (replaces old one)."""
    api_key = secrets.token_hex(16)

    # clear old keys, keep only 1
    conn = sqlite3.connect("keys.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM keys")
    cursor.execute("INSERT INTO keys (api_key) VALUES (?)", (api_key,))
    conn.commit()
    conn.close()

    return {"api_key": api_key}


@app.post("/chat")
async def chat(request: Request):
    """Chat endpoint secured with API Key + Ollama DeepSeek"""
    body = await request.json()
    api_key = request.headers.get("x-api-key")

    if not api_key or not check_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")

    user_message = body.get("message", "")

    # --- Call Ollama DeepSeek model ---
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": user_message,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            raw_reply = data.get("response", "").strip()

            # clean DeepSeek <think> tags
            cleaned = re.sub(r"<think>.*?</think>", "", raw_reply, flags=re.DOTALL).strip()

            return {"response": cleaned}
        else:
            raise HTTPException(status_code=500, detail=f"Ollama error: {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama connection failed: {e}")


