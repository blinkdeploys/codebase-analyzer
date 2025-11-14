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

DIRS_EXCLUDED = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build'}
CODE_EXTENSIONS = ['.py', '.js', '.ts', '.java', '.go', '.rs', '.cpp', '.c', '.h', '.jsx', '.tsx', '.vue', '.rb', '.php', '.cs', '.swift', '.kt']

class CodebaseAnalyzer:
    def __init__(self, job_id, repo_path, output_name):
        # queued job id
        self.job_id = job_id
        # codebase repo path
        self.repo_path = Path(repo_path)
        # output codebase path
        self.output_path = Path("/app/output") / output_name
        # work directory
        self.workdir = Path("/app/workdir") / job_id

    def update_progress(self):
        """Update job progress in Redis"""
        job_data = json.loads(redis_client.get(f"job:{self.job_id}"))
        job_data["status"] = status
        job_data["progress"] = progress_data
        redis_client.set(f"job:{self.job_id}", json.dumps(job_data))

    def scan_codebase(self):
        """Scan and collect all code files"""
        self.update_progress("scanning", {"step": "Scanning codebase"})
        
        # codebase from files
        codebase = []
        
        # scan al files and folders in path
        for root, dirs, filenames in os.walk(self.repo_path):
            # only exclude the indicated folders that do not hold handwritten code
            # or may make the project too large to analuyse
            dirs[:] = [d for d in dirs if d not in DIRS_EXCLUDED]
            
            for filename in filenames:
                file_path = Path(root) / filename
                # only processs file with the expeceted extensions
                if file_path.suffix in CODE_EXTENSIONS:
                    try:
                        # open file...
                        with open(file_path, 'r', encoding='utf-8') as f:
                            # read contents
                            content = f.read()
                            # add code text to codebase
                            codebase.append(dict(path=str(file_path.relative_to(self.repo_path)),
                                              content=content,
                                              size=en(content)
                                              )
                                        )
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
        # deliver
        return codebase

    def analyze_with_ai(self, files):
        """Use AI to analyze the codebase"""
        pass

    def create_git_repo(self, analysis):
        """Create new git repository with feature branches"""
        pass

    def create_feature_branches(self, analysis, files):
        """Create feature branches with commits"""
        pass


    def merge_features(self, features_completed):
        """Merge feature branches into master"""
        pass

    def run(self):
        """Execute the full analysis pipeline"""
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