from flask_login import UserMixin
from database import get_db_connection

class User(UserMixin):
    """User model for authentication"""
    
    def __init__(self, id, username, email, role):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
    
    @staticmethod
    def get(user_id):
        """Get user by ID"""
        conn = get_db_connection()
        user_data = conn.execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()
        conn.close()
        
        if user_data:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                role=user_data['role']
            )
        return None
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        conn = get_db_connection()
        user_data = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        conn.close()
        
        if user_data:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                role=user_data['role']
            ), user_data['password_hash']
        return None, None
    
    @staticmethod
    def create_user(username, email, password_hash, role='agent'):
        """Create a new user"""
        conn = get_db_connection()
        try:
            cursor = conn.execute(
                'INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
                (username, email, password_hash, role)
            )
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
        except Exception as e:
            conn.close()
            raise e
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def is_agent(self):
        """Check if user is agent"""
        return self.role == 'agent'
    
    def __repr__(self):
        return f'<User {self.username}>'
