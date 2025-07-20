from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_login import login_required, current_user
from database import get_db_connection
from datetime import datetime, timedelta
import json

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

class Analytics:
    """Analytics class for generating dashboard data"""
    
    @staticmethod
    def get_tickets_by_category():
        """Get ticket count by category"""
        conn = get_db_connection()
        query = '''
            SELECT c.name, c.color, COUNT(t.id) as count
            FROM categories c
            LEFT JOIN tickets t ON c.id = t.category_id
            GROUP BY c.id, c.name, c.color
            ORDER BY count DESC
        '''
        results = conn.execute(query).fetchall()
        conn.close()
        
        return [{'name': row['name'], 'count': row['count'], 'color': row['color']} for row in results]
    
    @staticmethod
    def get_average_resolution_time():
        """Calculate average resolution time in hours"""
        conn = get_db_connection()
        query = '''
            SELECT 
                AVG(JULIANDAY(resolved_at) - JULIANDAY(created_at)) * 24 as avg_hours,
                COUNT(*) as resolved_count
            FROM tickets 
            WHERE resolved_at IS NOT NULL
        '''
        result = conn.execute(query).fetchone()
        conn.close()
        
        if result and result['avg_hours']:
            return {
                'average_hours': round(result['avg_hours'], 2),
                'resolved_count': result['resolved_count']
            }
        return {'average_hours': 0, 'resolved_count': 0}
    
    @staticmethod
    def get_resolution_time_by_category():
        """Get average resolution time by category"""
        conn = get_db_connection()
        query = '''
            SELECT 
                c.name,
                c.color,
                AVG(JULIANDAY(t.resolved_at) - JULIANDAY(t.created_at)) * 24 as avg_hours,
                COUNT(t.id) as count
            FROM categories c
            LEFT JOIN tickets t ON c.id = t.category_id AND t.resolved_at IS NOT NULL
            GROUP BY c.id, c.name, c.color
            HAVING count > 0
            ORDER BY avg_hours ASC
        '''
        results = conn.execute(query).fetchall()
        conn.close()
        
        return [{
            'category': row['name'],
            'avg_hours': round(row['avg_hours'], 2) if row['avg_hours'] else 0,
            'count': row['count'],
            'color': row['color']
        } for row in results]
    
    @staticmethod
    def get_time_series_data(days=30):
        """Get time series data for ticket creation and resolution"""
        conn = get_db_connection()
        
        # Get ticket creation data
        creation_query = '''
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as created_count
            FROM tickets 
            WHERE created_at >= date('now', '-{} days')
            GROUP BY DATE(created_at)
            ORDER BY date
        '''.format(days)
        
        # Get ticket resolution data
        resolution_query = '''
            SELECT 
                DATE(resolved_at) as date,
                COUNT(*) as resolved_count
            FROM tickets 
            WHERE resolved_at IS NOT NULL 
            AND resolved_at >= date('now', '-{} days')
            GROUP BY DATE(resolved_at)
            ORDER BY date
        '''.format(days)
        
        created_data = conn.execute(creation_query).fetchall()
        resolved_data = conn.execute(resolution_query).fetchall()
        conn.close()
        
        # Create date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Initialize data dictionaries
        created_dict = {row['date']: row['created_count'] for row in created_data}
        resolved_dict = {row['date']: row['resolved_count'] for row in resolved_data}
        
        # Generate complete time series
        time_series = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            time_series.append({
                'date': date_str,
                'created': created_dict.get(date_str, 0),
                'resolved': resolved_dict.get(date_str, 0)
            })
            current_date += timedelta(days=1)
        
        return time_series
    
    @staticmethod
    def get_priority_distribution():
        """Get ticket distribution by priority"""
        conn = get_db_connection()
        query = '''
            SELECT 
                priority,
                COUNT(*) as count,
                CASE 
                    WHEN priority = 'high' THEN '#EF4444'
                    WHEN priority = 'medium' THEN '#F59E0B'
                    WHEN priority = 'low' THEN '#10B981'
                    ELSE '#6B7280'
                END as color
            FROM tickets
            GROUP BY priority
            ORDER BY 
                CASE priority 
                    WHEN 'high' THEN 1 
                    WHEN 'medium' THEN 2 
                    WHEN 'low' THEN 3 
                END
        '''
        results = conn.execute(query).fetchall()
        conn.close()
        
        return [{'priority': row['priority'], 'count': row['count'], 'color': row['color']} for row in results]
    
    @staticmethod
    def get_status_distribution():
        """Get ticket distribution by status"""
        conn = get_db_connection()
        query = '''
            SELECT 
                status,
                COUNT(*) as count,
                CASE 
                    WHEN status = 'open' THEN '#3B82F6'
                    WHEN status = 'in_progress' THEN '#F59E0B'
                    WHEN status = 'resolved' THEN '#10B981'
                    WHEN status = 'closed' THEN '#6B7280'
                    ELSE '#8B5CF6'
                END as color
            FROM tickets
            GROUP BY status
            ORDER BY count DESC
        '''
        results = conn.execute(query).fetchall()
        conn.close()
        
        return [{'status': row['status'], 'count': row['count'], 'color': row['color']} for row in results]
    
    @staticmethod
    def get_agent_performance():
        """Get agent performance metrics"""
        conn = get_db_connection()
        query = '''
            SELECT 
                u.username,
                COUNT(t.id) as total_tickets,
                COUNT(CASE WHEN t.status = 'resolved' THEN 1 END) as resolved_tickets,
                AVG(CASE WHEN t.resolved_at IS NOT NULL 
                    THEN JULIANDAY(t.resolved_at) - JULIANDAY(t.created_at) 
                    END) * 24 as avg_resolution_hours
            FROM users u
            LEFT JOIN tickets t ON u.id = t.assigned_to
            WHERE u.role = 'agent'
            GROUP BY u.id, u.username
            ORDER BY resolved_tickets DESC
        '''
        results = conn.execute(query).fetchall()
        conn.close()
        
        return [{
            'agent': row['username'],
            'total_tickets': row['total_tickets'],
            'resolved_tickets': row['resolved_tickets'],
            'resolution_rate': round((row['resolved_tickets'] / row['total_tickets'] * 100), 1) if row['total_tickets'] > 0 else 0,
            'avg_resolution_hours': round(row['avg_resolution_hours'], 2) if row['avg_resolution_hours'] else 0
        } for row in results]

