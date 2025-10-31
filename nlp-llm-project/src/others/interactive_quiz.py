import os
import json
from datetime import datetime
from gpt_client import client

QUIZ_DIR = "quizzes"
os.makedirs(QUIZ_DIR, exist_ok=True)

def generate_quiz(topic, num_questions=5):
    """Generate a quiz with explanations and autosave"""
    prompt = f"""
    Create a {num_questions}-question multiple-choice quiz on "{topic}".
    Format as JSON:
    [
      {{
        "question": "...",
        "options": ["A","B","C","D"],
        "answer": "B",
        "explanation": "Explain why this answer is correct."
      }},
      ...
    ]
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an educational assistant creating quizzes with explanations."},
            {"role": "user", "content": prompt}
        ]
    )
    quiz_text = response.choices[0].message.content
    try:
        quiz = json.loads(quiz_text)
    except json.JSONDecodeError:
        print("⚠️ Failed to parse JSON:\n", quiz_text)
        return []

    # Autosave immediately
    filename = os.path.join(QUIZ_DIR, f"quiz_{topic.replace(' ','_')}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(quiz, f, indent=2, ensure_ascii=False)
    print(f"💾 Quiz auto-saved to {filename}")
    return quiz

def load_quiz():
    files = [f for f in os.listdir(QUIZ_DIR) if f.endswith(".json")]
    if not files:
        print("No saved quizzes found.")
        return None

    print("📁 Saved quizzes:")
    for i, f in enumerate(files, 1):
        print(f"{i}. {f}")

    choice = input("Enter number to load or press Enter to cancel: ").strip()
    if not choice:
        return None
    try:
        idx = int(choice) - 1
        filename = os.path.join(QUIZ_DIR, files[idx])
        with open(filename, "r", encoding="utf-8") as f:
            quiz = json.load(f)
        print(f"✅ Loaded quiz: {files[idx]}")
        return quiz
    except:
        print("❌ Invalid choice.")
        return None

def take_quiz(quiz):
    """Interactive quiz with optional hints"""
    score = 0
    for i, q in enumerate(quiz, 1):
        print(f"\nQ{i}: {q['question']}")
        for idx, opt in enumerate(q['options'], 1):
            print(f"  {chr(64+idx)}. {opt}")

        while True:
            user_answer = input("Your answer (A/B/C/D) or type '/hint': ").strip().upper()
            if user_answer == "/HINT":
                hint_prompt = f"Provide a short hint for this question: {q['question']}"
                hint_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful tutor providing hints."},
                        {"role": "user", "content": hint_prompt}
                    ]
                )
                print(f"💡 Hint: {hint_response.choices[0].message.content}")
                continue
            if user_answer in ["A","B","C","D"]:
                break
            print("❌ Invalid input. Enter A/B/C/D or '/hint'.")

        correct_answer = q['answer'].upper()
        if user_answer == correct_answer:
            print("✅ Correct!")
            score += 1
        else:
            print(f"❌ Wrong! Correct answer: {correct_answer}")
        print(f"💡 Explanation: {q.get('explanation','No explanation available.')}\n")

    print(f"\n🎉 Quiz complete! Score: {score}/{len(quiz)}")

def quiz_flow():
    print("\n1. Generate new quiz\n2. Load saved quiz\n3. Cancel")
    choice = input("Select option: ").strip()
    if choice == "1":
        topic = input("Enter topic for new quiz: ").strip()
        quiz = generate_quiz(topic)
        if quiz:
            take_quiz(quiz)
    elif choice == "2":
        quiz = load_quiz()
        if quiz:
            take_quiz(quiz)
    else:
        print("Cancelled.")
