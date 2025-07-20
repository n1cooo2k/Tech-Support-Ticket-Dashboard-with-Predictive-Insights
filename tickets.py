from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ticket_models import Ticket, Category, Comment
from models import User
from database import get_db_connection

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/tickets')
@login_required
def ticket_list():
    """Display list of tickets based on user role"""
    try:
        if current_user.is_admin():
            tickets = Ticket.get_all(user_role='admin')
        else:
            tickets = Ticket.get_all(user_role='agent', user_id=current_user.id)
        
        categories = Category.get_all()
        return render_template('tickets/ticket_list.html', tickets=tickets, categories=categories)
    except Exception as e:
        flash(f'Error loading tickets: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@tickets_bp.route('/tickets/create', methods=['GET', 'POST'])
@login_required
def create_ticket():
    """Create a new ticket"""
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            priority = request.form.get('priority', 'medium')
            category_id = request.form.get('category_id')
            assigned_to = request.form.get('assigned_to') if current_user.is_admin() else None
            
            # Validation
            if not title or not description:
                flash('Title and description are required.', 'error')
                return redirect(url_for('tickets.create_ticket'))
            
            if category_id:
                category_id = int(category_id)
            else:
                category_id = None
            
            if assigned_to:
                assigned_to = int(assigned_to) if assigned_to != '' else None
            
            # Create ticket
            ticket_id = Ticket.create(
                title=title,
                description=description,
                priority=priority,
                category_id=category_id,
                created_by=current_user.id,
                assigned_to=assigned_to
            )
            
            flash('Ticket created successfully!', 'success')
            return redirect(url_for('tickets.ticket_detail', ticket_id=ticket_id))
            
        except Exception as e:
            flash(f'Error creating ticket: {str(e)}', 'error')
    
    # GET request - show form
    categories = Category.get_all()
    agents = []
    
    if current_user.is_admin():
        # Get all agents for assignment
        conn = get_db_connection()
        agents = conn.execute("SELECT id, username FROM users WHERE role = 'agent'").fetchall()
        conn.close()
    
    return render_template('tickets/ticket_create.html', categories=categories, agents=agents)

@tickets_bp.route('/tickets/<int:ticket_id>')
@login_required
def ticket_detail(ticket_id):
    """Display ticket details"""
    try:
        ticket = Ticket.get_by_id(ticket_id)
        
        if not ticket:
            flash('Ticket not found.', 'error')
            return redirect(url_for('tickets.ticket_list'))
        
        # Check permissions
        if not current_user.is_admin():
            if ticket['created_by'] != current_user.id and ticket['assigned_to'] != current_user.id:
                flash('You do not have permission to view this ticket.', 'error')
                return redirect(url_for('tickets.ticket_list'))
        
        # Get comments
        comments = Comment.get_by_ticket(ticket_id)
        
        # Get categories and agents for editing
        categories = Category.get_all()
        agents = []
        
        if current_user.is_admin():
            conn = get_db_connection()
            agents = conn.execute("SELECT id, username FROM users WHERE role = 'agent'").fetchall()
            conn.close()
        
        return render_template('tickets/ticket_detail.html', 
                             ticket=ticket, comments=comments, 
                             categories=categories, agents=agents)
        
    except Exception as e:
        flash(f'Error loading ticket: {str(e)}', 'error')
        return redirect(url_for('tickets.ticket_list'))

@tickets_bp.route('/tickets/<int:ticket_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_ticket(ticket_id):
    """Edit ticket"""
    try:
        ticket = Ticket.get_by_id(ticket_id)
        
        if not ticket:
            flash('Ticket not found.', 'error')
            return redirect(url_for('tickets.ticket_list'))
        
        # Check permissions
        if not current_user.is_admin():
            if ticket['created_by'] != current_user.id and ticket['assigned_to'] != current_user.id:
                flash('You do not have permission to edit this ticket.', 'error')
                return redirect(url_for('tickets.ticket_detail', ticket_id=ticket_id))
        
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            status = request.form.get('status')
            priority = request.form.get('priority')
            category_id = request.form.get('category_id')
            assigned_to = request.form.get('assigned_to') if current_user.is_admin() else None
            
            # Validation
            if not title or not description:
                flash('Title and description are required.', 'error')
                return redirect(url_for('tickets.edit_ticket', ticket_id=ticket_id))
            
            # Prepare update parameters
            update_params = {
                'title': title,
                'description': description,
                'status': status,
                'priority': priority,
                'category_id': int(category_id) if category_id else None
            }
            
            if current_user.is_admin() and assigned_to is not None:
                update_params['assigned_to'] = int(assigned_to) if assigned_to != '' else None
            
            # Update ticket
            Ticket.update(ticket_id, **update_params)
            
            flash('Ticket updated successfully!', 'success')
            return redirect(url_for('tickets.ticket_detail', ticket_id=ticket_id))
        
        # GET request - show form
        categories = Category.get_all()
        agents = []
        
        if current_user.is_admin():
            conn = get_db_connection()
            agents = conn.execute("SELECT id, username FROM users WHERE role = 'agent'").fetchall()
            conn.close()
        
        return render_template('tickets/ticket_edit.html', 
                             ticket=ticket, categories=categories, agents=agents)
        
    except Exception as e:
        flash(f'Error editing ticket: {str(e)}', 'error')
        return redirect(url_for('tickets.ticket_detail', ticket_id=ticket_id))

@tickets_bp.route('/tickets/<int:ticket_id>/delete', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    """Delete ticket (admin only)"""
    if not current_user.is_admin():
        flash('You do not have permission to delete tickets.', 'error')
        return redirect(url_for('tickets.ticket_detail', ticket_id=ticket_id))
    
    try:
        ticket = Ticket.get_by_id(ticket_id)
        
        if not ticket:
            flash('Ticket not found.', 'error')
            return redirect(url_for('tickets.ticket_list'))
        
        Ticket.delete(ticket_id)
        flash('Ticket deleted successfully!', 'success')
        return redirect(url_for('tickets.ticket_list'))
        
    except Exception as e:
        flash(f'Error deleting ticket: {str(e)}', 'error')
        return redirect(url_for('tickets.ticket_detail', ticket_id=ticket_id))

@tickets_bp.route('/tickets/<int:ticket_id>/comments', methods=['POST'])
@login_required
def add_comment(ticket_id):
    """Add comment to ticket"""
    try:
        ticket = Ticket.get_by_id(ticket_id)
        
        if not ticket:
            flash('Ticket not found.', 'error')
            return redirect(url_for('tickets.ticket_list'))
        
        # Check permissions
        if not current_user.is_admin():
            if ticket['created_by'] != current_user.id and ticket['assigned_to'] != current_user.id:
                flash('You do not have permission to comment on this ticket.', 'error')
                return redirect(url_for('tickets.ticket_list'))
        
        comment_text = request.form.get('comment', '').strip()
        
        if not comment_text:
            flash('Comment cannot be empty.', 'error')
            return redirect(url_for('tickets.ticket_detail', ticket_id=ticket_id))
        
        Comment.create(ticket_id, current_user.id, comment_text)
        flash('Comment added successfully!', 'success')
        
        return redirect(url_for('tickets.ticket_detail', ticket_id=ticket_id))
        
    except Exception as e:
        flash(f'Error adding comment: {str(e)}', 'error')
        return redirect(url_for('tickets.ticket_detail', ticket_id=ticket_id))

@tickets_bp.route('/tickets/<int:ticket_id>/status', methods=['POST'])
@login_required
def update_status(ticket_id):
    """Quick status update"""
    try:
        ticket = Ticket.get_by_id(ticket_id)
        
        if not ticket:
            return jsonify({'success': False, 'message': 'Ticket not found'})
        
        # Check permissions
        if not current_user.is_admin():
            if ticket['created_by'] != current_user.id and ticket['assigned_to'] != current_user.id:
                return jsonify({'success': False, 'message': 'Permission denied'})
        
        new_status = request.json.get('status')
        
        if new_status not in ['open', 'in_progress', 'resolved', 'closed']:
            return jsonify({'success': False, 'message': 'Invalid status'})
        
        Ticket.update(ticket_id, status=new_status)
        
        return jsonify({'success': True, 'message': 'Status updated successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@tickets_bp.route('/api/tickets/stats')
@login_required
def ticket_stats():
    """Get ticket statistics (admin only)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        stats = Ticket.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
