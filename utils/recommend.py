import joblib
import os
import numpy as np

model_path = 'models/model.pkl'

# Load model if available
if os.path.exists(model_path):
    model = joblib.load(model_path)
else:
    model = None

def recommend_job_domains(extracted_info):
    # If the model is not loaded, return an error message
    if not model:
        return ['Model not available']

    # Prepare input data
    combined_text = ' '.join([
        ' '.join(extracted_info.get('education', [])),
        ' '.join(extracted_info.get('skills', [])),
        ' '.join(extracted_info.get('experience', []))
    ])
    X = model.named_steps['tfidf'].transform([combined_text])

    # Predict job domains using the classifier
    predicted_probabilities = model.named_steps['clf'].predict_proba(X)[0]
    top_indices = np.argsort(predicted_probabilities)[::-1][:3]

    # Check if 'label_encoder' exists in the model steps
    if 'label_encoder' in model.named_steps:
        label_mapping = model.named_steps['label_encoder'].classes_
        recommendations = [label_mapping[index] for index in top_indices]
    else:
        # Return a generic message if label_encoder is not available
        print("Warning: 'label_encoder' not found in model pipeline.")
        recommendations = ['Job domain prediction unavailable']

    return recommendations
