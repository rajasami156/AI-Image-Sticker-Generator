from main_celery import celery_app

# Start the Celery worker with the app defined in main.py
if __name__ == "__main__":
    celery_app.start()
