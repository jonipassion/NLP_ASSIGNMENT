import os
import json
import random
import socket
import time
import threading
import webbrowser
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, validator
from openai import OpenAI
import requests
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem

client = OpenAI() 
templates = Jinja2Templates(directory="templates")

app = FastAPI(
    title="Educational Quiz API",
    description="Generates structured educational quizzes with multiple difficulty levels",
    version="1.0"
)

@app.get("/", response_class=HTMLResponse)
async def index_redirect():
    """Redirect root URL to /ui."""
    return RedirectResponse(url="/ui")

@app.get("/ui", response_class=HTMLResponse)
async def serve_ui(request: Request):
    """Serve main quiz page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health():
    """Health check for readiness."""
    return {"status": "ok"}


CONVO_DIR = "conversations"
os.makedirs(CONVO_DIR, exist_ok=True)

def conversation_file(session_id: str) -> str:
    return os.path.join(CONVO_DIR, f"{session_id}.json")

def load_conversation(session_id: Optional[str] = None):
    """Load or create a new LLM conversation."""
    base_system_msg = {
        "role": "system",
        "content": (
            "You are a helpful AI assistant that ONLY generates educational quizzes. "
            "Output JSON only — an array of questions. "
            "Each question object must include: question, type, options (if multiple-choice), answer, and difficulty."
        )
    }

    if not session_id:
        session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
        return session_id, [base_system_msg]

    path = conversation_file(session_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            messages = json.load(f)
    else:
        messages = [base_system_msg]
    return session_id, messages

def save_conversation(session_id: str, messages: List[dict]):
    path = conversation_file(session_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)

ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}
FORBIDDEN_WORDS = ["gambling", "politics", "violence", "porn", "drugs"]

class QuizRequest(BaseModel):
    topic: str
    difficulties: Optional[List[str]] = ["medium"]
    hide_answers: Optional[bool] = False
    session_id: Optional[str] = None

    @validator("topic")
    def topic_must_be_safe(cls, v):
        if not v.strip():
            raise ValueError("Topic cannot be empty")
        if len(v) > 100:
            raise ValueError("Topic too long (max 100 characters)")
        if any(word in v.lower() for word in FORBIDDEN_WORDS):
            raise ValueError("Topic contains non-educational content")
        return v.strip()

    @validator("difficulties", each_item=True)
    def validate_difficulties(cls, v):
        if v.lower() not in ALLOWED_DIFFICULTIES:
            raise ValueError(f"Invalid difficulty '{v}'. Allowed: {ALLOWED_DIFFICULTIES}")
        return v.lower()

class QuizQuestion(BaseModel):
    question: str
    type: str 
    options: Optional[List[str]] = None
    answer: str
    difficulty: Optional[str] = None
    show_answer: Optional[bool] = True

class QuizResponse(BaseModel):
    topic: str
    quiz: List[QuizQuestion]
    session_id: str

def query_llm(messages: List[dict]) -> str:
    """Call the OpenAI API safely and return raw text."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def parse_quiz_json(quiz_str: str) -> List[QuizQuestion]:
    """Parse LLM quiz JSON output into structured questions."""
    try:
        quiz_str = quiz_str.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(quiz_str)
        if not isinstance(data, list):
            raise ValueError("Expected a list of questions")
        questions = []
        for q in data:
            difficulty = q.get("difficulty", "medium")
            questions.append(
                QuizQuestion(
                    question=q["question"],
                    type=q["type"],
                    options=q.get("options"),
                    answer=q["answer"],
                    difficulty=difficulty,
                    show_answer=q.get("show_answer", True)
                )
            )
        return questions
    except Exception as e:
        print("JSON parse failed:", e)
        return [QuizQuestion(question=quiz_str, type="short-answer", answer="(Error parsing quiz)", difficulty="medium")]

def shuffle_multiple_choice(questions: List[QuizQuestion]) -> List[QuizQuestion]:
    for q in questions:
        if q.type == "multiple-choice" and q.options:
            if q.answer not in q.options:
                q.options.append(q.answer)
            random.shuffle(q.options)
    return questions

@app.post("/quiz")
async def generate_quiz(req: QuizRequest):
    """Generate an educational quiz."""
    session_id, messages = load_conversation(req.session_id)

    messages.append({
        "role": "user",
        "content": (
            f"Create a JSON quiz about '{req.topic}' "
            f"with {', '.join(req.difficulties)} difficulty questions. "
            "Each question must include question, type, options (if applicable), answer, and difficulty."
        )
    })

    raw_output = query_llm(messages)

    if raw_output.startswith("Error:"):
        print(raw_output)
        raise HTTPException(status_code=500, detail="OpenAI API error")

    print("Raw LLM output:\n", raw_output[:300])  # show partial for debugging

    questions = parse_quiz_json(raw_output)
    questions = shuffle_multiple_choice(questions)
    save_conversation(session_id, messages)

    return QuizResponse(topic=req.topic, quiz=questions, session_id=session_id)

def generate_quiz_pdf(topic: str, questions: List[QuizQuestion], hide_answers: bool = False) -> str:
    """Generate and save a quiz PDF."""
    os.makedirs("exports", exist_ok=True)
    filename = f"quiz_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join("exports", filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(f"<b>Quiz Topic:</b> {topic.title()}", styles["Title"]),
        Spacer(1, 0.3 * inch)
    ]

    for i, q in enumerate(questions, 1):
        story.append(Paragraph(f"<b>{i}. {q.question}</b>", styles["Normal"]))
        if q.type == "multiple-choice" and q.options:
            story.append(ListFlowable([ListItem(Paragraph(opt, styles["Normal"])) for opt in q.options]))
        if not hide_answers:
            story.append(Paragraph(f"<i>Answer:</i> {q.answer}", styles["Italic"]))
        story.append(Spacer(1, 0.2 * inch))

    doc.build(story)
    return filepath

@app.post("/generate_pdf", response_class=FileResponse)
async def generate_pdf_endpoint(req: QuizRequest):
    """Generate a quiz and return downloadable PDF."""
    session_id, messages = load_conversation(req.session_id)
    messages.append({"role": "user", "content": f"Create a quiz about {req.topic}."})
    raw_output = query_llm(messages)
    questions = parse_quiz_json(raw_output)
    questions = shuffle_multiple_choice(questions)
    save_conversation(session_id, messages)
    pdf_path = generate_quiz_pdf(req.topic, questions, hide_answers=req.hide_answers)
    return FileResponse(pdf_path, filename=os.path.basename(pdf_path), media_type="application/pdf")

# -----------------------------------------------------
# AUTO OPEN UI (DEV MODE ONLY)
# -----------------------------------------------------
@app.on_event("startup")
def open_ui():
    """Open the browser automatically on startup in development."""
    env_mode = os.getenv("APP_ENV", "development").lower()
    if env_mode != "development":
        print("Skipping auto-browser launch (production mode).")
        return

    def _open_browser():
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except:
            ip = "127.0.0.1"

        url = f"http://{ip}:8000/ui"
        health_url = f"http://{ip}:8000/health"

        print(f"Waiting for FastAPI to start at {health_url} ...")
        for _ in range(20):
            try:
                r = requests.get(health_url, timeout=0.5)
                if r.status_code == 200:
                    print(f"Server is ready at {url}")
                    break
            except:
                pass
            time.sleep(0.5)

        print(f"Opening browser at {url}")
        try:
            webbrowser.get("xdg-open").open(url)
        except:
            webbrowser.open(url)

    threading.Thread(target=_open_browser).start()
