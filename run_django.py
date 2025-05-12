#!/usr/bin/env python
import os
import subprocess
import sys

def run_django_server():
    """
    Run Django development server on port 5000 with proper settings
    for Replit environment
    """
    try:
        # Make migrations
        subprocess.run(["python", "manage.py", "makemigrations"], check=True)
        
        # Apply migrations
        subprocess.run(["python", "manage.py", "migrate"], check=True)
        
        # Run server
        os.environ.setdefault("PYTHONUNBUFFERED", "1")
        subprocess.run([
            "python", "manage.py", "runserver", "0.0.0.0:5000"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer shut down")
        sys.exit(0)

if __name__ == "__main__":
    run_django_server()