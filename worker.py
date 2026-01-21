#!/usr/bin/env python3
import os
import sys
import json
import time
import logging
from redis import Redis
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Redis Connection
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
QUEUE_NAME = 'dreamweaving_pending'

def process_job(job):
    """
    Process a single job.
    job structure: { "id": "...", "data": { "ssml": "...", "voice": "..." } }
    """
    try:
        data = job.get('data', {})
        job_id = job.get('id')
        logger.info(f"🔨 Processing Job {job_id}...")
        
        # Here we would call the actual synthesis logic
        # For now, we simulate success
        time.sleep(2) # Simulate work
        
        logger.info(f"✅ Job {job_id} Completed successfully.")
        
    except Exception as e:
        logger.error(f"❌ Error processing job: {e}")

def start_worker():
    """Starts a simple Redis List consumer worker."""
    logger.info(f"🚀 Starting Dreamweaving List Consumer...")
    logger.info(f"🔌 Connecting to Redis at {REDIS_URL}")
    logger.info(f"👂 Waiting for jobs in list: {QUEUE_NAME}")

    try:
        conn = Redis.from_url(REDIS_URL)
        
        while True:
            # Blocking pop (wait indefinitely for a job)
            # blpop returns tuple (key, value)
            _, payload = conn.blpop(QUEUE_NAME)
            
            if payload:
                try:
                    job = json.loads(payload)
                    process_job(job)
                except json.JSONDecodeError:
                    logger.error("❌ Failed to decode JSON payload")
            
    except KeyboardInterrupt:
        logger.info("🛑 Helper stopping...")
    except Exception as e:
        logger.error(f"❌ Worker crashed: {e}")
        time.sleep(5) # Prevent tight loop on error
        start_worker()

if __name__ == '__main__':
    start_worker()
