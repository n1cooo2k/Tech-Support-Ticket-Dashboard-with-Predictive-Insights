from database import get_db_connection
from datetime import datetime

class Ticket:
    """Ticket model for support tickets"""
    
    def __init__(self, id, title, description, status, priority, category_id, 
                 created_by, assigned_to, created_at, updated_at, resolved_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.category_id = category_id
        self.created_by = created_by
        self.assigned_to = assigned_to
        self.created_at = created_at
        self.updated_at = updated_at
        self.resolved_at = resolved_at
    
    @staticmethod
    def create(title, description, priority, category_id, created_by, assigned_to=None):
        """Create a new ticket"""
        conn = get_db_connection()
        try:
            cursor = conn.execute('''
                INSERT INTO tickets (title, description, priority, category_id, created_by, assigned_to)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, description, priority, category_id, created_by, assigned_to))
            ticket_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return ticket_id
        except Exception as e:
            conn.close()
            raise e
    
    @staticmethod
    def get_all(user_role=None, user_id=None, filters=None):
        """Get all tickets based on user role and filters"""
        conn = get_db_connection()
        
        # Base query
        base_query = '''
            SELECT t.*, c.name as category_name, c.color as category_color,
                   creator.username as created_by_username,
                   assignee.username as assigned_to_username
            FROM tickets t
            LEFT JOIN categories c ON t.category_id = c.id
            LEFT JOIN users creator ON t.created_by = creator.id
            LEFT JOIN users assignee ON t.assigned_to = assignee.id
        '''
        
        where_conditions = []
        params = []
        
        # Role-based filtering
        if user_role != 'admin':
            where_conditions.append('(t.assigned_to = ? OR t.created_by = ?)')
            params.extend([user_id, user_id])
        
        # Apply filters if provided
        if filters:
            # Search filter
            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                where_conditions.append('(LOWER(t.title) LIKE LOWER(?) OR LOWER(t.description) LIKE LOWER(?))')
                params.extend([search_term, search_term])
            
            # Status filter
            if filters.get('status'):
                where_conditions.append('t.status = ?')
                params.append(filters['status'])
            
            # Priority filter
            if filters.get('priority'):
                where_conditions.append('t.priority = ?')
                params.append(filters['priority'])
            
            # Category filter
            if filters.get('category'):
                where_conditions.append('c.name = ?')
                params.append(filters['category'])
            
            # User filter (created by)
            if filters.get('created_by'):
                where_conditions.append('creator.username = ?')
                params.append(filters['created_by'])
            
            # Assigned to filter
            if filters.get('assigned_to'):
                if filters['assigned_to'] == 'unassigned':
                    where_conditions.append('t.assigned_to IS NULL')
                else:
                    where_conditions.append('assignee.username = ?')
                    params.append(filters['assigned_to'])
            
            # Date range filters
            if filters.get('date_from'):
                where_conditions.append('DATE(t.created_at) >= ?')
                params.append(filters['date_from'])
            
            if filters.get('date_to'):
                where_conditions.append('DATE(t.created_at) <= ?')
                params.append(filters['date_to'])
            
            # Last updated filter
            if filters.get('updated_from'):
                where_conditions.append('DATE(t.updated_at) >= ?')
                params.append(filters['updated_from'])
            
            if filters.get('updated_to'):
                where_conditions.append('DATE(t.updated_at) <= ?')
                params.append(filters['updated_to'])
        
        # Construct final query
        if where_conditions:
            query = base_query + ' WHERE ' + ' AND '.join(where_conditions)
        else:
            query = base_query
        
        # Add sorting
        sort_by = filters.get('sort_by', 'created_at') if filters else 'created_at'
        sort_order = filters.get('sort_order', 'DESC') if filters else 'DESC'
        
        # Validate sort parameters
        valid_sort_fields = ['created_at', 'updated_at', 'title', 'status', 'priority']
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        
        if sort_order not in ['ASC', 'DESC']:
            sort_order = 'DESC'
        
        query += f' ORDER BY t.{sort_by} {sort_order}'
        
        tickets = conn.execute(query, params).fetchall()
        conn.close()
        return tickets
    
    @staticmethod
    def get_by_id(ticket_id):
        """Get ticket by ID"""
        conn = get_db_connection()
        ticket = conn.execute('''
            SELECT t.*, c.name as category_name, c.color as category_color,
                   creator.username as created_by_username,
                   assignee.username as assigned_to_username
            FROM tickets t
            LEFT JOIN categories c ON t.category_id = c.id
            LEFT JOIN users creator ON t.created_by = creator.id
            LEFT JOIN users assignee ON t.assigned_to = assignee.id
            WHERE t.id = ?
        ''', (ticket_id,)).fetchone()
        conn.close()
        return ticket
    
    @staticmethod
    def update(ticket_id, title=None, description=None, status=None, priority=None, 
               category_id=None, assigned_to=None):
        """Update ticket"""
        conn = get_db_connection()
        
        # Build dynamic update query
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if status is not None:
            updates.append("status = ?")
            params.append(status)
            if status == 'resolved':
                updates.append("resolved_at = ?")
                params.append(datetime.now().isoformat())
        if priority is not None:
            updates.append("priority = ?")
            params.append(priority)
        if category_id is not None:
            updates.append("category_id = ?")
            params.append(category_id)
        if assigned_to is not None:
            updates.append("assigned_to = ?")
            params.append(assigned_to)
        
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(ticket_id)
        
        query = f"UPDATE tickets SET {', '.join(updates)} WHERE id = ?"
        
        try:
            conn.execute(query, params)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e
    
    @staticmethod
    def delete(ticket_id):
        """Delete ticket"""
        conn = get_db_connection()
        try:
            conn.execute('DELETE FROM tickets WHERE id = ?', (ticket_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e
    
    @staticmethod
    def get_stats():
        """Get ticket statistics"""
        conn = get_db_connection()
        
        # Total tickets
        total = conn.execute('SELECT COUNT(*) FROM tickets').fetchone()[0]
        
        # Tickets by status
        open_tickets = conn.execute("SELECT COUNT(*) FROM tickets WHERE status = 'open'").fetchone()[0]
        in_progress = conn.execute("SELECT COUNT(*) FROM tickets WHERE status = 'in_progress'").fetchone()[0]
        resolved = conn.execute("SELECT COUNT(*) FROM tickets WHERE status = 'resolved'").fetchone()[0]
        closed = conn.execute("SELECT COUNT(*) FROM tickets WHERE status = 'closed'").fetchone()[0]
        
        # Tickets by priority
        high_priority = conn.execute("SELECT COUNT(*) FROM tickets WHERE priority = 'high'").fetchone()[0]
        medium_priority = conn.execute("SELECT COUNT(*) FROM tickets WHERE priority = 'medium'").fetchone()[0]
        low_priority = conn.execute("SELECT COUNT(*) FROM tickets WHERE priority = 'low'").fetchone()[0]
        
        conn.close()
        
        return {
            'total': total,
            'open': open_tickets,
            'in_progress': in_progress,
            'resolved': resolved,
            'closed': closed,
            'high_priority': high_priority,
            'medium_priority': medium_priority,
            'low_priority': low_priority
        }

class Category:
    """Category model for ticket categories"""
    
    @staticmethod
    def get_all():
        """Get all categories"""
        conn = get_db_connection()
        categories = conn.execute('SELECT * FROM categories ORDER BY name').fetchall()
        conn.close()
        return categories
    
    @staticmethod
    def get_by_id(category_id):
        """Get category by ID"""
        conn = get_db_connection()
        category = conn.execute('SELECT * FROM categories WHERE id = ?', (category_id,)).fetchone()
        conn.close()
        return category

class Comment:
    """Comment model for ticket comments"""
    
    @staticmethod
    def create(ticket_id, user_id, comment):
        """Create a new comment"""
        conn = get_db_connection()
        try:
            cursor = conn.execute('''
                INSERT INTO comments (ticket_id, user_id, comment)
                VALUES (?, ?, ?)
            ''', (ticket_id, user_id, comment))
            comment_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return comment_id
        except Exception as e:
            conn.close()
            raise e
    
    @staticmethod
    def get_by_ticket(ticket_id):
        """Get all comments for a ticket"""
        conn = get_db_connection()
        comments = conn.execute('''
            SELECT c.*, u.username, u.role
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.ticket_id = ?
            ORDER BY c.created_at ASC
        ''', (ticket_id,)).fetchall()
        conn.close()
        return comments
    
    @staticmethod
    def delete(comment_id):
        """Delete comment"""
        conn = get_db_connection()
        try:
            conn.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e
