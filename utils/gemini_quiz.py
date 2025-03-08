import google.generativeai as genai
import logging

# Configure Gemini API Key
genai.configure(api_key="AIzaSyBdiTBiBBTNIacb1ZJVpbbicjJ-uLSSzek")

def generate_quiz_questions(job_role):
    """Fetch quiz questions from Google Gemini API based on job role."""
    try:
        logging.info(f"Fetching quiz questions for: {job_role}")

        # Correct Model Name
        model = genai.GenerativeModel("models/gemini-1.0-pro")

        prompt = f"""
        Generate a technical quiz for the job role: {job_role}.
        - Provide 15 multiple-choice questions.
        - Each question should have 4 answer choices (A, B, C, D).
        - Mark the correct answer.
        - Include an explanation for each correct answer.
        Output the quiz in a JSON format.
        """

        response = model.generate_content(prompt)

        if response and response.candidates:
            return response.candidates[0].content
        else:
            logging.error("❌ No quiz questions received from Gemini API.")
            return None

    except Exception as e:
        logging.error(f"❌ Error fetching quiz questions: {e}")
        return None
