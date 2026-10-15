import os
import json
import re
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "openai/gpt-oss-120b"


def fallback_evaluation(question, answer):
    """
    Simple backup evaluation if Groq fails.
    """
    answer = answer.lower().strip()

    if len(answer) < 20:
        return {
            "score": 3,
            "feedback": "Answer is too short and lacks technical depth.",
            "improvement": "Explain the concept in more detail with examples."
        }
    elif len(answer) < 60:
        return {
            "score": 5,
            "feedback": "Answer is partially correct but needs more clarity and depth.",
            "improvement": "Add key concepts, examples, and more technical explanation."
        }
    else:
        return {
            "score": 7,
            "feedback": "Answer is reasonably detailed but can be improved further.",
            "improvement": "Use more precise technical terminology and structured explanation."
        }


def clean_json_response(text):
    """
    Extract JSON object from model response safely.
    """
    text = text.strip()

    # Remove markdown code fences if present
    text = re.sub(r"^```json", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"^```", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    # Find first JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        text = text[start:end+1]

    return text


def evaluate_answer(question, answer, target_role="Candidate", job_description=""):
    """
    Uses Groq to evaluate a candidate answer and return:
    {
        "score": int (0-10),
        "feedback": "...",
        "improvement": "..."
    }
    """

    if not GROQ_API_KEY:
        print("Groq API key not found. Using fallback evaluation.")
        return fallback_evaluation(question, answer)

    prompt = f"""
You are an expert technical interviewer evaluating a candidate answer.

Candidate target role:
{target_role}

Job description context:
{job_description}

Question:
{question}

Candidate answer:
{answer}

Evaluate the answer and return ONLY valid JSON in this exact format:
{{
  "score": <integer from 0 to 10>,
  "feedback": "<2-3 line feedback about answer quality>",
  "improvement": "<1-2 line improvement suggestion>"
}}

Evaluation criteria:
1. Technical correctness
2. Relevance to the question
3. Clarity and completeness
4. Depth of explanation
5. Communication quality

Important rules:
- Return only JSON.
- Score must be an integer between 0 and 10.
- feedback should be concise and professional.
- improvement should be practical and specific.
"""

    try:
        client = Groq(api_key=GROQ_API_KEY)

        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict but fair technical interviewer who evaluates candidate answers and returns structured JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=500
        )

        response_text = completion.choices[0].message.content
        cleaned = clean_json_response(response_text)
        result = json.loads(cleaned)

        # Safety checks
        score = result.get("score", 5)
        feedback = result.get("feedback", "Answer evaluated.")
        improvement = result.get("improvement", "Try to explain with more technical clarity.")

        # Ensure score range
        try:
            score = int(score)
        except:
            score = 5

        score = max(0, min(score, 10))

        return {
            "score": score,
            "feedback": feedback,
            "improvement": improvement
        }

    except Exception as e:
        print("Groq evaluation error:", e)
        return fallback_evaluation(question, answer)