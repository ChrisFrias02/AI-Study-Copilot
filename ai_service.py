import json
import os

from openai import OpenAI

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError(
                "OPENAI_API_KEY is not set. Add it to your .env in the project root or Backend folder."
            )
        _client = OpenAI(api_key=key)
    return _client

def generate_study_plan(text):
    prompt = f"""You are a study assistant.
A student has provided their notes below.
Identify the main topics (3-8 topics) and write a structured study plan.

Return ONLY valid JSON, no extra text:
{{
  "topics": ["topic 1", "topic 2"],
  "plan": [
    {{"topic": "topic 1", "time": "30 min", "priority": "high", "tips": "focus on..."}}
  ]
}}

Notes:
{text[:8000]}"""

    response = _get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    raw = response.choices[0].message.content
    cleaned = raw.strip().removeprefix("```json").removesuffix("```").strip()
    return json.loads(cleaned)

def generate_quiz(text, num_questions=10):
    prompt = f"""You are a quiz generator.
Based on the notes below, create {num_questions} multiple choice questions.

Return ONLY valid JSON, no extra text:
{{
  "questions": [
    {{
      "question": "What is...?",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "answer": "A",
      "explanation": "Because..."
    }}
  ]
}}

Notes:
{text[:8000]}"""

    response = _get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    raw = response.choices[0].message.content
    cleaned = raw.strip().removeprefix("```json").removesuffix("```").strip()
    return json.loads(cleaned)