import google.generativeai as genai
import logging

# Configure Gemini API Key
genai.configure(api_key="AIzaSyBdiTBiBBTNIacb1ZJVpbbicjJ-uLSSzek")

def generate_quiz_questions(job_role):
    genai.configure(api_key="YOUR_API_KEY")
    model = genai.GenerativeModel("gemini-1.5-pro")  # Ensure correct model name

    prompt = f"Generate a 15-question multiple-choice quiz for {job_role}. Each question should have 4 options with only one correct answer."

    try:
        response = model.generate_content(prompt)
        logging.info(f"🔍 Gemini API Response: {response}")
        return response.text  # Check if response contains questions
    except Exception as e:
        logging.error(f"❌ Error fetching quiz questions: {e}")
        return None

    except Exception as e:
        logging.error(f"❌ Error fetching quiz questions: {e}")
        return None
