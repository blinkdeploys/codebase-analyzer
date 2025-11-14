from pydantic import BaseModel
from typing import Optional


class AnalysisRequest(BaseModel):
    repo_path: str
    output_name: str
    description: Optional[str] = None


class AnalysisStatus(BaseModel):
    job_id: str
    status: str
    progress: Optional[dict] = None
    result: Optional[dict] = None
    error: Optional[str] = None
