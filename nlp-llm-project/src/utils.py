# src/api/utils.py
import json
import random
from typing import List
from schemas import QuizQuestion

def parse_quiz_json(quiz_str: str) -> List[QuizQuestion]:
    """
    Parse LLM output as JSON and validate structure.
    Fallbacks to single short-answer question if invalid.
    """
    try:
        data = json.loads(quiz_str)
        if isinstance(data, list):
            questions = []
            for q in data:
                # Ensure all required fields exist
                if 'question' in q and 'type' in q and 'answer' in q:
                    options = q.get('options', None)
                    difficulty = q.get('difficulty', None)
                    show_answer = q.get('show_answer', True)
                    questions.append(
                        QuizQuestion(
                            question=q['question'],
                            type=q['type'],
                            options=options,
                            answer=q['answer'],
                            difficulty=difficulty,
                            show_answer=show_answer
                        )
                    )
            return questions if questions else [QuizQuestion(question=quiz_str, type="short-answer", answer="", show_answer=True)]
        else:
            return [QuizQuestion(question=str(data), type="short-answer", answer="", show_answer=True)]
    except json.JSONDecodeError:
        return [QuizQuestion(question=quiz_str, type="short-answer", answer="", show_answer=True)]

def shuffle_multiple_choice(questions: List[QuizQuestion]) -> List[QuizQuestion]:
    """
    Shuffle multiple-choice options for each question, keeping correct answer intact.
    """
    for q in questions:
        if q.type == "multiple-choice" and q.options:
            # Ensure correct answer is in options
            if q.answer not in q.options:
                q.options.append(q.answer)
            # Shuffle options
            random.shuffle(q.options)
    return questions
