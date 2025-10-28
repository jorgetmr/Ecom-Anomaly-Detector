import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


from detection import apply_detector
from dotenv import load_dotenv
from celery import Celery

load_dotenv()

app = Celery(__name__, broker=os.getenv("REDIS_URL"), backend = os.getenv("REDIS_URL"))

app.conf.imports = ("detection.apply_detector")

app.conf.beat_schedule = {
    "detect-every-60s": {"task": "detection.apply_detector.celery_detect", "schedule": 60.0}
}

app.conf.timezone = "UTC"