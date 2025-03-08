from flask import Blueprint, request, jsonify
from utils.gemini_quiz import generate_quiz_questions
from flask_login import login_required

quiz_blueprint = Blueprint('quiz', __name__)

@quiz_blueprint.route('/check_answers', methods=['POST'])
@login_required
def check_answers():
    user_answers = request.json  # User-submitted answers
    job_role = request.args.get('job_role', '')

    # Get correct answers from Gemini API
    quiz_questions = generate_quiz_questions(job_role)
    correct_answers = {f"q{index}": q["correct_option"] for index, q in enumerate(quiz_questions)}

    # Calculate score
    score = sum(1 for q, ans in user_answers.items() if correct_answers.get(q) == ans)

    return jsonify({"score": score, "correct_answers": correct_answers})
