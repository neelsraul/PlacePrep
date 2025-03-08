import pandas as pd
import numpy as np
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix

# Load dataset
df = pd.read_csv('D:/Dwarkadas J. Sanghvi College of Engineering/Semester 7/Project/Optimized Placement Preparation Portal/synthetic_resume_dataset.csv')

# Handle missing values
df.dropna(subset=['text', 'label'], inplace=True)

# Encode labels
label_encoder = LabelEncoder()
df['label_encoded'] = label_encoder.fit_transform(df['label'])

# Split data
X = df['text']
y = df['label_encoded']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Build pipeline
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english', max_df=0.7)),
    ('clf', LogisticRegression(max_iter=1000, n_jobs=-1, class_weight='balanced'))
])

# Hyperparameter tuning
parameters = {
    'tfidf__ngram_range': [(1, 1), (1, 2)],
    'tfidf__min_df': [1, 3, 5],
    'clf__C': [0.1, 1, 10]
}

grid_search = GridSearchCV(pipeline, parameters, cv=5, n_jobs=-1, scoring='accuracy')
grid_search.fit(X_train, y_train)

# Evaluate
print(f'Best parameters: {grid_search.best_params_}')
print(f'Training set score: {grid_search.best_score_}')

y_pred = grid_search.predict(X_test)
print('Test set results:')
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

# Confusion matrix
conf_matrix = confusion_matrix(y_test, y_pred)
print('Confusion Matrix:')
print(conf_matrix)

# Save the trained pipeline and label encoder together
model_data = {
    'model': grid_search.best_estimator_,
    'label_encoder': label_encoder
}
joblib.dump(model_data, 'models/model.pkl')

print('Model training completed and saved to models/model.pkl')
