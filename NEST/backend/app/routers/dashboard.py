from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Dict, Any, List
import json
from pathlib import Path
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# Set up templates and static files
templates = Jinja2Templates(directory="templates")
router.mount("/static", StaticFiles(directory="static"), name="static")

# Store training metrics in memory (in production, use a database)
training_metrics: Dict[str, List[Dict[str, Any]]] = {
    "emotion": [],
    "chat": [],
    "meditation": []
}

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render the training dashboard."""
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "models": ["emotion", "chat", "meditation"]
        }
    )

@router.get("/metrics/{model_type}")
async def get_metrics(model_type: str):
    """Get training metrics for a specific model."""
    if model_type not in training_metrics:
        raise HTTPException(status_code=404, detail="Model type not found")
    return training_metrics[model_type]

@router.post("/metrics/{model_type}")
async def update_metrics(model_type: str, metrics: Dict[str, Any]):
    """Update training metrics for a specific model."""
    if model_type not in training_metrics:
        raise HTTPException(status_code=404, detail="Model type not found")
    
    # Add timestamp to metrics
    metrics["timestamp"] = datetime.now().isoformat()
    training_metrics[model_type].append(metrics)
    
    # Keep only last 100 metrics
    training_metrics[model_type] = training_metrics[model_type][-100:]
    
    return {"status": "success"}

@router.get("/status/{model_type}")
async def get_training_status(model_type: str):
    """Get current training status for a model."""
    if model_type not in training_metrics:
        raise HTTPException(status_code=404, detail="Model type not found")
    
    if not training_metrics[model_type]:
        return {
            "status": "not_started",
            "message": "Training has not started"
        }
    
    latest_metrics = training_metrics[model_type][-1]
    return {
        "status": "in_progress" if latest_metrics.get("is_training", False) else "completed",
        "metrics": latest_metrics
    } 