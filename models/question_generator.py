import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def get_role_topics(target_role):
    role = target_role.lower()

    role_topics_map = {
        "full stack": [
            "HTML", "CSS", "JavaScript", "React", "Bootstrap",
            "Python Flask", "REST API", "SQL", "Database", "Git"
        ],
        "full stack developer": [
            "HTML", "CSS", "JavaScript", "React", "Bootstrap",
            "Python Flask", "REST API", "SQL", "Database", "Git"
        ],
        "python developer": [
            "Python", "OOP", "Functions", "File Handling",
            "Flask", "APIs", "SQL", "Git"
        ],
        "ai/ml engineer": [
            "Python", "Machine Learning", "Pandas", "NumPy",
            "Scikit-learn", "Model Evaluation", "Data Preprocessing", "NLP"
        ],
        "data analyst": [
            "Python", "SQL", "Pandas", "NumPy",
            "Excel", "Data Visualization", "Statistics"
        ]
    }

    for key in role_topics_map:
        if key in role:
            return role_topics_map[key]

    return []


def generate_interview_questions(
    resume_text,
    matched_skills,
    missing_skills,
    target_role,
    job_description,
    num_questions=8
):
    role_topics = get_role_topics(target_role)

    prompt = f"""
You are an AI technical interviewer.

Generate exactly {num_questions} multiple-choice interview questions for a candidate.

Target role: {target_role}

Job description:
{job_description}

Resume text:
{resume_text}

Matched skills from resume and JD:
{matched_skills}

Missing skills from JD:
{missing_skills}

Mandatory role-specific topics to include if relevant:
{role_topics}

IMPORTANT INSTRUCTIONS:
1. Questions must NOT be based only on resume skills.
2. Generate a balanced interview using:
   - some questions from matched resume skills
   - some questions from missing skills
   - some questions from mandatory role-specific topics
3. If the target role is Full Stack, include questions from frontend, backend, APIs, database, and Git even if they are not clearly present in the resume.
4. Prefer missing skills and role-specific topics over repeating too many resume-only questions.
5. Return ONLY valid JSON.
6. Each question must have:
   - question
   - options (4 options)
   - answer
   - skill

Output format:
[
  {{
    "question": "What does HTML stand for?",
    "options": ["Hyper Text Markup Language", "High Text Markdown Language", "Hyper Transfer Machine Language", "None"],
    "answer": "Hyper Text Markup Language",
    "skill": "HTML"
  }}
]
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are a technical interviewer who returns only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        content = response.choices[0].message.content.strip()

        # Remove markdown code block if present
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        questions = json.loads(content)

        if isinstance(questions, list):
            return questions
        return []

    except Exception as e:
        print("Error generating/parsing questions:", e)
        return []
        