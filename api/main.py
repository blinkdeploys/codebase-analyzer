from fastapi import FastAPI, BackgroundTasks, HTTPException, Header
import redis
import json
import uuid
import os
import hmac
import hashlib
from typing import Optional, Dict
from .models import AnalysisRequest, AnalysisStatus
from .utils import verify_webhook_signature



# initalise app
app = FastAPI(title="Codebase Analyzer API")

# Redis connection
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))


def initalise_job(request: AnalysisRequest,
                  job_id: str) -> Dict:
    job_data = dict(job_id=job_id,
                    repo_path=request.repo_path,
                    output_name=request.output_name,
                    description=request.description,
                    status="queued",
                    progress=dict()
                    )
    return job_data



@app.get("/")
async def root():
    """Information endpoint"""
    return dict(service="Codebase Analyzer API",
                version="1.0.0",
                endpoints=dict(analyze="POST /analyze",
                            status="GET /status/{job_id}",
                            webhook="POST /webhook"
                            )
                )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        redis_client.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.post("/analyze")
async def analyze_codebase(request: AnalysisRequest,
                           background_tasks: BackgroundTasks
                           ):
    """Submit a codebase for analysis"""
    
    # validate the repo path
    if not os.path.exists(request.repo_path):
        raise HTTPException(status_code=400, detail="Repository path does not exist")
    
    # generate the job id
    job_id = str(uuid.uuid4())

    # create job data
    job_id = str(uuid.uuid4())
    job_data = initalise_job(request, job_id)

    # store job in redis
    redis_client.set(f"job:{job_id}", json.dumps(job_data))
    redis_client.lpush("job_queue", job_id)

    # package
    response = dict(job_id=job_id,
                    status="queued",
                    message="Analysis job submitted successfully"
                    )
    # deliver
    return response




@app.get("/status/{job_id}")
async def get_status(job_id: str):
    """Get the status of an analysis job"""
    # fetch job data
    job_data = redis_client.get(f"job:{job_id}")

    # return 404 if data does not exist
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")

    # return data if it does
    data = json.loads(job_data)
    return AnalysisStatus(**data)


@app.post("/webhook")
async def webhook_handler(request: AnalysisRequest,
                          x_webhook_signature: Optional[str] = Header(None)
                          ):
    """Webhook endpoint for external integrations"""

    # autth: check the if signature is provided with webhook
    if x_webhook_signature:
        payload = json.dumps(request.dict()).encode()
        if not verify_webhook_signature(payload, x_webhook_signature):
            # raise exception if signature invalid
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # create job data
    job_id = str(uuid.uuid4())
    job_data = initalise_job(request, job_id)

    # persist to redis
    redis_client.set(f"job:{job_id}", json.dumps(job_data))
    redis_client.lpush("job_queue", job_id)

    # package and deliver
    response = dict(job_id=job_id,
                    status="queued",
                    message="Analysis job submitted successfully"
                    webhook_received=True
                    )
    return response


