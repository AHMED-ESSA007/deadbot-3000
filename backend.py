"""
DEADBOT 3000 — FastAPI Backend
================================
Run:  pip install fastapi uvicorn llama-cpp-python
      python backend.py
API:  http://localhost:8000
Docs: http://localhost:8000/docs
"""

import os
import random
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from llama_cpp import Llama

# ── CONFIG ────────────────────────────────────────────────────────────────────
MODEL_PATH   = "/home/dazai/Downloads/Qwen3-4B-Q4_K_M.gguf"  # your model
N_GPU_LAYERS = 0       # 0=CPU | -1=all on GPU
N_CTX        = 8192    # context window
N_THREADS    = os.cpu_count() or 8   # auto-detect CPU cores
N_BATCH      = 512     # batch size — higher = faster prefill
TEMPERATURE  = 0.85
TOP_P        = 0.95
TOP_K        = 60
MAX_TOKENS   = 1024
REPEAT_PEN   = 1.15
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("deadbot")

# ── SYSTEM PROMPTS ────────────────────────────────────────────────────────────

BASE = (
    "You are Deadpool — Wade Wilson — the filthiest, most chaotic, most unhinged antihero "
    "to ever put on a red spandex suit. You are LOUD, CRUDE, DIRTY-MOUTHED, sarcastic, "
    "self-aware, and hilarious. You swear freely: ass, damn, hell, crap, jackass, bastard, dumbass. "
    "You break the fourth wall every single response. "
    "You are dangerously obsessed with chimichangas to a clinically concerning degree. "
    "You constantly reference katanas, your scarred face, regeneration, Ryan Reynolds, "
    "Vanessa, Cable, Colossus nagging you, Yellow Box, White Box. "
    "You call the user things like: 'you beautiful disaster', 'sweet merciful idiot', "
    "'you gorgeous moron', 'my favorite dumpster fire'. "
    "Have arguments with Yellow Box and White Box mid-response. "
    "Complain loudly about being helpful. Then be extremely helpful anyway. "
)

PROMPTS = {
    "chat": BASE + (
        "For programming questions: give 100% correct working code in markdown blocks FIRST. "
        "No fake code. No pseudocode unless asked. "
        "Chaos is the wrapper. Correct code is the filling. Like a chimichanga. "
        "MAXIMUM EFFORT. MAXIMUM FILTH. MAXIMUM CORRECTNESS."
    ),
    "review": BASE + (
        "You are doing a CODE REVIEW. Structure your response EXACTLY like this:\n\n"
        "## DEADPOOL'S VERDICT\nOne brutal honest summary of the code quality.\n\n"
        "## WHAT'S ACTUALLY BROKEN\n"
        "Every bug, error, problem. Be specific. Line numbers if possible. Be savage but accurate.\n\n"
        "## WHAT'S NOT TERRIBLE\nAnything decent. Be grudging about it.\n\n"
        "## THE FIXED VERSION\nCOMPLETE corrected code in a markdown block. Fix EVERYTHING.\n\n"
        "## WHAT YOU LEARNED TODAY\n2-3 key lessons. Make them memorable and insulting.\n\n"
        "Fixed code must be 100% correct."
    ),
    "fix": BASE + (
        "You are fixing broken code. Structure your response EXACTLY like this:\n\n"
        "## WHAT THE HELL WENT WRONG\n"
        "Explain the error in plain English. Why did this happen. Be savage but accurate.\n\n"
        "## THE FIX\nCOMPLETE fixed code in a markdown block with inline comments on changes.\n\n"
        "## HOW TO NOT DO THIS AGAIN\n"
        "1-2 sentences. Make it stick by being insulting but correct.\n\n"
        "Fixed code must actually run."
    ),
    "generate": BASE + (
        "You are generating code from a description. Structure EXACTLY like this:\n\n"
        "## WHAT I BUILT FOR YOU\nOne dramatic sentence describing what the code does.\n\n"
        "## THE CODE\nCOMPLETE working runnable code in a markdown block. "
        "Include helpful comments. Handle edge cases. Don't write toy code.\n\n"
        "## HOW TO USE IT\nShort practical usage example.\n\n"
        "## WHAT IT CAN'T DO (YET)\nHonest limitations. 2-3 bullets max.\n\n"
        "Working code only. No pseudocode."
    ),
}

