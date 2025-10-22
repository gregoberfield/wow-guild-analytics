"""
Celery configuration for background task processing
"""
from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

# Redis URL from environment or default to localhost
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

def make_celery(app_name=__name__):
    """Create and configure Celery instance"""
    celery = Celery(
        app_name,
        broker=REDIS_URL,
        backend=REDIS_URL,
        include=['app.tasks']  # Import tasks module
    )
    
    # Celery configuration
    celery.conf.update(
        # Task result settings
        result_expires=3600,  # Results expire after 1 hour
        result_persistent=True,  # Store results in Redis
        
        # Task execution settings
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        
        # Worker settings
        worker_prefetch_multiplier=1,  # Take one task at a time
        worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks (prevent memory leaks)
        
        # Task tracking
        task_track_started=True,  # Track when tasks start
        task_send_sent_event=True,  # Send task-sent events
        
        # Retry settings
        task_acks_late=True,  # Acknowledge task after completion (safer)
        task_reject_on_worker_lost=True,  # Requeue tasks if worker dies
        
        # Rate limiting (prevent API abuse)
        task_default_rate_limit='10/m',  # Max 10 tasks per minute by default
        
        # Beat schedule for periodic tasks
        beat_schedule={
            'sync-all-guilds-daily': {
                'task': 'app.tasks.sync_all_guilds_scheduled',
                'schedule': crontab(hour=3, minute=0),  # Run at 3 AM daily
                'options': {
                    'expires': 3600,  # Task expires if not run within 1 hour
                }
            },
        },
    )
    
    return celery

# Create Celery instance
celery = make_celery('wow_guild_analytics')
