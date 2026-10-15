from flask import Flask, render_template, request
import os
import json
from models.resume_parser import extract_resume_text
from models.skill_extractor import extract_skills
from models.matcher import calculate_match_score
from models.question_generator import generate_interview_questions
from models.suggestions import get_skill_suggestions

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Make sure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
DATA_FILE = "data/candidates.json"
os.makedirs("data", exist_ok=True)

# create file if not exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)


def load_candidates():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_candidate_report(report):
    candidates = load_candidates()
    candidates.append(report)
    with open(DATA_FILE, "w") as f:
        json.dump(candidates, f, indent=4)


# =========================
# Home / candidate / recruiter pages
# =========================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/candidate")
def candidate():
    return render_template("candidate_dashboard.html")


@app.route("/recruiter")
def recruiter():
    candidates = load_candidates()
    return render_template("recruiter_dashboard.html", candidates=candidates)

# =========================
# Analyze Resume
# =========================
@app.route("/analyze", methods=["POST"])
def analyze():
    candidate_name = request.form["candidate_name"]
    target_role = request.form["target_role"]
    job_description = request.form["job_description"]
    resume = request.files["resume"]

    # Save resume
    resume_path = os.path.join(app.config["UPLOAD_FOLDER"], resume.filename)
    resume.save(resume_path)

    # Extract resume text and skills
    resume_text = extract_resume_text(resume_path)
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)

    # Match calculation
    result = calculate_match_score(resume_skills, jd_skills)

    return render_template(
        "analysis_result.html",
        candidate_name=candidate_name,
        target_role=target_role,
        job_description=job_description,
        resume_text=resume_text,
        score=result["score"],
        matched_skills=result["matched_skills"],
        missing_skills=result["missing_skills"],
        resume_skills=resume_skills,
        jd_skills=jd_skills
    )


# =========================
# Start Interview
# =========================
@app.route("/start_interview", methods=["POST"])
def start_interview():
    candidate_name = request.form["candidate_name"]
    target_role = request.form["target_role"]
    job_description = request.form["job_description"]
    resume_text = request.form["resume_text"]
    resume_score = request.form.get("resume_score", "N/A")

    matched_skills = request.form.getlist("matched_skills")
    missing_skills = request.form.getlist("missing_skills")

    questions = generate_interview_questions(
        resume_text=resume_text,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        target_role=target_role,
        job_description=job_description,
        num_questions=8
    )

    return render_template(
        "interview.html",
        candidate_name=candidate_name,
        target_role=target_role,
        questions=questions,
        resume_score=resume_score
    )

    
    

# =========================
# Submit Interview
# =========================
@app.route("/submit_interview", methods=["POST"])
def submit_interview():
    candidate_name = request.form.get("candidate_name", "Candidate")
    target_role = request.form.get("target_role", "Target Role")
    resume_score = request.form.get("resume_score", "N/A")

    questions_json = request.form.get("questions_json", "[]")
    questions = json.loads(questions_json)

    total_questions = len(questions)
    correct_count = 0
    results = []
    weak_skills = []

    for i, q in enumerate(questions):
        selected_answer = request.form.get(f"answer_{i}", "").strip()
        correct_answer = q.get("answer", "").strip()
        question_text = q.get("question", "")
        skill = q.get("skill", "Unknown Skill")

        is_correct = selected_answer == correct_answer

        if is_correct:
            correct_count += 1
        else:
            weak_skills.append(skill)

        results.append({
            "question": question_text,
            "skill": skill,
            "selected_answer": selected_answer if selected_answer else "Not Answered",
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })

    score = round((correct_count / total_questions) * 100, 2) if total_questions > 0 else 0
    weak_skills = list(set(weak_skills))
    


    if score >= 75:
        recommendation = "Good Fit"
        verdict = "The candidate performed well in the AI interview and is a strong fit for the role."
    elif score >= 50:
        recommendation = "Moderate Fit"
        verdict = "The candidate has a decent foundation but needs improvement in some areas."
    else:
        recommendation = "Needs Improvement"
        verdict = "The candidate needs stronger technical preparation before being recommended."

    suggestions = []
    if weak_skills:
        for skill in weak_skills:
            suggestions.append(f"Improve fundamentals and practice more questions in {skill}.")
    else:
        suggestions.append("Excellent performance. Continue practicing advanced concepts for stronger preparation.")

    # ===== SAVE FOR RECRUITER DASHBOARD =====
    candidate_report = {
        "candidate_name": candidate_name,
        "target_role": target_role,
        "resume_score": resume_score,
        "interview_score": score,
        "correct_count": correct_count,
        "total_questions": total_questions,
        "recommendation": recommendation,
        "verdict": verdict,
        "weak_skills": weak_skills
    }
    print("Saving candidate report:", candidate_report)

    save_candidate_report(candidate_report)
    
    return render_template(
        "candidate_result.html",
        candidate_name=candidate_name,
        target_role=target_role,
        score=score,
        correct_count=correct_count,
        total_questions=total_questions,
        recommendation=recommendation,
        verdict=verdict,
        weak_skills=weak_skills,
        suggestions=suggestions,
        results=results,
        
    )
if __name__ == "__main__":
    app.run(debug=True)