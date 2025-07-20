from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from ml_predictions import predictor, initialize_ml_models
import sqlite3
from datetime import datetime

predictions_bp = Blueprint('predictions', __name__, url_prefix='/predictions')

def get_db_connection():
    conn = sqlite3.connect('instance/database.db')
    conn.row_factory = sqlite3.Row
    return conn

@predictions_bp.route('/')
@login_required
def dashboard():
    """Predictive insights dashboard"""
    return render_template('predictions/dashboard.html')

@predictions_bp.route('/api/predict', methods=['POST'])
@login_required
def predict_ticket():
    """API endpoint for ticket predictions"""
    try:
        data = request.get_json()
        description = data.get('description', '')
        
        if not description.strip():
            return jsonify({'error': 'Description is required'}), 400
        
        # Get predictions
        insights = predictor.get_prediction_insights(description)
        
        return jsonify({
            'success': True,
            'predictions': insights
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@predictions_bp.route('/api/retrain', methods=['POST'])
@login_required
def retrain_models():
    """API endpoint to retrain ML models"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        success = predictor.train_models()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Models retrained successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to retrain models'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@predictions_bp.route('/api/model-status')
@login_required
def model_status():
    """Get ML model status information"""
    try:
        # Check if models are loaded
        models_loaded = predictor.models_trained
        
        # Get some basic stats
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count total tickets for training data
        cursor.execute("SELECT COUNT(*) FROM tickets")
        total_tickets = cursor.fetchone()[0]
        
        # Count resolved tickets (used for training)
        cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'Resolved'")
        resolved_tickets = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'models_loaded': models_loaded,
            'total_tickets': total_tickets,
            'training_data_size': resolved_tickets,
            'recommendation': 'Good' if resolved_tickets >= 50 else 'Limited' if resolved_tickets >= 10 else 'Insufficient'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@predictions_bp.route('/api/batch-predict', methods=['POST'])
@login_required
def batch_predict():
    """Batch prediction for multiple tickets"""
    try:
        data = request.get_json()
        descriptions = data.get('descriptions', [])
        
        if not descriptions:
            return jsonify({'error': 'No descriptions provided'}), 400
        
        results = []
        for desc in descriptions:
            if desc.strip():
                insights = predictor.get_prediction_insights(desc)
                results.append({
                    'description': desc,
                    'predictions': insights
                })
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@predictions_bp.route('/test')
@login_required
def test_predictions():
    """Test page for predictions"""
    return render_template('predictions/test.html')

@predictions_bp.route('/insights')
@login_required
def insights():
    """Prediction insights and analytics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get category distribution
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM tickets 
            GROUP BY category 
            ORDER BY count DESC
        """)
        category_stats = cursor.fetchall()
        
        # Get average resolution times by category
        cursor.execute("""
            SELECT 
                category,
                AVG(CASE WHEN status = 'Resolved' THEN 
                    (julianday(updated_at) - julianday(created_at)) * 24 
                END) as avg_hours
            FROM tickets 
            WHERE status = 'Resolved'
            GROUP BY category
            ORDER BY avg_hours
        """)
        resolution_stats = cursor.fetchall()
        
        # Get recent predictions (if we stored them)
        cursor.execute("""
            SELECT 
                title,
                description,
                category,
                created_at
            FROM tickets 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        recent_tickets = cursor.fetchall()
        
        conn.close()
        
        return render_template('predictions/insights.html',
                             category_stats=category_stats,
                             resolution_stats=resolution_stats,
                             recent_tickets=recent_tickets)
        
    except Exception as e:
        flash(f'Error loading insights: {str(e)}', 'error')
        return redirect(url_for('predictions.dashboard'))

# Initialize ML models when blueprint is imported
try:
    initialize_ml_models()
except Exception as e:
    print(f"Warning: Could not initialize ML models: {e}")
