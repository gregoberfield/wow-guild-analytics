from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services import GuildService
from app.raid_composer import RaidComposerService
from app.models import Guild, Character, GuildMemberHistory, CharacterProgressionHistory, Task
from app import db
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page showing all tracked guilds"""
    guilds = Guild.query.all()
    return render_template('index.html', guilds=guilds)

@main_bp.route('/guild/<int:guild_id>')
def guild_detail(guild_id):
    """Guild detail page with analytics and pagination"""
    # Get sorting parameters from query string
    sort_by = request.args.get('sort_by', 'level')  # default sort by level
    sort_order = request.args.get('sort_order', 'desc')  # default descending
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '', type=str).strip()
    
    # Validate per_page (20, 50, 100, or 0 for all)
    valid_per_page = [20, 50, 100, 0]
    if per_page not in valid_per_page:
        per_page = 20
    
    service = GuildService()
    analytics = service.get_guild_analytics(guild_id)
    
    if not analytics:
        flash('Guild not found', 'error')
        return redirect(url_for('main.index'))
    
    # Get all characters for this guild
    characters_query = Character.query.filter_by(guild_id=guild_id)
    
    # Apply search filter if provided
    if search:
        characters_query = characters_query.filter(
            Character.name.ilike(f'%{search}%')
        )
    
    # Map sort_by parameter to Character model attributes
    valid_sort_columns = {
        'name': Character.name,
        'level': Character.level,
        'class': Character.character_class,
        'race': Character.race,
        'rank': Character.rank,
        'ilvl': Character.average_item_level,
        'gender': Character.gender,
        'spec': Character.spec_name,
        'last_seen': Character.last_login_timestamp
    }
    
    # Apply sorting
    if sort_by in valid_sort_columns:
        sort_column = valid_sort_columns[sort_by]
        if sort_order == 'asc':
            characters_query = characters_query.order_by(sort_column.asc())
        else:
            characters_query = characters_query.order_by(sort_column.desc())
    else:
        # Default sorting
        characters_query = characters_query.order_by(Character.level.desc())
    
    # Get total count before pagination
    total_characters = characters_query.count()
    
    # Apply pagination (if per_page is 0, show all)
    if per_page == 0:
        characters = characters_query.all()
        pagination = None
    else:
        pagination = characters_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        characters = pagination.items
    
    # Add characters and pagination info to analytics
    analytics['characters'] = characters
    analytics['sort_by'] = sort_by
    analytics['sort_order'] = sort_order
    analytics['pagination'] = pagination
    analytics['per_page'] = per_page
    analytics['search'] = search
    analytics['total_characters'] = total_characters
    
    return render_template('guild_detail.html', **analytics)

@main_bp.route('/sync', methods=['GET', 'POST'])
@login_required
def sync_guild():
    """Sync guild roster from Battle.net (now uses background task)"""
    if request.method == 'POST':
        realm_slug = request.form.get('realm_slug')
        guild_name_slug = request.form.get('guild_name_slug')
        
        if not realm_slug or not guild_name_slug:
            flash('Realm and guild name are required', 'error')
            return redirect(url_for('main.sync_guild'))
        
        try:
            # Import here to avoid circular imports
            from app.tasks import sync_guild_roster
            
            # Create task record
            task = Task(
                celery_id='pending',  # Will be updated when task starts
                task_type='guild_sync',
                status='PENDING',
                current_step='Queuing sync task...'
            )
            db.session.add(task)
            db.session.commit()
            
            # Queue background task
            celery_task = sync_guild_roster.apply_async(
                args=[realm_slug, guild_name_slug, task.id]
            )
            
            # Update task with Celery ID
            task.celery_id = celery_task.id
            db.session.commit()
            
            flash('Guild sync started! You can monitor progress below.', 'info')
            return redirect(url_for('main.task_status_page', task_id=task.id))
            
        except Exception as e:
            flash(f'Error starting guild sync: {str(e)}', 'error')
            return redirect(url_for('main.sync_guild'))
    
    return render_template('sync.html')

@main_bp.route('/guild/<int:guild_id>/sync-characters', methods=['POST'])
@login_required
def sync_character_details(guild_id):
    """Sync detailed character information for a guild (now uses background task)"""
    try:
        # Import here to avoid circular imports
        from app.tasks import sync_character_details as sync_char_task
        
        # Create task record
        task = Task(
            celery_id='pending',
            task_type='character_sync',
            status='PENDING',
            guild_id=guild_id,
            current_step='Queuing character sync task...'
        )
        db.session.add(task)
        db.session.commit()
        
        # Queue background task
        celery_task = sync_char_task.apply_async(
            args=[guild_id, task.id]
        )
        
        # Update task with Celery ID
        task.celery_id = celery_task.id
        db.session.commit()
        
        flash('Character sync started! You can monitor progress below.', 'info')
        return redirect(url_for('main.task_status_page', task_id=task.id))
        
    except Exception as e:
        flash(f'Error starting character sync: {str(e)}', 'error')
    
    return redirect(url_for('main.guild_detail', guild_id=guild_id))

@main_bp.route('/guild/<int:guild_id>/history')
def guild_history(guild_id):
    """View guild member history log"""
    guild = Guild.query.get_or_404(guild_id)
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    action_filter = request.args.get('action', None)  # 'added', 'removed', or None for all
    
    # Build query
    query = GuildMemberHistory.query.filter_by(guild_id=guild_id)
    
    # Apply filter if specified
    if action_filter in ['added', 'removed']:
        query = query.filter_by(action=action_filter)
    
    # Order by most recent first
    query = query.order_by(GuildMemberHistory.timestamp.desc())
    
    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    history_entries = pagination.items
    
    # Get summary statistics
    total_added = GuildMemberHistory.query.filter_by(guild_id=guild_id, action='added').count()
    total_removed = GuildMemberHistory.query.filter_by(guild_id=guild_id, action='removed').count()
    
    return render_template('guild_history.html',
                         guild=guild,
                         history_entries=history_entries,
                         pagination=pagination,
                         action_filter=action_filter,
                         total_added=total_added,
                         total_removed=total_removed)

@main_bp.route('/character/<int:character_id>/progression')
def character_progression(character_id):
    """View character progression history"""
    character = Character.query.get_or_404(character_id)
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Query progression history for this character
    progression_query = CharacterProgressionHistory.query.filter_by(
        character_id=character_id
    ).order_by(CharacterProgressionHistory.timestamp.desc())
    
    pagination = progression_query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    progression_entries = pagination.items
    
    # Get statistics
    first_entry = CharacterProgressionHistory.query.filter_by(
        character_id=character_id
    ).order_by(CharacterProgressionHistory.timestamp.asc()).first()
    
    latest_entry = CharacterProgressionHistory.query.filter_by(
        character_id=character_id
    ).order_by(CharacterProgressionHistory.timestamp.desc()).first()
    
    # Calculate gains
    level_gain = 0
    ilvl_gain = 0
    
    if first_entry and latest_entry:
        if first_entry.character_level and latest_entry.character_level:
            level_gain = latest_entry.character_level - first_entry.character_level
        if first_entry.average_item_level and latest_entry.average_item_level:
            ilvl_gain = latest_entry.average_item_level - first_entry.average_item_level
    
    # Prepare data for chart (convert to dict for JSON serialization)
    progression_data_for_chart = []
    for entry in progression_entries:
        progression_data_for_chart.append({
            'character_level': entry.character_level,
            'average_item_level': entry.average_item_level,
            'equipped_item_level': entry.equipped_item_level,
            'timestamp': entry.timestamp.isoformat() if entry.timestamp else None
        })
    
    return render_template('character_progression.html',
                         character=character,
                         progression_entries=progression_entries,
                         progression_data_for_chart=progression_data_for_chart,
                         pagination=pagination,
                         first_entry=first_entry,
                         latest_entry=latest_entry,
                         level_gain=level_gain,
                         ilvl_gain=ilvl_gain)

@main_bp.route('/api/guild/<int:guild_id>/analytics')
def api_guild_analytics(guild_id):
    """API endpoint for guild analytics"""
    service = GuildService()
    analytics = service.get_guild_analytics(guild_id)
    
    if not analytics:
        return jsonify({'error': 'Guild not found'}), 404
    
    return jsonify({
        'guild_name': analytics['guild'].name,
        'total_members': analytics['total_members'],
        'class_distribution': analytics['class_distribution'],
        'race_distribution': analytics['race_distribution'],
        'level_distribution': analytics['level_distribution'],
        'level_class_distribution': analytics['level_class_distribution'],
        'level_60_count': analytics['level_60_count'],
        'level_60_by_class': analytics['level_60_by_class'],
        'level_60_percentages': analytics['level_60_percentages'],
        'average_item_level': analytics['average_item_level'],
        'spec_distribution': analytics['spec_distribution']
    })

@main_bp.route('/api/guild/<int:guild_id>/characters')
def api_guild_characters(guild_id):
    """API endpoint for guild characters"""
    characters = Character.query.filter_by(guild_id=guild_id).all()
    return jsonify([char.to_dict() for char in characters])

@main_bp.route('/guild/<int:guild_id>/raid-composer')
@login_required
def raid_composer(guild_id):
    """AI-powered raid composition suggestion page"""
    guild = Guild.query.get_or_404(guild_id)
    
    # Check if Azure OpenAI is configured
    composer_service = RaidComposerService()
    is_configured = composer_service.is_configured()
    
    # Get level 60 count
    level_60_count = Character.query.filter_by(
        guild_id=guild_id,
        level=60
    ).count()
    
    return render_template('raid_composer.html',
                         guild=guild,
                         level_60_count=level_60_count,
                         is_configured=is_configured)

@main_bp.route('/api/guild/<int:guild_id>/suggest-raid-composition', methods=['POST'])
@login_required
def suggest_raid_composition(guild_id):
    """API endpoint for AI raid composition suggestions"""
    guild = Guild.query.get_or_404(guild_id)
    
    # Get parameters from request
    data = request.get_json() or {}
    raid_size = data.get('raid_size', 40)
    raid_type = data.get('raid_type', 'General')
    
    # Validate raid size
    if raid_size not in [20, 25, 40]:
        return jsonify({'error': 'Invalid raid size. Must be 20, 25, or 40.'}), 400
    
    # Call the AI service
    composer_service = RaidComposerService()
    result = composer_service.suggest_raid_composition(guild_id, raid_size, raid_type)
    
    if result['error']:
        return jsonify(result), 500
    
    return jsonify(result)

# ============================================================================
# Task Status and Monitoring Routes
# ============================================================================

@main_bp.route('/task/<int:task_id>')
@login_required
def task_status_page(task_id):
    """Display task status page with real-time progress updates"""
    task = Task.query.get_or_404(task_id)
    return render_template('task_status.html', task=task)

@main_bp.route('/api/task/<int:task_id>')
def api_task_status(task_id):
    """API endpoint to check task status (polled by frontend)"""
    task = Task.query.get_or_404(task_id)
    
    response = task.to_dict()
    
    # Add redirect URL if task completed successfully
    if task.status == 'SUCCESS' and task.guild_id:
        response['redirect_url'] = url_for('main.guild_detail', guild_id=task.guild_id)
    
    return jsonify(response)

@main_bp.route('/api/tasks/recent')
@login_required
def api_recent_tasks():
    """API endpoint to get recent tasks"""
    limit = request.args.get('limit', 10, type=int)
    tasks = Task.query.order_by(Task.created_at.desc()).limit(limit).all()
    return jsonify([task.to_dict() for task in tasks])

@main_bp.route('/tasks')
@login_required
def task_list():
    """Display list of all tasks"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = Task.query.order_by(Task.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('task_list.html', pagination=pagination)
