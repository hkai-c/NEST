from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os
from pathlib import Path

router = APIRouter()

class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    context: Optional[Dict[str, Any]] = None
    userId: Optional[str] = None
    sessionId: Optional[str] = None

class PerformanceMetric(BaseModel):
    name: str
    value: float
    timestamp: str
    tags: Optional[Dict[str, str]] = None

class UserAction(BaseModel):
    action: str
    timestamp: str
    context: Optional[Dict[str, Any]] = None

class LogBatch(BaseModel):
    logs: List[LogEntry]

class MetricBatch(BaseModel):
    metrics: List[PerformanceMetric]
    userActions: List[UserAction]

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

def get_log_file_path(date: str) -> Path:
    return LOGS_DIR / f"app-{date}.log"

def get_metric_file_path(date: str) -> Path:
    return LOGS_DIR / f"metrics-{date}.json"

@router.post("/logs")
async def receive_logs(batch: LogBatch):
    try:
        # Get current date for file naming
        current_date = datetime.now().strftime("%Y-%m-%d")
        log_file = get_log_file_path(current_date)

        # Append logs to file
        with open(log_file, "a", encoding="utf-8") as f:
            for log in batch.logs:
                log_entry = {
                    "timestamp": log.timestamp,
                    "level": log.level,
                    "message": log.message,
                    "context": log.context,
                    "userId": log.userId,
                    "sessionId": log.sessionId
                }
                f.write(json.dumps(log_entry) + "\n")

        return {"status": "success", "message": f"Received {len(batch.logs)} logs"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metrics")
async def receive_metrics(batch: MetricBatch):
    try:
        # Get current date for file naming
        current_date = datetime.now().strftime("%Y-%m-%d")
        metric_file = get_metric_file_path(current_date)

        # Read existing metrics if file exists
        existing_metrics = []
        if metric_file.exists():
            with open(metric_file, "r", encoding="utf-8") as f:
                try:
                    existing_metrics = json.load(f)
                except json.JSONDecodeError:
                    existing_metrics = []

        # Append new metrics
        new_metrics = {
            "timestamp": datetime.now().isoformat(),
            "metrics": [metric.dict() for metric in batch.metrics],
            "userActions": [action.dict() for action in batch.userActions]
        }
        existing_metrics.append(new_metrics)

        # Write back to file
        with open(metric_file, "w", encoding="utf-8") as f:
            json.dump(existing_metrics, f, indent=2)

        return {
            "status": "success",
            "message": f"Received {len(batch.metrics)} metrics and {len(batch.userActions)} user actions"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/{date}")
async def get_logs(date: str):
    try:
        log_file = get_log_file_path(date)
        if not log_file.exists():
            return {"logs": []}

        logs = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))

        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/{date}")
async def get_metrics(date: str):
    try:
        metric_file = get_metric_file_path(date)
        if not metric_file.exists():
            return {"metrics": []}

        with open(metric_file, "r", encoding="utf-8") as f:
            metrics = json.load(f)

        return {"metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 