# Routes
@analytics_bp.route('/')
@login_required
def analytics_dashboard():
    """Main analytics dashboard"""
    if not current_user.is_admin():
        return redirect(url_for('agent_dashboard'))
    
    return render_template('analytics/dashboard.html', user=current_user)

@analytics_bp.route('/api/tickets-by-category')
@login_required
def api_tickets_by_category():
    """API endpoint for tickets by category data"""
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = Analytics.get_tickets_by_category()
    return jsonify(data)

@analytics_bp.route('/api/resolution-time')
@login_required
def api_resolution_time():
    """API endpoint for resolution time data"""
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    overall = Analytics.get_average_resolution_time()
    by_category = Analytics.get_resolution_time_by_category()
    
    return jsonify({
        'overall': overall,
        'by_category': by_category
    })

@analytics_bp.route('/api/time-series')
@login_required
def api_time_series():
    """API endpoint for time series data"""
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    days = request.args.get('days', 30, type=int)
    data = Analytics.get_time_series_data(days)
    return jsonify(data)

@analytics_bp.route('/api/priority-distribution')
@login_required
def api_priority_distribution():
    """API endpoint for priority distribution"""
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = Analytics.get_priority_distribution()
    return jsonify(data)

@analytics_bp.route('/api/status-distribution')
@login_required
def api_status_distribution():
    """API endpoint for status distribution"""
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = Analytics.get_status_distribution()
    return jsonify(data)

@analytics_bp.route('/api/agent-performance')
@login_required
def api_agent_performance():
    """API endpoint for agent performance"""
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = Analytics.get_agent_performance()
    return jsonify(data)

# Custom Dashboard Routes
@analytics_bp.route('/custom')
@login_required
def custom_dashboards():
    """Custom dashboards management"""
    if not current_user.is_admin():
        return redirect(url_for('agent_dashboard'))
    
    dashboards = CustomDashboard.get_all_by_user(current_user.id)
    return render_template('analytics/custom_dashboards.html', dashboards=dashboards, user=current_user)

@analytics_bp.route('/custom/create')
@login_required
def create_custom_dashboard():
    """Create new custom dashboard"""
    if not current_user.is_admin():
        return redirect(url_for('agent_dashboard'))
    
    return render_template('analytics/create_dashboard.html', user=current_user)

@analytics_bp.route('/custom/<int:dashboard_id>')
@login_required
def view_custom_dashboard(dashboard_id):
    """View custom dashboard"""
    if not current_user.is_admin():
        return redirect(url_for('agent_dashboard'))
    
    dashboard = CustomDashboard.get_by_id(dashboard_id)
    if not dashboard or dashboard['user_id'] != current_user.id:
        return redirect(url_for('analytics.custom_dashboards'))
    
    return render_template('analytics/custom_dashboard.html', dashboard=dashboard, user=current_user)

class CustomDashboard:
    """Custom Dashboard model"""
    
    @staticmethod
    def create(name, description, config, user_id):
        """Create a new custom dashboard"""
        conn = get_db_connection()
        try:
            cursor = conn.execute('''
                INSERT INTO custom_dashboards (name, description, config, user_id)
                VALUES (?, ?, ?, ?)
            ''', (name, description, json.dumps(config), user_id))
            dashboard_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return dashboard_id
        except Exception as e:
            conn.close()
            raise e
    
    @staticmethod
    def get_all_by_user(user_id):
        """Get all custom dashboards for a user"""
        conn = get_db_connection()
        dashboards = conn.execute('''
            SELECT * FROM custom_dashboards 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (user_id,)).fetchall()
        conn.close()
        return dashboards
    
    @staticmethod
    def get_by_id(dashboard_id):
        """Get custom dashboard by ID"""
        conn = get_db_connection()
        dashboard = conn.execute('''
            SELECT * FROM custom_dashboards WHERE id = ?
        ''', (dashboard_id,)).fetchone()
        conn.close()
        return dashboard
    
    @staticmethod
    def update(dashboard_id, name=None, description=None, config=None):
        """Update custom dashboard"""
        conn = get_db_connection()
        
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if config is not None:
            updates.append("config = ?")
            params.append(json.dumps(config))
        
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(dashboard_id)
        
        query = f"UPDATE custom_dashboards SET {', '.join(updates)} WHERE id = ?"
        
        try:
            conn.execute(query, params)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e
    
    @staticmethod
    def delete(dashboard_id):
        """Delete custom dashboard"""
        conn = get_db_connection()
        try:
            conn.execute('DELETE FROM custom_dashboards WHERE id = ?', (dashboard_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e
