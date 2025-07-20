import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, mean_absolute_error
import joblib
import os
import sqlite3
from datetime import datetime, timedelta
import re

class TicketPredictor:
    def __init__(self):
        self.category_model = None
        self.resolution_time_model = None
        self.tfidf_vectorizer = None
        self.label_encoder = None
        self.models_trained = False
        self.model_dir = 'ml_models'
        
        # Create models directory if it doesn't exist
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
    
    def preprocess_text(self, text):
        """Clean and preprocess text data"""
        if pd.isna(text) or text is None:
            return ""
        
        # Convert to lowercase
        text = str(text).lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def generate_sample_data(self):
        """Generate sample training data for demonstration"""
        categories = ['Technical Issue', 'Account Support', 'Billing', 'Feature Request', 'Bug Report', 'General Inquiry']
        priorities = ['Low', 'Medium', 'High', 'Critical']
        
        # Sample descriptions for each category
        sample_descriptions = {
            'Technical Issue': [
                'cannot login to system', 'password reset not working', 'system crashes frequently',
                'slow performance issues', 'connection timeout errors', 'database connection failed'
            ],
            'Account Support': [
                'need to update profile information', 'account locked out', 'forgot username',
                'change email address', 'deactivate account', 'account permissions issue'
            ],
            'Billing': [
                'incorrect charges on invoice', 'payment method update', 'refund request',
                'billing cycle questions', 'subscription cancellation', 'pricing inquiry'
            ],
            'Feature Request': [
                'add new dashboard widget', 'export data functionality', 'mobile app feature',
                'integration with third party', 'custom reporting options', 'user interface improvements'
            ],
            'Bug Report': [
                'button not responding', 'data not saving properly', 'incorrect calculations',
                'page loading errors', 'missing information display', 'form validation issues'
            ],
            'General Inquiry': [
                'how to use new feature', 'training materials request', 'system requirements',
                'best practices guidance', 'documentation questions', 'general support'
            ]
        }
        
        # Generate sample data
        data = []
        for category in categories:
            for desc in sample_descriptions[category]:
                priority = np.random.choice(priorities)
                
                # Resolution time based on priority and category
                base_time = {
                    'Critical': np.random.normal(2, 0.5),
                    'High': np.random.normal(8, 2),
                    'Medium': np.random.normal(24, 6),
                    'Low': np.random.normal(72, 12)
                }[priority]
                
                # Category modifier
                category_modifier = {
                    'Technical Issue': 1.2,
                    'Bug Report': 1.5,
                    'Feature Request': 2.0,
                    'Billing': 0.8,
                    'Account Support': 0.6,
                    'General Inquiry': 0.5
                }[category]
                
                resolution_time = max(1, base_time * category_modifier)
                
                data.append({
                    'description': desc,
                    'category': category,
                    'priority': priority,
                    'resolution_time_hours': resolution_time
                })
        
        return pd.DataFrame(data)
    
    def load_data_from_db(self):
        """Load ticket data from database"""
        try:
            conn = sqlite3.connect('instance/database.db')
            query = """
            SELECT title, description, category, priority, status, created_at, updated_at
            FROM tickets
            WHERE status = 'Resolved'
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if len(df) < 10:  # If not enough real data, use sample data
                print("Not enough real data, using sample data for training...")
                return self.generate_sample_data()
            
            # Calculate resolution time
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['updated_at'] = pd.to_datetime(df['updated_at'])
            df['resolution_time_hours'] = (df['updated_at'] - df['created_at']).dt.total_seconds() / 3600
            
            # Combine title and description
            df['description'] = df['title'].fillna('') + ' ' + df['description'].fillna('')
            
            return df[['description', 'category', 'priority', 'resolution_time_hours']]
            
        except Exception as e:
            print(f"Error loading data from database: {e}")
            return self.generate_sample_data()
    
    def train_models(self):
        """Train both category prediction and resolution time models"""
        print("Loading training data...")
        df = self.load_data_from_db()
        
        if len(df) == 0:
            print("No data available for training")
            return False
        
        print(f"Training with {len(df)} samples...")
        
        # Preprocess descriptions
        df['description_clean'] = df['description'].apply(self.preprocess_text)
        
        # Remove empty descriptions
        df = df[df['description_clean'].str.len() > 0]
        
        if len(df) == 0:
            print("No valid descriptions for training")
            return False
        
        # Prepare features
        X_text = df['description_clean'].values
        
        # TF-IDF Vectorization
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        X_tfidf = self.tfidf_vectorizer.fit_transform(X_text)
        
        # Train Category Prediction Model
        print("Training category prediction model...")
        self.label_encoder = LabelEncoder()
        y_category = self.label_encoder.fit_transform(df['category'])
        
        X_train_cat, X_test_cat, y_train_cat, y_test_cat = train_test_split(
            X_tfidf, y_category, test_size=0.2, random_state=42
        )
        
        self.category_model = DecisionTreeClassifier(random_state=42, max_depth=10)
        self.category_model.fit(X_train_cat, y_train_cat)
        
        # Evaluate category model
        y_pred_cat = self.category_model.predict(X_test_cat)
        cat_accuracy = accuracy_score(y_test_cat, y_pred_cat)
        print(f"Category prediction accuracy: {cat_accuracy:.2f}")
        
        # Train Resolution Time Prediction Model
        print("Training resolution time prediction model...")
        y_resolution = df['resolution_time_hours'].values
        
        X_train_res, X_test_res, y_train_res, y_test_res = train_test_split(
            X_tfidf, y_resolution, test_size=0.2, random_state=42
        )
        
        self.resolution_time_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.resolution_time_model.fit(X_train_res, y_train_res)
        
        # Evaluate resolution time model
        y_pred_res = self.resolution_time_model.predict(X_test_res)
        res_mae = mean_absolute_error(y_test_res, y_pred_res)
        print(f"Resolution time prediction MAE: {res_mae:.2f} hours")
        
        # Save models
        self.save_models()
        self.models_trained = True
        
        return True
    
    def save_models(self):
        """Save trained models to disk"""
        try:
            joblib.dump(self.category_model, os.path.join(self.model_dir, 'category_model.pkl'))
            joblib.dump(self.resolution_time_model, os.path.join(self.model_dir, 'resolution_time_model.pkl'))
            joblib.dump(self.tfidf_vectorizer, os.path.join(self.model_dir, 'tfidf_vectorizer.pkl'))
            joblib.dump(self.label_encoder, os.path.join(self.model_dir, 'label_encoder.pkl'))
            print("Models saved successfully")
        except Exception as e:
            print(f"Error saving models: {e}")
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            model_files = [
                'category_model.pkl',
                'resolution_time_model.pkl',
                'tfidf_vectorizer.pkl',
                'label_encoder.pkl'
            ]
            
            # Check if all model files exist
            for file in model_files:
                if not os.path.exists(os.path.join(self.model_dir, file)):
                    return False
            
            self.category_model = joblib.load(os.path.join(self.model_dir, 'category_model.pkl'))
            self.resolution_time_model = joblib.load(os.path.join(self.model_dir, 'resolution_time_model.pkl'))
            self.tfidf_vectorizer = joblib.load(os.path.join(self.model_dir, 'tfidf_vectorizer.pkl'))
            self.label_encoder = joblib.load(os.path.join(self.model_dir, 'label_encoder.pkl'))
            
            self.models_trained = True
            print("Models loaded successfully")
            return True
            
        except Exception as e:
            print(f"Error loading models: {e}")
            return False
    
    def predict_category(self, description):
        """Predict ticket category based on description"""
        if not self.models_trained:
            if not self.load_models():
                if not self.train_models():
                    return "General Inquiry", 0.0
        
        try:
            # Preprocess description
            clean_desc = self.preprocess_text(description)
            if not clean_desc:
                return "General Inquiry", 0.0
            
            # Transform to TF-IDF
            X_tfidf = self.tfidf_vectorizer.transform([clean_desc])
            
            # Predict category
            prediction = self.category_model.predict(X_tfidf)[0]
            probabilities = self.category_model.predict_proba(X_tfidf)[0]
            
            # Get category name and confidence
            category = self.label_encoder.inverse_transform([prediction])[0]
            confidence = max(probabilities)
            
            return category, confidence
            
        except Exception as e:
            print(f"Error predicting category: {e}")
            return "General Inquiry", 0.0
    
    def predict_resolution_time(self, description):
        """Predict expected resolution time based on description"""
        if not self.models_trained:
            if not self.load_models():
                if not self.train_models():
                    return 24.0  # Default 24 hours
        
        try:
            # Preprocess description
            clean_desc = self.preprocess_text(description)
            if not clean_desc:
                return 24.0
            
            # Transform to TF-IDF
            X_tfidf = self.tfidf_vectorizer.transform([clean_desc])
            
            # Predict resolution time
            prediction = self.resolution_time_model.predict(X_tfidf)[0]
            
            # Ensure reasonable bounds
            prediction = max(1.0, min(168.0, prediction))  # Between 1 hour and 1 week
            
            return round(prediction, 1)
            
        except Exception as e:
            print(f"Error predicting resolution time: {e}")
            return 24.0
    
    def get_prediction_insights(self, description):
        """Get comprehensive prediction insights"""
        category, category_confidence = self.predict_category(description)
        resolution_time = self.predict_resolution_time(description)
        
        # Convert hours to human-readable format
        if resolution_time < 24:
            time_str = f"{resolution_time:.1f} hours"
        else:
            days = resolution_time / 24
            time_str = f"{days:.1f} days"
        
        return {
            'predicted_category': category,
            'category_confidence': round(category_confidence * 100, 1),
            'predicted_resolution_time_hours': resolution_time,
            'predicted_resolution_time_display': time_str,
            'confidence_level': 'High' if category_confidence > 0.7 else 'Medium' if category_confidence > 0.5 else 'Low'
        }

# Global predictor instance
predictor = TicketPredictor()

def initialize_ml_models():
    """Initialize ML models on startup"""
    try:
        if not predictor.load_models():
            print("Training new ML models...")
            predictor.train_models()
        return True
    except Exception as e:
        print(f"Error initializing ML models: {e}")
        return False

if __name__ == "__main__":
    # Test the predictor
    predictor = TicketPredictor()
    predictor.train_models()
    
    # Test predictions
    test_descriptions = [
        "Cannot login to the system, password reset not working",
        "Need help with billing invoice charges",
        "System crashes when I try to save data",
        "Request for new dashboard feature"
    ]
    
    for desc in test_descriptions:
        insights = predictor.get_prediction_insights(desc)
        print(f"\nDescription: {desc}")
        print(f"Predicted Category: {insights['predicted_category']} ({insights['category_confidence']}% confidence)")
        print(f"Expected Resolution Time: {insights['predicted_resolution_time_display']}")
