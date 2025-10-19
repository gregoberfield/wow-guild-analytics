from app import create_app
import logging

app = create_app()

if __name__ == '__main__':
    # Additional console logging for when run directly
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    
    # Add console handler to root logger
    logging.root.addHandler(console_handler)
    logging.root.setLevel(logging.INFO)
    
    print("=" * 60)
    print("WoW Guild Analytics - Starting Server")
    print("=" * 60)
    print(f"Server: http://localhost:5000")
    print(f"Logs: logs/app.log")
    print(f"Press CTRL+C to quit")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
