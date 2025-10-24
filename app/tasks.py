"""
Celery background tasks for long-running operations
"""
from app.celery_config import celery
from app import create_app, db
from app.models import Guild, Character, Task
from app.services import GuildService
from datetime import datetime
from celery import current_task
from celery.exceptions import SoftTimeLimitExceeded
import logging

logger = logging.getLogger(__name__)

# Create Flask app context for tasks
flask_app = create_app()


def update_task_progress(task_record, progress, current_step, status='STARTED'):
    """Update task progress in database"""
    with flask_app.app_context():
        try:
            task_record.progress = progress
            task_record.current_step = current_step
            task_record.status = status
            if status == 'STARTED' and not task_record.started_at:
                task_record.started_at = datetime.utcnow()
            db.session.commit()
            
            # Update Celery task state
            current_task.update_state(
                state=status,
                meta={
                    'progress': progress,
                    'current_step': current_step
                }
            )
        except Exception as e:
            logger.error(f"Error updating task progress: {str(e)}")
            db.session.rollback()


@celery.task(bind=True, name='app.tasks.sync_guild_roster', max_retries=3, soft_time_limit=300)
def sync_guild_roster(self, realm_slug, guild_name_slug, task_id=None):
    """
    Background task to sync guild roster from Battle.net API
    
    Args:
        realm_slug: Realm identifier
        guild_name_slug: Guild name identifier
        task_id: Database task record ID for progress tracking
    """
    with flask_app.app_context():
        task_record = None
        
        try:
            # Get or create task record
            if task_id:
                task_record = Task.query.get(task_id)
            
            if not task_record:
                task_record = Task(
                    celery_id=self.request.id,
                    task_type='guild_sync',
                    status='STARTED'
                )
                db.session.add(task_record)
                db.session.commit()
                task_id = task_record.id
            
            # Update progress: Starting
            update_task_progress(task_record, 10, "Initializing guild sync...")
            
            # Create service and sync
            service = GuildService()
            
            update_task_progress(task_record, 20, "Fetching guild information from Battle.net...")
            
            # Perform the sync
            guild, member_count, removed_count = service.sync_guild_roster(realm_slug, guild_name_slug)
            
            # Update task with guild_id
            task_record.guild_id = guild.id
            
            update_task_progress(task_record, 90, f"Synced {member_count} members, removed {removed_count}")
            
            # Build success message
            success_msg = f'Successfully synced {member_count} members from {guild.name}'
            if removed_count > 0:
                success_msg += f' ({removed_count} member{"s" if removed_count != 1 else ""} removed)'
            success_msg += '. Character detail sync scheduled.'
            
            # Mark as complete
            task_record.status = 'SUCCESS'
            task_record.progress = 100
            task_record.current_step = "Sync completed"
            task_record.result_message = success_msg
            task_record.completed_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Guild sync completed: {success_msg}")
            
            # Automatically schedule character detail sync after successful guild sync
            logger.info(f"Scheduling character detail sync for guild {guild.id}...")
            sync_character_details.delay(guild.id)
            logger.info(f"Character detail sync task queued for guild {guild.id}")
            
            return {
                'status': 'success',
                'guild_id': guild.id,
                'guild_name': guild.name,
                'member_count': member_count,
                'removed_count': removed_count,
                'message': success_msg
            }
            
        except SoftTimeLimitExceeded:
            # Task took too long
            error_msg = "Guild sync timed out (exceeded 5 minutes)"
            logger.error(error_msg)
            
            if task_record:
                task_record.status = 'FAILURE'
                task_record.error_message = error_msg
                task_record.completed_at = datetime.utcnow()
                db.session.commit()
            
            raise
            
        except Exception as e:
            # Handle errors
            error_msg = f"Error syncing guild: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            if task_record:
                task_record.status = 'FAILURE'
                task_record.error_message = error_msg
                task_record.completed_at = datetime.utcnow()
                db.session.commit()
            
            # Retry if this is a transient error (network, API issues)
            if 'connection' in str(e).lower() or 'timeout' in str(e).lower():
                raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds
            
            raise


