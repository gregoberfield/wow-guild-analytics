from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app.models import User
from app import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('You must be an administrator to access this page.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def index():
    """Admin dashboard"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/index.html', users=users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    """Add a new user"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        is_admin = request.form.get('is_admin') == 'on'
        
        # Validation
        if not username or not email or not password:
            flash('Username, email, and password are required', 'error')
            return render_template('admin/add_user.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('admin/add_user.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('admin/add_user.html')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('admin/add_user.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('admin/add_user.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            is_admin=is_admin,
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {username} created successfully', 'success')
        return redirect(url_for('admin.index'))
    
    return render_template('admin/add_user.html')

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Edit an existing user"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        is_admin = request.form.get('is_admin') == 'on'
        is_active = request.form.get('is_active') == 'on'
        
        # If editing own account, preserve admin status and active status
        # (disabled checkboxes don't submit values)
        if user.id == current_user.id:
            is_admin = user.is_admin  # Keep current admin status
            is_active = user.is_active  # Keep current active status
        
        # Validation
        if not username or not email:
            flash('Username and email are required', 'error')
            return render_template('admin/edit_user.html', user=user)
        
        # Check if username changed and is taken
        if username != user.username and User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('admin/edit_user.html', user=user)
        
        # Check if email changed and is taken
        if email != user.email and User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('admin/edit_user.html', user=user)
        
        # Update password if provided
        if password:
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return render_template('admin/edit_user.html', user=user)
            
            if len(password) < 6:
                flash('Password must be at least 6 characters long', 'error')
                return render_template('admin/edit_user.html', user=user)
            
            user.set_password(password)
        
        # Update user (admin and active status already set above for self-edits)
        user.username = username
        user.email = email
        user.is_admin = is_admin
        user.is_active = is_active
        
        db.session.commit()
        
        flash(f'User {username} updated successfully', 'success')
        return redirect(url_for('admin.index'))
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent user from deleting themselves
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('admin.index'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} deleted successfully', 'success')
    return redirect(url_for('admin.index'))

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    # Prevent user from deactivating themselves
    if user.id == current_user.id:
        flash('You cannot deactivate your own account', 'error')
        return redirect(url_for('admin.index'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} {status} successfully', 'success')
    return redirect(url_for('admin.index'))
