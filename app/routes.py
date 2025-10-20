from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services import GuildService
from app.models import Guild, Character
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page showing all tracked guilds"""
    guilds = Guild.query.all()
    return render_template('index.html', guilds=guilds)

@main_bp.route('/guild/<int:guild_id>')
def guild_detail(guild_id):
    """Guild detail page with analytics"""
    # Get sorting parameters from query string
    sort_by = request.args.get('sort_by', 'level')  # default sort by level
    sort_order = request.args.get('sort_order', 'desc')  # default descending
    
    service = GuildService()
    analytics = service.get_guild_analytics(guild_id)
    
    if not analytics:
        flash('Guild not found', 'error')
        return redirect(url_for('main.index'))
    
    # Get all characters for this guild and apply sorting
    characters = Character.query.filter_by(guild_id=guild_id)
    
    # Map sort_by parameter to Character model attributes
    valid_sort_columns = {
        'name': Character.name,
        'level': Character.level,
        'class': Character.character_class,
        'race': Character.race,
        'rank': Character.rank,
        'ilvl': Character.average_item_level,
        'gender': Character.gender,
        'spec': Character.spec_name
    }
    
    # Apply sorting
    if sort_by in valid_sort_columns:
        sort_column = valid_sort_columns[sort_by]
        if sort_order == 'asc':
            characters = characters.order_by(sort_column.asc())
        else:
            characters = characters.order_by(sort_column.desc())
    else:
        # Default sorting
        characters = characters.order_by(Character.level.desc())
    
    characters = characters.all()
    
    # Add characters and sorting info to analytics
    analytics['characters'] = characters
    analytics['sort_by'] = sort_by
    analytics['sort_order'] = sort_order
    
    return render_template('guild_detail.html', **analytics)

@main_bp.route('/sync', methods=['GET', 'POST'])
@login_required
def sync_guild():
    """Sync guild roster from Battle.net"""
    if request.method == 'POST':
        realm_slug = request.form.get('realm_slug')
        guild_name_slug = request.form.get('guild_name_slug')
        
        if not realm_slug or not guild_name_slug:
            flash('Realm and guild name are required', 'error')
            return redirect(url_for('main.sync_guild'))
        
        try:
            service = GuildService()
            guild, member_count, removed_count = service.sync_guild_roster(realm_slug, guild_name_slug)
            
            # Build success message
            success_msg = f'Successfully synced {member_count} members from {guild.name}'
            if removed_count > 0:
                success_msg += f' ({removed_count} member{"s" if removed_count != 1 else ""} removed)'
            
            flash(success_msg, 'success')
            return redirect(url_for('main.guild_detail', guild_id=guild.id))
        except Exception as e:
            flash(f'Error syncing guild: {str(e)}', 'error')
            return redirect(url_for('main.sync_guild'))
    
    return render_template('sync.html')

@main_bp.route('/guild/<int:guild_id>/sync-characters', methods=['POST'])
@login_required
def sync_character_details(guild_id):
    """Sync detailed character information for a guild"""
    try:
        service = GuildService()
        result = service.sync_character_details(guild_id)
        flash(f'Character sync completed! Successfully updated {result["successful"]} out of {result["total"]} characters.', 'success')
    except Exception as e:
        flash(f'Error syncing character details: {str(e)}', 'error')
    
    return redirect(url_for('main.guild_detail', guild_id=guild_id))

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
