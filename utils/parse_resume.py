import os
import re
import nltk
import spacy
from pdfminer.high_level import extract_text
import docx

# Download NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)

# Load Spacy language model
nlp = spacy.load('en_core_web_sm')

def parse_resume(filepath):
    """
    Main function to parse a resume file and extract relevant information.
    """
    text = extract_text_from_file(filepath)
    if not text:
        raise ValueError("No text extracted from the file.")
    
    cleaned_text = clean_text(text)
    extracted_info = extract_information(cleaned_text)
    return extracted_info

def extract_text_from_file(filepath):
    """
    Extracts text from PDF or DOCX files.
    """
    try:
        if filepath.endswith('.pdf'):
            text = extract_text(filepath)  # Using pdfminer
        elif filepath.endswith('.docx'):
            doc = docx.Document(filepath)
            text = '\n'.join([para.text for para in doc.paragraphs])
        else:
            raise ValueError("Unsupported file format. Only PDF and DOCX files are supported.")
    except Exception as e:
        raise ValueError(f"Error extracting text from file: {e}")
    
    return text

def clean_text(text):
    """
    Cleans the extracted text by removing special characters, digits, and extra spaces.
    """
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    # Convert to lowercase and strip
    text = text.lower().strip()
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_information(text):
    """
    Extracts structured information like education, skills, and experience from text.
    """
    doc = nlp(text)
    info = {}
    info['education'] = extract_education(doc)
    info['skills'] = extract_skills(doc)
    info['experience'] = extract_experience(doc)
    return info

def extract_education(doc):
    """
    Extracts education information from the text using predefined degree keywords.
    """
    education = []
    education_degrees = ['bachelor', 'master', 'bsc', 'msc', 'phd', 'be', 'me', 'btech', 'mtech', 'mba', 'diploma']
    for sent in doc.sents:
        for degree in education_degrees:
            if degree in sent.text.lower():
                education.append(sent.text.strip())
    return list(set(education))

def extract_skills(doc):
    """
    Extracts skills by matching against a predefined skills list.
    The skills list should be provided in a file named 'skills.txt' under the 'utils' folder.
    """
    skills = []
    skill_file_path = 'utils/skills.txt'  # Update path if skills.txt is elsewhere
    if not os.path.exists(skill_file_path):
        return skills  # Return an empty list if the file doesn't exist

    # Load skills from the file
    with open(skill_file_path, 'r') as f:
        skill_list = [line.strip().lower() for line in f]

    # Match skills from the text
    for token in doc:
        if token.text.lower() in skill_list:
            skills.append(token.text)

    return list(set(skills))

def extract_experience(doc):
    """
    Extracts experience information such as years or months mentioned in the text.
    """
    experience = []
    experience_patterns = [r'\b\d+\s+years?\b', r'\b\d+\s+months?\b']  # Regex patterns for experience
    text = doc.text
    for pattern in experience_patterns:
        matches = re.findall(pattern, text)
        experience.extend(matches)
    return list(set(experience))
