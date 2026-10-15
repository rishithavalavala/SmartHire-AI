SKILL_DB = [
    "python", "java", "c", "c++", "sql", "html", "css", "javascript",
    "flask", "django", "machine learning", "deep learning", "nlp",
    "pandas", "numpy", "matplotlib", "tensorflow", "pytorch",
    "git", "github", "data structures", "algorithms", "oop", "dbms"
]

def extract_skills(text):
    text = text.lower()
    found_skills = []

    for skill in SKILL_DB:
        if skill in text:
            found_skills.append(skill)

    return list(set(found_skills))