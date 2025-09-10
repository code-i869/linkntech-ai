from fastapi import FastAPI
import requests
import os
from pydantic import BaseModel

app = FastAPI()

# ------------------------------
# CONFIGURATION
# ------------------------------
AI_MODE = "ollama"   # "openai" or "ollama"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-key")
OPENAI_MODEL = "gpt-4o-mini"

# ✅ DeepSeek model for Ollama
OLLAMA_MODEL = "deepseek-r1:1.5b"
OLLAMA_URL = "http://localhost:11434/api/generate"

# ------------------------------
# REQUEST BODY
# ------------------------------
class ChatRequest(BaseModel):
    message: str

# ------------------------------
# CHAT ENDPOINT
# ------------------------------
@app.post("/chat")
async def chat(req: ChatRequest):
    user_message = req.message

    if AI_MODE == "openai":
        # ----- OpenAI -----
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        data = {
            "model": OPENAI_MODEL,
            "messages": [{"role": "user", "content": user_message}]
        }
        response = requests.post("https://api.openai.com/v1/chat/completions",
                                 headers=headers, json=data)
        if response.status_code == 200:
            return {"reply": response.json()["choices"][0]["message"]["content"]}
        else:
            return {"error": response.text}

    elif AI_MODE == "ollama":
        # ----- DeepSeek via Ollama -----
        data = {"model": OLLAMA_MODEL, "prompt": user_message}
        response = requests.post(OLLAMA_URL, json=data, stream=False)
        if response.status_code == 200:
            return {"reply": response.json()["response"]}
        else:
            return {"error": response.text}

    else:
        return {"error": "Invalid AI_MODE. Use 'openai' or 'ollama'."}
