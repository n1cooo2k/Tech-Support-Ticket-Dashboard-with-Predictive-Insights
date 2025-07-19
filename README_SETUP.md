# Tech Support Ticket Dashboard - User Login System

## Overview
This is the first phase of a comprehensive Tech Support Ticket Dashboard with Predictive Insights. This phase implements a complete User Login System with role-based access control (Admin vs Agent roles).

## Features Implemented
- ✅ User Authentication (Login/Logout)
- ✅ User Registration
- ✅ Role-based Access Control (Admin/Agent)
- ✅ Secure Password Hashing
- ✅ Session Management
- ✅ Responsive UI with Tailwind CSS
- ✅ Admin Dashboard
- ✅ Agent Dashboard
- ✅ Error Handling (404, 403 pages)

## Tech Stack
- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript, Tailwind CSS
- **Database**: SQLite
- **Authentication**: Flask-Login
- **Security**: Werkzeug password hashing

## Installation & Setup

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Initialize Database
```bash
python database.py
```

### Step 3: Run the Application
```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## Demo Credentials

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Access**: Full admin dashboard with system overview

### Agent Account
- **Username**: `agent1`
- **Password**: `agent123`
- **Access**: Agent dashboard with ticket management focus

## Project Structure
```
/
├── app.py                 # Main Flask application
├── auth.py               # Authentication routes
├── models.py             # User model
├── database.py           # Database setup and initialization
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── templates/            # HTML templates
│   ├── base.html        # Base template with navigation
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   ├── admin_dashboard.html  # Admin dashboard
│   ├── agent_dashboard.html  # Agent dashboard
│   ├── 404.html         # 404 error page
│   └── 403.html         # 403 error page
├── static/              # Static files
│   ├── css/
│   │   └── style.css    # Custom CSS styles
│   └── js/
│       └── main.js      # JavaScript functionality
└── instance/            # Database storage
    └── database.db      # SQLite database (created automatically)
```

## Key Features

### Authentication System
- Secure login/logout functionality
- Password hashing using Werkzeug
- Session management with Flask-Login
- Remember me functionality

### Role-Based Access Control
- **Admin Role**: Full system access, user management capabilities
- **Agent Role**: Limited access focused on ticket handling

### User Interface
- Modern, responsive design using Tailwind CSS
- Intuitive navigation with role-based menus
- Flash message system for user feedback
- Mobile-friendly responsive layout

### Security Features
- Password hashing (never store plain text passwords)
- Session-based authentication
- CSRF protection ready
- Input validation and sanitization

## Next Development Phases

### Phase 2: Ticket Management System
- Create, read, update, delete tickets
- Ticket assignment and status tracking
- Priority levels and categories
- File attachments

### Phase 3: Dashboard Analytics
- Ticket statistics and metrics
- Performance tracking
- Chart.js integration for data visualization

### Phase 4: Predictive Insights
- Machine learning integration with scikit-learn
- Ticket categorization and priority prediction
- Trend analysis and forecasting

### Phase 5: Advanced Features
- Real-time notifications
- Email integration
- Advanced reporting
- API endpoints

## Development Notes

### Database Schema
The current user table includes:
- `id`: Primary key
- `username`: Unique username
- `email`: User email address
- `password_hash`: Hashed password
- `role`: User role (admin/agent)
- `created_at`: Account creation timestamp

### Environment Variables
Configure these in your `.env` file:
- `SECRET_KEY`: Flask secret key for sessions
- `FLASK_ENV`: Development/production environment
- `FLASK_DEBUG`: Debug mode toggle

## Troubleshooting

### Common Issues
1. **Database not found**: Run `python database.py` to initialize
2. **Permission errors**: Check file permissions in the instance directory
3. **Port already in use**: Change the port in app.py or kill the existing process

### Development Tips
- Use `FLASK_DEBUG=True` for development
- Check the console for detailed error messages
- The database is automatically created on first run

## Contributing
This is a portfolio project showcasing full-stack development skills including:
- Backend API development with Flask
- Frontend development with modern CSS frameworks
- Database design and management
- User authentication and security
- Responsive web design
- Code organization and best practices

## License
This project is for educational and portfolio purposes.
