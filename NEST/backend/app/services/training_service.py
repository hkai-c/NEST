from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from datetime import datetime
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionDataset(Dataset):
    def __init__(self, texts: List[str], labels: List[int]):
        self.texts = texts
        self.labels = labels

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        return self.texts[idx], self.labels[idx]

class EmotionClassifier(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, num_classes: int):
        super(EmotionClassifier, self).__init__()
        self.layer1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(hidden_size, num_classes)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        x = self.layer1(x)
        x = self.relu(x)
        x = self.layer2(x)
        x = self.softmax(x)
        return x

class TrainingService:
    def __init__(self):
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.emotion_model = None
        self.chat_model = None
        self.meditation_model = None

    def prepare_emotion_data(self, data: List[Dict[str, Any]]) -> tuple:
        """Prepare emotion data for training."""
        texts = [item["text"] for item in data]
        labels = [item["emotion"] for item in data]
        
        # Convert text to features (implement your text preprocessing here)
        features = self._text_to_features(texts)
        
        return features, labels

    def _text_to_features(self, texts: List[str]) -> np.ndarray:
        """Convert text to numerical features."""
        # Implement your text feature extraction here
        # This is a placeholder implementation
        return np.random.rand(len(texts), 100)  # 100-dimensional features

    def train_emotion_model(
        self,
        data: List[Dict[str, Any]],
        epochs: int = 10,
        batch_size: int = 32,
        learning_rate: float = 0.001
    ) -> Dict[str, float]:
        """Train the emotion classification model."""
        try:
            # Prepare data
            features, labels = self.prepare_emotion_data(data)
            X_train, X_val, y_train, y_val = train_test_split(
                features, labels, test_size=0.2, random_state=42
            )

            # Create datasets and dataloaders
            train_dataset = EmotionDataset(X_train, y_train)
            val_dataset = EmotionDataset(X_val, y_val)
            train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
            val_loader = DataLoader(val_dataset, batch_size=batch_size)

            # Initialize model
            input_size = features.shape[1]
            hidden_size = 128
            num_classes = len(set(labels))
            self.emotion_model = EmotionClassifier(input_size, hidden_size, num_classes)
            self.emotion_model.to(self.device)

            # Training setup
            criterion = nn.CrossEntropyLoss()
            optimizer = torch.optim.Adam(self.emotion_model.parameters(), lr=learning_rate)

            # Training loop
            best_val_accuracy = 0
            for epoch in range(epochs):
                self.emotion_model.train()
                train_loss = 0
                for batch_texts, batch_labels in train_loader:
                    batch_texts = batch_texts.to(self.device)
                    batch_labels = batch_labels.to(self.device)

                    optimizer.zero_grad()
                    outputs = self.emotion_model(batch_texts)
                    loss = criterion(outputs, batch_labels)
                    loss.backward()
                    optimizer.step()
                    train_loss += loss.item()

                # Validation
                self.emotion_model.eval()
                val_predictions = []
                val_true = []
                with torch.no_grad():
                    for batch_texts, batch_labels in val_loader:
                        batch_texts = batch_texts.to(self.device)
                        outputs = self.emotion_model(batch_texts)
                        _, predicted = torch.max(outputs.data, 1)
                        val_predictions.extend(predicted.cpu().numpy())
                        val_true.extend(batch_labels.numpy())

                val_accuracy = accuracy_score(val_true, val_predictions)
                precision, recall, f1, _ = precision_recall_fscore_support(
                    val_true, val_predictions, average='weighted'
                )

                logger.info(
                    f"Epoch {epoch+1}/{epochs} - "
                    f"Train Loss: {train_loss/len(train_loader):.4f} - "
                    f"Val Accuracy: {val_accuracy:.4f} - "
                    f"F1 Score: {f1:.4f}"
                )

                # Save best model
                if val_accuracy > best_val_accuracy:
                    best_val_accuracy = val_accuracy
                    self.save_model("emotion_model", self.emotion_model)

            return {
                "accuracy": val_accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1
            }

        except Exception as e:
            logger.error(f"Error training emotion model: {str(e)}")
            raise

    def save_model(self, model_name: str, model: nn.Module):
        """Save a trained model."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = self.models_dir / f"{model_name}_{timestamp}.pt"
        torch.save(model.state_dict(), model_path)
        logger.info(f"Model saved to {model_path}")

    def load_model(self, model_name: str) -> Optional[nn.Module]:
        """Load a trained model."""
        try:
            # Get the latest model file
            model_files = list(self.models_dir.glob(f"{model_name}_*.pt"))
            if not model_files:
                return None

            latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
            
            # Initialize model with appropriate architecture
            if model_name == "emotion_model":
                model = EmotionClassifier(input_size=100, hidden_size=128, num_classes=7)
            else:
                raise ValueError(f"Unknown model type: {model_name}")

            model.load_state_dict(torch.load(latest_model))
            model.to(self.device)
            model.eval()
            
            logger.info(f"Loaded model from {latest_model}")
            return model

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return None

    def evaluate_model(
        self,
        model: nn.Module,
        test_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Evaluate a trained model on test data."""
        try:
            features, labels = self.prepare_emotion_data(test_data)
            test_dataset = EmotionDataset(features, labels)
            test_loader = DataLoader(test_dataset, batch_size=32)

            model.eval()
            predictions = []
            true_labels = []

            with torch.no_grad():
                for batch_texts, batch_labels in test_loader:
                    batch_texts = batch_texts.to(self.device)
                    outputs = model(batch_texts)
                    _, predicted = torch.max(outputs.data, 1)
                    predictions.extend(predicted.cpu().numpy())
                    true_labels.extend(batch_labels.numpy())

            accuracy = accuracy_score(true_labels, predictions)
            precision, recall, f1, _ = precision_recall_fscore_support(
                true_labels, predictions, average='weighted'
            )

            return {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1
            }

        except Exception as e:
            logger.error(f"Error evaluating model: {str(e)}")
            raise

    def prepare_training_data(self, data_type: str) -> List[Dict[str, Any]]:
        """Prepare training data from various sources."""
        try:
            if data_type == "emotion":
                # Load emotion data from your database or files
                # This is a placeholder implementation
                return [
                    {"text": "I'm feeling happy today", "emotion": 0},
                    {"text": "I'm feeling sad", "emotion": 1},
                    # Add more training examples
                ]
            elif data_type == "chat":
                # Load chat data
                return []
            elif data_type == "meditation":
                # Load meditation data
                return []
            else:
                raise ValueError(f"Unknown data type: {data_type}")

        except Exception as e:
            logger.error(f"Error preparing training data: {str(e)}")
            raise 