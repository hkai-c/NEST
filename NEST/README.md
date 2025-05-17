# NEST - Mental Health Support Platform

A comprehensive mental health support platform providing anonymous counseling, AI-powered emotional support, and guided healing features.

## Features

- Anonymous Self-Expression: Anonymous text and voice-based emotional expression
- Real-time Emotion Analysis: Multi-dimensional emotion classification using Transformer models
- AI Companion: Empathetic AI chatbot with cognitive restructuring suggestions
- Guided Healing: Integrated meditation, breathing exercises, and mindfulness journaling
- Emotion Tracking: Periodic emotional trend analysis and mental health reports

## Technical Stack

### Frontend
- React Native + TypeScript
- Cross-platform mobile development

### Backend
- FastAPI + Python
- AI inference and business logic

### AI/ML
- LLaVA/LLaMA based open-source models
- Fine-tuned with safety filters

### Data Storage
- PostgreSQL: User metadata
- MongoDB: Conversation logs

### Infrastructure
- Kubernetes + Docker
- RabbitMQ for async task scheduling

## Security & Privacy

- HIPAA & GDPR compliant
- AES-256 encryption for data at rest
- TLS 1.3 with PFS for data in transit
- Minimal data collection
- Regular security audits

## Setup Instructions

1. Clone the repository
2. Install dependencies:
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt

   # Frontend
   cd frontend
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```

4. Start the development servers:
   ```bash
   # Backend
   cd backend
   uvicorn main:app --reload

   # Frontend
   cd frontend
   npm start
   ```

## Project Structure

```
nest/
├── backend/           # FastAPI backend
├── frontend/         # React Native frontend
├── ml_models/        # AI model implementations
├── infrastructure/   # Kubernetes & Docker configs
└── docs/            # Documentation
```

## License

MIT License 