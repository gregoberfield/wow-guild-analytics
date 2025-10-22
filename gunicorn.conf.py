"""
Gunicorn configuration file for WoW Guild Analytics production deployment.

This configuration is optimized for production use with reasonable defaults.
Adjust the settings based on your server resources and traffic patterns.
"""
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"  # Listen on all interfaces, port 8000
backlog = 2048  # Maximum number of pending connections

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # Recommended: (2 x $num_cores) + 1
worker_class = "sync"  # Use sync workers (suitable for Flask apps)
worker_connections = 1000  # Maximum number of simultaneous clients per worker
max_requests = 1000  # Restart workers after this many requests (prevents memory leaks)
max_requests_jitter = 50  # Randomize max_requests to avoid all workers restarting at once
timeout = 30  # Workers silent for more than this many seconds are killed and restarted
keepalive = 2  # Number of seconds to wait for requests on a Keep-Alive connection

# Logging
accesslog = "logs/gunicorn-access.log"  # Access log file
errorlog = "logs/gunicorn-error.log"  # Error log file
loglevel = "info"  # Logging level (debug, info, warning, error, critical)
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "wow-guild-analytics"  # Process name in ps/top

# Server mechanics
daemon = False  # Don't run in background (use systemd or supervisor instead)
pidfile = "logs/gunicorn.pid"  # PID file location
umask = 0o007  # File permissions for created files
user = None  # Run as this user (None = don't change user)
group = None  # Run as this group (None = don't change group)
tmp_upload_dir = None  # Directory for temporary request data

# SSL/HTTPS (if using Gunicorn for SSL - typically use nginx instead)
# keyfile = None
# certfile = None

# Server hooks for lifecycle events
def on_starting(server):
    """Called just before the master process is initialized."""
    print("Gunicorn is starting...")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    print("Gunicorn is reloading...")

def when_ready(server):
    """Called just after the server is started."""
    print(f"Gunicorn is ready. Listening on {bind}")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    print(f"Worker spawned (pid: {worker.pid})")

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    pass

def worker_int(worker):
    """Called just after a worker received the SIGINT or SIGQUIT signal."""
    print(f"Worker received INT or QUIT signal (pid: {worker.pid})")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    print(f"Worker received SIGABRT signal (pid: {worker.pid})")

def pre_exec(server):
    """Called just before a new master process is forked."""
    print("Forking new master process...")

def pre_request(worker, req):
    """Called just before a worker processes the request."""
    worker.log.debug(f"{req.method} {req.path}")

def post_request(worker, req, environ, resp):
    """Called after a worker processes the request."""
    pass

def child_exit(server, worker):
    """Called just after a worker has been exited."""
    print(f"Worker exited (pid: {worker.pid})")

def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    pass

def nworkers_changed(server, new_value, old_value):
    """Called just after num_workers has been changed."""
    print(f"Number of workers changed from {old_value} to {new_value}")

def on_exit(server):
    """Called just before exiting Gunicorn."""
    print("Gunicorn is shutting down...")

# Environment variables
# Gunicorn will inherit environment variables from the shell
# For production, consider using a .env file and loading it in wsgi.py
raw_env = [
    # Example: 'FLASK_ENV=production',
    # Add any environment variables you want to set here
]
