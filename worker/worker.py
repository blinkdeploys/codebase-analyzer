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
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


GH_USER_NAME="Blink Deploys"
GH_EMAIL="blinkdeloys@gmail.com"
APP_NAME="Codebase Analyzer"
CODENASE_LIMIT = 20
DIRS_EXCLUDED = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build'}
CODE_EXTENSIONS = ['.py', '.js', '.ts', '.java', '.go', '.rs', '.cpp', '.c', '.h', '.jsx', '.tsx', '.vue', '.rb', '.php', '.cs', '.swift', '.kt']
SENIOR_DEV_ROLE = "You are a senior software engineer reconstructing a Git history."



def run_openai(prompt, role=SENIOR_DEV_ROLE):
    ai_model = "gpt-5"
    max_tokens = 16000

    # split into lines
    non_empty_lines = [line for line in prompt[:max_tokens].split("\n") if len(trim(line)) > 0]
    prompt_lines = set(non_empty_lines)

    console.log("[cyan]Generating AI commit plan...")
    response = client.chat.completions.create(model=ai_model,
                                              messages=[
                                                        {"role": "system", "content": role},
                                                        {"role": "user", "content": prompt_lines},
                                                        ]
                                              )
    json_str = response.choices[0].message.content

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        console.log("[yellow]Warning: AI returned invalid JSON, saving raw output.")
        with open("ai_commit_plan_raw.txt", "w") as f:
            f.write(json_str)
        raise
    return json_str


def run_anthropic(prompt):
    ai_model = "claude-sonnet-4-20250514"
    max_tokens = 4000

    message = anthropic.messages.create(model=ai_model,
                                        max_tokens=max_tokens,
                                        messages=[dict(role="user",
                                                       content=prompt)]
                                        )
    response_text = message.content[0].text

    json_str = ""
    if "```json" in response_text:
        json_str = response_text.split("```json")[1].split("```")[0]
    else:
        json_str = response_text

    # parse the json response
    try
        return json.loads(json_str) 
    except json.JSONDecodeError:
        console.log("[yellow]Warning: AI returned invalid JSON, saving raw output.")
        with open("ai_commit_plan_raw.txt", "w") as f:
            f.write(json_str)
        raise
    return json_str



