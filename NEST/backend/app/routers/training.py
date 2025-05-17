from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..services.training_service import TrainingService
import logging

router = APIRouter()
training_service = TrainingService()
logger = logging.getLogger(__name__)

class TrainingRequest(BaseModel):
    model_type: str
    epochs: Optional[int] = 10
    batch_size: Optional[int] = 32
    learning_rate: Optional[float] = 0.001

class TrainingResponse(BaseModel):
    status: str
    message: str
    metrics: Optional[Dict[str, float]] = None

class EvaluationRequest(BaseModel):
    model_type: str
    test_data: List[Dict[str, Any]]

class EvaluationResponse(BaseModel):
    status: str
    metrics: Dict[str, float]

def train_model_async(
    model_type: str,
    epochs: int,
    batch_size: int,
    learning_rate: float
):
    """Background task for model training."""
    try:
        # Prepare training data
        training_data = training_service.prepare_training_data(model_type)
        
        # Train model
        if model_type == "emotion":
            metrics = training_service.train_emotion_model(
                training_data,
                epochs=epochs,
                batch_size=batch_size,
                learning_rate=learning_rate
            )
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        logger.info(f"Training completed for {model_type} model")
        return metrics
    except Exception as e:
        logger.error(f"Error in async training: {str(e)}")
        raise

@router.post("/train", response_model=TrainingResponse)
async def train_model(
    request: TrainingRequest,
    background_tasks: BackgroundTasks
):
    """Start model training in the background."""
    try:
        # Validate model type
        if request.model_type not in ["emotion", "chat", "meditation"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported model type: {request.model_type}"
            )

        # Add training task to background tasks
        background_tasks.add_task(
            train_model_async,
            request.model_type,
            request.epochs,
            request.batch_size,
            request.learning_rate
        )

        return TrainingResponse(
            status="success",
            message=f"Training started for {request.model_type} model"
        )
    except Exception as e:
        logger.error(f"Error starting training: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_model(request: EvaluationRequest):
    """Evaluate a trained model."""
    try:
        # Load model
        model = training_service.load_model(request.model_type)
        if model is None:
            raise HTTPException(
                status_code=404,
                detail=f"No trained model found for {request.model_type}"
            )

        # Evaluate model
        metrics = training_service.evaluate_model(model, request.test_data)

        return EvaluationResponse(
            status="success",
            metrics=metrics
        )
    except Exception as e:
        logger.error(f"Error evaluating model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{model_type}")
async def get_training_status(model_type: str):
    """Get the status of a model training process."""
    try:
        # Check if model exists
        model = training_service.load_model(model_type)
        if model is None:
            return {
                "status": "not_trained",
                "message": f"No trained model found for {model_type}"
            }

        return {
            "status": "trained",
            "message": f"Model {model_type} is trained and ready to use"
        }
    except Exception as e:
        logger.error(f"Error getting training status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 