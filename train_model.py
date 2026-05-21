import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
import joblib

# Define symptoms and diseases
symptoms = ['fever', 'cough', 'fatigue', 'headache', 'nausea', 'chest_pain',
            'shortness_breath', 'sore_throat', 'muscle_ache', 'runny_nose',
            'vomiting', 'abdominal_pain', 'dizziness', 'sweating', 'rapid_heartbeat']

diseases = ['Influenza', 'Common Cold', 'Gastroenteritis', 'Migraine',
            'Heart Attack', 'Anxiety', 'Pneumonia']

# Synthetic data: each disease has a probability pattern
disease_symptom_prob = {
    'Influenza': [0.8, 0.7, 0.9, 0.3, 0.2, 0.0, 0.0, 0.6, 0.8, 0.4, 0.1, 0.0, 0.2, 0.5, 0.1],
    'Common Cold': [0.3, 0.9, 0.4, 0.2, 0.0, 0.0, 0.0, 0.8, 0.3, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0],
    'Gastroenteritis': [0.2, 0.0, 0.7, 0.1, 0.9, 0.0, 0.0, 0.0, 0.2, 0.0, 0.8, 0.9, 0.3, 0.1, 0.0],
    'Migraine': [0.0, 0.0, 0.5, 0.9, 0.3, 0.0, 0.0, 0.0, 0.2, 0.0, 0.4, 0.0, 0.8, 0.0, 0.0],
    'Heart Attack': [0.0, 0.0, 0.4, 0.1, 0.2, 0.9, 0.8, 0.0, 0.0, 0.0, 0.1, 0.0, 0.5, 0.7, 0.9],
    'Anxiety': [0.0, 0.0, 0.7, 0.6, 0.2, 0.3, 0.7, 0.0, 0.2, 0.0, 0.0, 0.0, 0.9, 0.6, 0.8],
    'Pneumonia': [0.9, 0.8, 0.7, 0.2, 0.1, 0.6, 0.9, 0.3, 0.5, 0.2, 0.1, 0.0, 0.2, 0.4, 0.2]
}

# Generate training data
X_train = []
y_train = []

for disease, probs in disease_symptom_prob.items():
    for _ in range(200):  # 200 samples per disease
        sample = [1 if np.random.random() < prob else 0 for prob in probs]
        X_train.append(sample)
        y_train.append(disease)

X_train = np.array(X_train)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save model and symptoms list
joblib.dump((model, symptoms, diseases), 'model.pkl')
print("Model trained and saved as model.pkl")