@celery.task(bind=True, name='app.tasks.sync_character_details', max_retries=3, soft_time_limit=600)
def sync_character_details(self, guild_id, task_id=None):
    """
    Background task to sync detailed character information for a guild
    
    Args:
        guild_id: Database ID of the guild
        task_id: Database task record ID for progress tracking
    """
    with flask_app.app_context():
        task_record = None
        
        try:
            # Get or create task record
            if task_id:
                task_record = Task.query.get(task_id)
            
            if not task_record:
                task_record = Task(
                    celery_id=self.request.id,
                    task_type='character_sync',
                    status='STARTED',
                    guild_id=guild_id
                )
                db.session.add(task_record)
                db.session.commit()
                task_id = task_record.id
            
            # Update progress: Starting
            update_task_progress(task_record, 10, "Initializing character sync...")
            
            # Create service and sync
            service = GuildService()
            
            update_task_progress(task_record, 20, "Fetching character details from Battle.net...")
            
            # Perform the sync
            result = service.sync_character_details(guild_id)
            
            update_task_progress(task_record, 90, f"Synced {result['successful']} of {result['total']} characters")
            
            # Build success message
            success_msg = f"Character sync completed! Successfully updated {result['successful']} out of {result['total']} characters."
            if result.get('failed', 0) > 0:
                success_msg += f" ({result['failed']} failed)"
            
            # Mark as complete
            task_record.status = 'SUCCESS'
            task_record.progress = 100
            task_record.current_step = "Sync completed"
            task_record.result_message = success_msg
            task_record.completed_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Character sync completed: {success_msg}")
            
            return {
                'status': 'success',
                'guild_id': guild_id,
                'total': result['total'],
                'successful': result['successful'],
                'failed': result.get('failed', 0),
                'message': success_msg
            }
            
        except SoftTimeLimitExceeded:
            # Task took too long
            error_msg = "Character sync timed out (exceeded 10 minutes)"
            logger.error(error_msg)
            
            if task_record:
                task_record.status = 'FAILURE'
                task_record.error_message = error_msg
                task_record.completed_at = datetime.utcnow()
                db.session.commit()
            
            raise
            
        except Exception as e:
            # Handle errors
            error_msg = f"Error syncing characters: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            if task_record:
                task_record.status = 'FAILURE'
                task_record.error_message = error_msg
                task_record.completed_at = datetime.utcnow()
                db.session.commit()
            
            # Retry if this is a transient error
            if 'connection' in str(e).lower() or 'timeout' in str(e).lower():
                raise self.retry(exc=e, countdown=120)  # Retry after 2 minutes
            
            raise


@celery.task(name='app.tasks.sync_all_guilds_scheduled')
def sync_all_guilds_scheduled():
    """
    Scheduled task to sync all guilds daily (runs at 3 AM via Celery Beat)
    """
    with flask_app.app_context():
        try:
            logger.info("Starting scheduled sync of all guilds")
            
            guilds = Guild.query.all()
            total_guilds = len(guilds)
            
            if total_guilds == 0:
                logger.info("No guilds to sync")
                return {'status': 'success', 'message': 'No guilds to sync'}
            
            logger.info(f"Found {total_guilds} guilds to sync")
            
            results = []
            for i, guild in enumerate(guilds, 1):
                try:
                    logger.info(f"Syncing guild {i}/{total_guilds}: {guild.name} on {guild.realm}")
                    
                    # Create task record
                    task_record = Task(
                        celery_id=f"scheduled-{guild.id}-{datetime.utcnow().timestamp()}",
                        task_type='guild_sync',
                        status='PENDING',
                        guild_id=guild.id
                    )
                    db.session.add(task_record)
                    db.session.commit()
                    
                    # Trigger async guild sync
                    # Use apply_async to run in background and not block this task
                    task_result = sync_guild_roster.apply_async(
                        args=[guild.realm.lower().replace(' ', '-'), 
                              guild.name.lower().replace(' ', '-'),
                              task_record.id]
                    )
                    
                    results.append({
                        'guild_id': guild.id,
                        'guild_name': guild.name,
                        'task_id': task_result.id,
                        'status': 'queued'
                    })
                    
                except Exception as e:
                    logger.error(f"Error queuing sync for {guild.name}: {str(e)}")
                    results.append({
                        'guild_id': guild.id,
                        'guild_name': guild.name,
                        'status': 'error',
                        'error': str(e)
                    })
            
            success_count = sum(1 for r in results if r['status'] == 'queued')
            logger.info(f"Scheduled sync complete: {success_count}/{total_guilds} guilds queued")
            
            return {
                'status': 'success',
                'total_guilds': total_guilds,
                'queued': success_count,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error in scheduled guild sync: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e)
            }
