import os
import json
import time
import redis
import subprocess
import shutil
from pathlib import Path
from anthropic import Anthropic
from openai import OpenAI


# Initialize
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
client = OpenAI()


class CodebaseAnalyzer:
    pass


def main():
    """Main worker loop"""
    print("Worker started, waiting for jobs...")
    
    while True:
        try:
            # block and wait for job
            job_id = redis_client.brpop("job_queue", timeout=5)
            
            if job_id:

                # clean the job id
                job_id = job_id[1].decode('utf-8')
                print(f"Processing job: {job_id}")
                
                # fetch a job from the queue
                job_data = json.loads(redis_client.get(f"job:{job_id}"))
                
                # process job
                analyzer = CodebaseAnalyzer(job_id,
                                            job_data['repo_path'],
                                            job_data['output_name']
                                            )
                analyzer.run()
                
                print(f"Job {job_id} completed")
                
        except Exception as e:
            print(f"Error processing job: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()