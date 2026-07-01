<div align="center">

```
██████╗ ███████╗ █████╗ ██████╗ ██████╗  ██████╗ ████████╗
██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝
██║  ██║█████╗  ███████║██║  ██║██████╔╝██║   ██║   ██║
██║  ██║██╔══╝  ██╔══██║██║  ██║██╔══██╗██║   ██║   ██║
██████╔╝███████╗██║  ██║██████╔╝██████╔╝╚██████╔╝   ██║
╚═════╝ ╚══════╝╚═╝  ╚═╝╚═════╝ ╚═════╝  ╚═════╝    ╚═╝
```

# ⚔️ DeadBot 3000

**Maximum Effort. Maximum Filth. Maximum Correctness.**

A locally-running AI coding assistant with the full unhinged personality of Deadpool.
Rude. Chaotic. Obsessed with chimichangas. But the code is always **100% correct**.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![llama-cpp](https://img.shields.io/badge/llama--cpp--python-local-E63946?style=for-the-badge)](https://github.com/abetlen/llama-cpp-python)
[![Model](https://img.shields.io/badge/Qwen3-4B_Q4__K__M-FFD60A?style=for-the-badge)](https://huggingface.co/Qwen/Qwen3-4B-GGUF)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Maximum Effort](https://img.shields.io/badge/Maximum-Effort-E63946?style=for-the-badge)](https://github.com/AHMED-ESSA007/deadbot-3000)

</div>

---

## 🌯 What is DeadBot 3000?

DeadBot is a **fully local** AI chatbot that runs on your machine — no API keys, no cloud, no subscription fees. It uses **Qwen3-4B-Instruct** quantized to Q4_K_M (GGUF format) via `llama-cpp-python`, served through a **FastAPI** backend with real-time **streaming**, and a custom dark red Deadpool-themed frontend.

It helps you with:
- **Programming questions** — explained with working code and maximum sarcasm
- **Code review** — your code gets roasted AND fixed
- **Error fixing** — paste the error, get the fix + a lecture
- **Code generation** — describe it, get complete working code

All responses start with Deadpool breaking the fourth wall and end with him eating a chimichanga.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💬 **Chat** | Ask anything — Python, JS, life advice, programming jokes |
| 🔍 **Code Review** | Paste code → get bugs found, roasted, and fixed |
| 🔧 **Fix My Error** | Paste error message → get root cause + fixed code |
| ⚡ **Generate Code** | Describe what you want → get complete working code |
| 🔴 **Streaming** | Tokens stream in real-time via SSE — feels instant |
| 🎨 **Deadpool UI** | Dark red/black theme, syntax highlighting via highlight.js |
| 🖥️ **100% Local** | No internet required after setup. Your data stays on your machine |
| 🧠 **Smart Context** | Remembers last 4 conversation turns |
| ⚡ **Optimized** | `use_mmap`, `n_batch=512`, async via `run_in_executor` |

---

## 🛠️ Tech Stack

```
┌─────────────────────────────────────────────┐
│                  FRONTEND                    │
│   Vanilla HTML + CSS + JS + highlight.js    │
│   Server-Sent Events (SSE) streaming        │
└─────────────────┬───────────────────────────┘
                  │ HTTP / SSE
┌─────────────────▼───────────────────────────┐
│                  BACKEND                     │
│   FastAPI + Uvicorn                         │
│   Async streaming with run_in_executor      │
│   4 modes: chat, review, fix, generate      │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│                   MODEL                      │
│   Qwen3-4B-Instruct Q4_K_M (GGUF)          │
│   llama-cpp-python                          │
│   Runs on CPU or GPU                        │
└─────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/AHMED-ESSA007/deadbot-3000.git
cd deadbot-3000
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Linux / Mac
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Download the model
Download **Qwen3-4B-Instruct-Q4_K_M.gguf** from Hugging Face:

👉 https://huggingface.co/Qwen/Qwen3-4B-GGUF

Place it anywhere on your machine and note the full path.

### 5. Set your model path
Open `backend.py` and edit line 20:
```python
MODEL_PATH = "/home/yourname/Downloads/Qwen3-4B-Q4_K_M.gguf"
```

### 6. Run the backend
```bash
python backend.py
```

You should see:
```
Model loaded. DeadBot is armed. Chimichangas: INFINITE.
Uvicorn running on http://0.0.0.0:8000
```

### 7. Open your browser
```
http://localhost:8000
```

---

## 📁 Project Structure

```
deadbot-3000/
│
├── backend.py           # FastAPI backend
│   ├── Model loading    #   Qwen3 GGUF via llama-cpp-python
│   ├── /api/chat        #   Non-streaming endpoint
│   ├── /api/chat/stream #   SSE streaming endpoint
│   └── 4 system prompts #   chat, review, fix, generate
│
├── static/
│   └── index.html       # Full frontend (single file)
│       ├── Chat tab      #   Streaming chat with history
│       ├── Review tab    #   Code review with language selector
│       ├── Fix tab       #   Error fixer
│       └── Generate tab  #   Code generator with examples
│
├── requirements.txt     # Python dependencies
├── .gitignore           # Ignores .gguf, venv, __pycache__
└── README.md            # You are here
```

---

## ⚙️ Configuration

All settings at the top of `backend.py`:

```python
MODEL_PATH   = "/path/to/Qwen3-4B-Q4_K_M.gguf"
N_GPU_LAYERS = 0       # 0 = CPU only | -1 = all layers on GPU
N_CTX        = 8192    # context window (tokens)
N_THREADS    = 8       # CPU threads — set to your core count
N_BATCH      = 512     # batch size — higher = faster prefill
TEMPERATURE  = 0.85    # 0.0 = boring | 1.0 = unhinged
MAX_TOKENS   = 1024    # max response tokens
```

### 🎮 GPU Acceleration (NVIDIA)

```bash
pip install llama-cpp-python \
  --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

Then in `backend.py`:
```python
N_GPU_LAYERS = -1   # load ALL layers onto GPU
```

### 🍎 GPU Acceleration (Apple Silicon)

```bash
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --force-reinstall
```

Then set `N_GPU_LAYERS = -1`.

---

## 🌐 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the frontend UI |
| `GET` | `/health` | Model status + chimichanga count |
| `POST` | `/api/chat` | Full response (waits for complete answer) |
| `POST` | `/api/chat/stream` | Streaming response via SSE |
| `GET` | `/api/modes` | List of available chat modes |

### Request body (`/api/chat` and `/api/chat/stream`)

```json
{
  "message": "How do I reverse a string in Python?",
  "mode": "chat",
  "language": "Python",
  "extra": "",
  "history": []
}
```

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | User's message or code to process |
| `mode` | string | `chat` / `review` / `fix` / `generate` |
| `language` | string | Programming language (for review/fix/generate) |
| `extra` | string | Error message (fix mode) or extra requirements (generate mode) |
| `history` | array | Previous messages `[{role, content}]` |

### Example cURL

```bash
# Chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I reverse a string in Python?", "mode": "chat"}'

# Health check
curl http://localhost:8000/health
```

---

## 💻 Hardware Requirements

| Setup | RAM needed | Speed |
|-------|-----------|-------|
| CPU only (Q4_K_M) | ~4 GB | ~8–15 tokens/sec |
| NVIDIA GPU | ~3 GB VRAM | ~40–80 tokens/sec |
| Apple Silicon (Metal) | ~3 GB unified | ~30–60 tokens/sec |

> **Q4_K_M** is the sweet spot — good quality, small size, runs on most machines.

---

## 🐛 Troubleshooting

**`ValueError: Model path does not exist`**
```bash
# Find your model file
find ~ -name "*.gguf" 2>/dev/null
# Then update MODEL_PATH in backend.py
```

**`Failed to fetch` in browser**
```bash
# Make sure the backend is running
python backend.py
# Then open http://localhost:8000 (not file://)
```

**`Directory 'static' does not exist`**
```bash
mkdir -p static
# Make sure index.html is inside the static/ folder
```

**Model is slow**
```bash
# Increase threads to your CPU core count
N_THREADS = 12   # or whatever your machine has
# Or enable GPU layers if you have a GPU
N_GPU_LAYERS = -1
```

---

## 🗺️ Roadmap

- [ ] Multi-turn conversation memory across sessions
- [ ] Support for more GGUF models (Mistral, LLaMA, Phi)
- [ ] Voice input / output
- [ ] Save and export chat history
- [ ] Docker support
- [ ] More languages in code review

---

## 📜 License

MIT — do whatever you want with it. Deadpool would.

---

## 🙏 Credits

- [Qwen3](https://huggingface.co/Qwen/Qwen3-4B-GGUF) — the brain
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) — the inference engine  
- [FastAPI](https://fastapi.tiangolo.com/) — the backbone
- [highlight.js](https://highlightjs.org/) — syntax highlighting
- **Deadpool** — the personality
- **Chimichangas** — the motivation

---

<div align="center">

**Made with Maximum Effort ⚔️ and zero chill 🌯**

*"With great power comes great need to eat a chimichanga."*

[![GitHub](https://img.shields.io/badge/GitHub-AHMED--ESSA007-181717?style=for-the-badge&logo=github)](https://github.com/AHMED-ESSA007)

</div>
