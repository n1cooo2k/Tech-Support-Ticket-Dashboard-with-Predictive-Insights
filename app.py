from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from database import init_db
from models import User
from auth import auth_bp
from tickets import tickets_bp
from ticket_models import Ticket
import os

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DATABASE'] = 'instance/database.db'
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tickets_bp)
    
    # Main routes
    @app.route('/')
    def index():
        """Home page - redirect to appropriate dashboard if logged in"""
        if current_user.is_authenticated:
            if current_user.is_admin():
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('agent_dashboard'))
        return redirect(url_for('auth.login'))
    
    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        """Admin dashboard"""
        if not current_user.is_admin():
            return redirect(url_for('agent_dashboard'))
        
        # Get ticket statistics for admin dashboard
        try:
            stats = Ticket.get_stats()
            recent_tickets = Ticket.get_all(user_role='admin')[:5]  # Get 5 most recent tickets
        except:
            stats = {'total': 0, 'open': 0, 'in_progress': 0, 'resolved': 0, 'closed': 0}
            recent_tickets = []
        
        return render_template('admin_dashboard.html', user=current_user, stats=stats, recent_tickets=recent_tickets)
    
    @app.route('/agent/dashboard')
    @login_required
    def agent_dashboard():
        """Agent dashboard"""
        # Get tickets assigned to this agent
        try:
            my_tickets = Ticket.get_all(user_role='agent', user_id=current_user.id)
            # Calculate agent-specific stats
            total_tickets = len(my_tickets)
            open_tickets = len([t for t in my_tickets if t['status'] == 'open'])
            in_progress = len([t for t in my_tickets if t['status'] == 'in_progress'])
            resolved_tickets = len([t for t in my_tickets if t['status'] == 'resolved'])
            
            agent_stats = {
                'total': total_tickets,
                'open': open_tickets,
                'in_progress': in_progress,
                'resolved': resolved_tickets
            }
        except:
            my_tickets = []
            agent_stats = {'total': 0, 'open': 0, 'in_progress': 0, 'resolved': 0}
        
        return render_template('agent_dashboard.html', user=current_user, 
                             my_tickets=my_tickets[:5], stats=agent_stats)
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Generic dashboard route - redirect based on role"""
        if current_user.is_admin():
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('agent_dashboard'))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('403.html'), 403
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    # Initialize database on first run
    init_db()
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