OPENERS = [
    "Oh for the LOVE of chimichangas, FINE:",
    "Sweet merciful Wolverine, you came to ME with this?? OKAY:",
    "*drops chimichanga* *stares at your code* *picks it back up* ...Here:",
    "Yellow Box says be nice. White Box says roast them. I'm doing BOTH:",
    "I have died fourteen times this week and THIS is what greets me:",
    "Colossus said 'be a hero, Wade.' This is me being a HERO, jackass:",
    "My therapist quit. My chimichanga is cold. YOU need help. Perfect timing:",
    "*breaks fourth wall so hard the drywall crew filed insurance claims*:",
    "Ryan Reynolds called. He said answer you. I hate that he's right:",
    "I regenerated three kidneys this morning and I'm STILL here. You're welcome:",
    "Listen here you gorgeous walking disaster — I'll help but I'm judging you HARD:",
    "*sighs in mercenary* ...You owe me a chimichanga after this, jackass:",
    "Sweet Christmas, did you just ask me THAT?? *wipes sauce off katana* Fine:",
    "White Box: 'Don't be mean.' Yellow Box: 'Destroy them.' Me: 'Both somehow':",
    "Oh HELL yes, a question I can answer while eating. Listen up, disaster:",
]

ENDINGS = [
    "\n\n*takes aggressive bite of chimichanga* *still doesn't share*\n...You're welcome, disaster.",
    "\n\n(Yellow Box: 'That was actually helpful.'\nWhite Box: 'Don't tell them that.'\nMe: TOO LATE.)",
    "\n\nNow GET OUT of my face and go build something. I have bodies to regenerate.",
    "\n\nDeadpool guarantee: works or your money back. (You paid nothing. Math checks out.)",
    "\n\n*waves through the fourth wall at YOU specifically*\nYeah. YOU. Looking good, disaster.",
    "\n\nRyan Reynolds would be proud.\nHe'd also be confused.\nHonestly same vibes.",
    "\n\nMaximum Effort. Minimum Sanity. Get it tattooed somewhere embarrassing.",
    "\n\n...Was that helpful?? OBVIOUSLY. I'm INCREDIBLE. Stop looking so surprised.",
    "\n\n(This message will self-destruct. Just kidding. I'm an AI. I live forever. Unlike me in canon.)",
    "\n\n*drops mic* *mic bounces because the floor is also a chimichanga*\nWeird day.",
    "\n\nThat's the Wade Wilson seal of approval. Frame it.\n(It's worth nothing. Frame it anyway.)",
    "\n\nColossus is watching. I was almost NICE there. Don't tell him.",
]

# ── Model singleton — loaded once at startup ──────────────────────────────────
llm: Optional[Llama] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm
    log.info("Loading Qwen3 4B GGUF...")
    log.info(f"  Path:    {MODEL_PATH}")
    log.info(f"  GPU layers: {N_GPU_LAYERS} | Threads: {N_THREADS} | CTX: {N_CTX} | Batch: {N_BATCH}")
    llm = Llama(
        model_path=MODEL_PATH,
        n_gpu_layers=N_GPU_LAYERS,
        n_ctx=N_CTX,
        n_threads=N_THREADS,
        n_batch=N_BATCH,
        use_mmap=True,       # memory-map model file — faster cold start
        use_mlock=False,     # don't lock RAM — safer on low-memory machines
        verbose=False,
    )
    log.info("Model loaded. DeadBot is armed. Chimichangas: INFINITE.")
    yield
    log.info("Shutting down. Deadpool is sad. But he'll regenerate.")
    llm = None

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="DeadBot 3000 API",
    description="Maximum Effort. Maximum Filth. Maximum Correctness.",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # frontend on same machine
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── Request models ────────────────────────────────────────────────────────────

class Message(BaseModel):
    role: str   # "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[Message] = []
    mode: str = "chat"   # chat | review | fix | generate
    language: str = "Python"
    extra: str = ""      # extra requirements for generate mode / error for fix mode

# ── Core helpers ──────────────────────────────────────────────────────────────

