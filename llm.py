import os
import openai
import subprocess
import requests
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
AIPROXY_TOKEN = os.getenv("AIPIPE_TOKEN")
AIPIPE_TOKEN = os.getenv("AIPIPE_TOKEN")
GROK_API_KEY = os.getenv("GROK_API_KEY")

# Models
OR_MODEL = "deepseek/deepseek-chat-v3-0324:free"
OR_PROXY_MODEL = "deepseek/deepseek-chat-v3-0324"
OA_PROXY_MODEL = "gpt-4.1-nano"

MODEL = "codellama:latest" 
GROQ_MODEL = "openai/gpt-oss-20b"

# ========== LLM via Grok (personal) ==========
def call_grok(prompt: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }

    response = requests.post(url, headers=headers, json=data, timeout=120)
    try:
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Groq Error]: {e} | Raw: {response.text}"

# ========== LLM via OpenRouter (personal) ==========
def call_openrouter(prompt: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": OR_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }

    response = requests.post(url, headers=headers, json=data, timeout=120)
    try:
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[OpenRouter Error]: {e} | Raw: {response.text}"


# ========== LLM via OpenRouter Proxy (TDS AI Pipe) ==========
def call_openrouter_proxy(prompt: str) -> str:
    API_URL = "https://aipipe.org/openrouter/v1/chat/completions"

    headers = {
        "Authorization": f"{AIPIPE_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": OR_PROXY_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()  # Raise error if request failed
    data = response.json()

    # Extract model output
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return f"Unexpected response: {data}"


# ========== LLM via OpenAI Proxy (TDS AI Proxy) ==========
def call_openai_proxy(prompt):
    API_URL = "https://aipipe.org/openai/v1/responses"

    headers = {
        "Authorization": f"{AIPIPE_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": OA_PROXY_MODEL,
        "input": prompt
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()  # Raise error if request failed
    data = response.json()

    try:
        # Extract assistant text
        return data["output"][0]["content"][0]["text"]
    except (KeyError, IndexError):
        return f"Unexpected response format: {data}"


# ========== Local LLM via Ollama ==========
def call_ollama(prompt: str) -> str: # Change if needed

    try:
        result = subprocess.run(
            ["ollama", "run", MODEL],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=90
        )

        if result.returncode != 0:
            return f"[Ollama Error]: {result.stderr.decode().strip()}"
        return result.stdout.decode().strip()

    except subprocess.TimeoutExpired:
        return "[Ollama Error]: Model timed out"
    except Exception as e:
        return f"[Ollama Exception]: {e}"

# ========== Groq LLM via OpenAI API ==========
def call_groq(prompt: str) -> str:
    """
    Send a prompt to Groq LLaMA 3 model and return the response text.
    """
    # Load environment variables
    load_dotenv()

    # Create Groq client
    client = openai.OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=GROK_API_KEY
    )

    # Send request
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=512
    )

    return response.choices[0].message.content.strip()

# ===== Global State for Fallback =====
use_direct_openrouter = False  # Start with proxy, switch to direct if proxy fails

def call_llm_with_fallback(prompt: str) -> str:
    """
    Try OpenRouter Proxy first; on failure, switch permanently to direct OpenRouter API.
    """
    global use_direct_openrouter

    if not use_direct_openrouter:
        # Attempt Proxy Call
        try:
            response = call_openrouter_proxy(prompt)
            # If response is empty or suspicious, treat as failure
            if not response or "Unexpected response" in response:
                raise RuntimeError("Empty/Unexpected Proxy response")
            return response
        except Exception as e:
            print(f"⚠️ Proxy call failed, switching to direct OpenRouter. Error: {e}")
            use_direct_openrouter = True  # Switch permanently

    # Fallback to direct OpenRouter
    try:
        return call_openrouter(prompt)
    except Exception as e:
        return f"[Direct OpenRouter Error]: {e}"


# ========== Example Test ==========
if __name__ == "__main__":
    test_prompt = "Explain the importance of clean energy in two sentences."

    print("\n🧪 Prompt:\n", test_prompt)

    try:
        print(call_grok(test_prompt))
    except Exception as e:
        print("❌ OpenRouter Error:", e)