class CodebaseAnalyzer:
    def __init__(self, job_id, repo_path, output_name, ai_service="openai"):
        # queued job id
        self.job_id = job_id
        # codebase repo path
        self.repo_path = Path(repo_path)
        # output codebase path
        self.output_path = Path("/app/output") / output_name
        # work directory
        self.workdir = Path("/app/workdir") / job_id
        # ai service to use for this instance
        self.ai_service = ai_service


    def update_progress(self, status, progress_data):
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


    def analyze_with_ai(self, codebase):
        """Use AI to analyze the codebase"""
        self.update_progress("analyzing", {"step": "Analyzing with AI", "files": len(files)})


        # prepare codebase summary for codebase context
        # TODO: to find a better way to track AI credits
        # and cover essential files while maintaining small context sizes
        codebase_summary = "\n".join([f"File: {f['path']}\nSize: {f['size']} bytes\n---CONTENT---\n{f['content'][:500]}...\n"
                                  for f in codebase[:CODENASE_LIMIT]  # Limit to first 20 files for context
                                  ])

        # build the prompt
        system_message = SENIOR_DEV_ROLE
        prompt = f"""Analyze this codebase and provide a comprehensive breakdown.

Files in codebase:
{codebase_summary}

Please provide:
1. Project description and purpose
2. Main features (list them)
3. Technology stack
4. Logical feature breakdown (how to split into git branches)
5. Dependencies between features
6. Recommended commit structure for each feature

Format your response as JSON with this structure:
{{
  "description": "project description",
  "features": [
    {{
      "name": "feature-name",
      "description": "what it does",
      "files": ["file1.py", "file2.js"],
      "dependencies": ["other-feature-name"],
      "commits": [
        {{
          "message": "commit message",
          "files": ["files changed"],
          "changes": "description of changes"
        }}
      ]
    }}
  ],
  "tech_stack": ["python", "react", etc]
}}"""

        response = dict()
        if self.ai_service == "anthropic"
            response = run_anthropic(prompt)
        else:
            response = run_openai(prompt, role)
        return response


    def get_ai_commit_plan(summary):
        console.log("[cyan]Generating AI commit plan...")
        role = SENIOR_DEV_ROLE
        prompt = """Given this project file summary, divide it into a sequence of logical commits.

For each commit, provide a JSON list with keys: commit (string message) and files (list of paths).

Here is the summary:\n{json.dumps(summary)[:16000]}
"""
        response = dict()
        if self.ai_service == "anthropic"
            response = run_anthropic(prompt)
        else:
            response = run_openai(prompt, role)
        return response


    def create_git_repo(self, analysis):
        """Create new git repository with feature branches"""
        self.update_progress("creating", {"step": "Creating Git repository"})

        # create output directory
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=self.output_path, check=True)
        subprocess.run(["git", "config", "user.name", GH_USER_NAME], cwd=self.output_path)
        subprocess.run(["git", "config", "user.email", GH_EMAIL], cwd=self.output_path)

        # Create initial commit on master
        readme_content = f"""# {analysis.get('description', 'Reconstructed Project')}

## Features
{chr(10).join(['- ' + f['name'] + ': ' + f['description'] for f in analysis['features']])}

## Technology Stack
{', '.join(analysis.get('tech_stack', []))}

## Branch Structure
This repository has been reconstructed with logical feature branches:
{chr(10).join(['- `' + f['name'] + '`' for f in analysis['features']])}

Generated by {APP_NAME}
"""
        
        with open(self.output_path / "README.md", "w") as f:
            f.write(readme_content)
        
        subprocess.run(["git", "add", "README.md"], cwd=self.output_path, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit: Project structure"], cwd=self.output_path, check=True)
        
        return analysis
    


    def create_feature_branches(self, analysis, files):
        """Create feature branches with commits"""
        features_completed = []

        for idx, feature in enumerate(analysis['features']):
            # update job status
            job_status = "branching"
            job_progress = dict(step=f"Creating feature branch {idx+1}/{len(analysis['features'])}",
                                feature=feature['name']
                                )
            self.update_progress(job_status, job_progress)

            # get the branch name
            branch_name = feature['name'].lower().replace(' ', '-')

            # create branch from master
            subprocess.run(["git", "checkout", "-b", branch_name], cwd=self.output_path, check=True)
            
            # create commits for this feature
            for commit_idx, commit_info in enumerate(feature.get('commits', [])):
                # find and copy relevant files
                for file_pattern in commit_info.get('files', []):
                    matching_files = [f for f in files if file_pattern in f['path']]
                    
                    for file_data in matching_files:
                        file_path = self.output_path / file_data['path']
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        # save to code in the new repo
                        with open(file_path, 'w') as f:
                            f.write(file_data['content'])
                
                # Stage and commit changes
                subprocess.run(["git", "add", "."], cwd=self.output_path, check=True)
                
                commit_message = f"{feature['name']}: {commit_info['message']}"
                try:
                    subprocess.run(["git", "commit", "-m", commit_message],
                                   cwd=self.output_path,
                                   check=True,
                                   capture_output=True
                                   )
                except subprocess.CalledProcessError:
                    # No changes to commit
                    pass
            # add to features completed
            features_completed.append(dict(branch=branch_name,
                                           feature=feature['name'],
                                           commits=len(feature.get('commits', []))
                                           )
                                     )
        return features_completed


    def merge_features(self, features_completed):
        """Merge feature branches into master"""
        self.update_progress("merging", {"step": "Merging features into master"})

        for feature_info in features_completed:
            try:
                # enqueue the job to merge feature branches to master
                subprocess.run(["git", "merge", "--no-ff", feature_info['branch'], "-m", 
                               f"Merge feature: {feature_info['feature']}"],
                               cwd=self.output_path,
                               check=True
                               )
            except subprocess.CalledProcessError as e:
                print(f"Error merging {feature_info['branch']}: {e}")
            

    def run(self):
        """Execute the full analysis pipeline"""
        try:
            # scan the codebase
            # run the analysis on the collected codebase
            # create fresh git repo
            # create all feature branches
            # merge the features
            # enqueue jobs

        except Exception as e:
            # update the job status as failed
            job_data = dict(job_id=self.job_id,
                            status="failed",
                            error=str(e)
                            )
            redis_client.set(f"job:{self.job_id}", json.dumps(job_data))
            raise        



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