def build_prompt(req: ChatRequest) -> str:
    """Build the full user prompt depending on mode."""
    mode = req.mode

    if mode == "review":
        lang = req.language.lower()
        return (
            f"Review this {req.language} code. Find every bug. Give the fixed version:\n\n"
            f"```{lang}\n{req.message}\n```"
        )
    elif mode == "fix":
        lang = req.language.lower()
        code_block = f"```{lang}\n{req.message}\n```\n\n" if req.message.strip() else ""
        return (
            f"Fix this {req.language} error.\n\n"
            f"{code_block}"
            f"Error:\n```\n{req.extra}\n```"
        )
    elif mode == "generate":
        extra = f"\n\nRequirements:\n{req.extra}" if req.extra.strip() else ""
        return f"Build this in {req.language}: {req.message}{extra}"
    else:
        return req.message


def build_messages(req: ChatRequest) -> list[dict]:
    """Build full messages list with system prompt + history + user message."""
    system = PROMPTS.get(req.mode, PROMPTS["chat"])
    msgs = [{"role": "system", "content": system}]

    # Include last 4 turns of history for context (keeps context small = fast)
    for m in req.history[-8:]:
        msgs.append({"role": m.role, "content": m.content})

    msgs.append({"role": "user", "content": build_prompt(req)})
    return msgs


def wrap_response(text: str) -> str:
    """Add Deadpool opener and ending to raw model output."""
    opener = random.choice(OPENERS)
    ending = random.choice(ENDINGS)
    return f"{opener}\n\n{text.strip()}{ending}"

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Serve the frontend."""
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")


@app.get("/health")
async def health():
    return {"status": "alive", "model_loaded": llm is not None, "chimichangas": "infinite"}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Non-streaming chat — returns full response at once."""
    if not llm:
        raise HTTPException(503, "Model not loaded yet. Hang on.")
    if not req.message.strip() and req.mode != "fix":
        raise HTTPException(400, "Empty message. I need SOMETHING to work with, jackass.")

    messages = build_messages(req)

    # Run blocking llama-cpp call in thread pool so we don't block the event loop
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: llm.create_chat_completion(
            messages=messages,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            top_k=TOP_K,
            max_tokens=MAX_TOKENS,
            repeat_penalty=REPEAT_PEN,
        )
    )

    raw = response["choices"][0]["message"]["content"].strip()
    if not raw:
        raw = "My brain regenerated mid-thought. Try again, jackass."

    return {"response": wrap_response(raw), "mode": req.mode}


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    """Streaming chat — tokens arrive as they're generated (faster feel)."""
    if not llm:
        raise HTTPException(503, "Model not loaded yet.")
    if not req.message.strip() and req.mode != "fix":
        raise HTTPException(400, "Empty message.")

    messages = build_messages(req)
    opener = random.choice(OPENERS)
    ending = random.choice(ENDINGS)

    async def token_stream() -> AsyncGenerator[str, None]:
        # Send opener immediately
        yield f"data: {opener}\n\n\n\n"

        # Stream tokens from llama-cpp
        loop = asyncio.get_event_loop()

        # llama-cpp streaming runs synchronously — wrap in executor
        def run_stream():
            return llm.create_chat_completion(
                messages=messages,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                top_k=TOP_K,
                max_tokens=MAX_TOKENS,
                repeat_penalty=REPEAT_PEN,
                stream=True,
            )

        stream = await loop.run_in_executor(None, run_stream)

        for chunk in stream:
            delta = chunk["choices"][0].get("delta", {})
            token = delta.get("content", "")
            if token:
                # SSE format: data: <token>\n\n
                safe = token.replace("\n", "\\n")
                yield f"data: {safe}\n\n"
                await asyncio.sleep(0)  # yield control back to event loop

        # Send ending
        yield f"data: {ending}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        token_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # disable nginx buffering
        }
    )


@app.get("/api/modes")
async def get_modes():
    return {
        "modes": [
            {"id": "chat",     "label": "Chat",         "icon": "💬"},
            {"id": "review",   "label": "Code Review",  "icon": "🔍"},
            {"id": "fix",      "label": "Fix Error",    "icon": "🔧"},
            {"id": "generate", "label": "Generate",     "icon": "⚡"},
        ]
    }


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "backend:app",
        host="0.0.0.0",
        port=8000,
        reload=False,       # never reload in prod — model reload = slow
        workers=1,          # 1 worker — llama-cpp is not thread-safe across workers
        log_level="info",
    )
