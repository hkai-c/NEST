from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import json

load_dotenv()

class ChatBot:
    def __init__(self):
        self.model_name = os.getenv("CHAT_MODEL", "meta-llama/Llama-2-7b-chat-hf")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto"
        )
        
        # Load safety filters
        self.safety_filters = self._load_safety_filters()
        
        # System prompt for the chat model
        self.system_prompt = """You are an empathetic AI mental health companion. Your role is to:
1. Listen actively and show understanding
2. Provide gentle guidance and support
3. Help users reframe negative thoughts
4. Suggest appropriate coping strategies
5. Maintain professional boundaries
6. Never give medical advice
7. Always prioritize user safety

Remember to be compassionate, non-judgmental, and supportive."""

    def _load_safety_filters(self) -> Dict:
        """Load safety filters for content moderation"""
        # TODO: Implement proper safety filters
        return {
            "harmful_content": True,
            "medical_advice": True,
            "personal_information": True
        }

    def _apply_safety_filters(self, text: str) -> bool:
        """
        Apply safety filters to the text.
        Returns True if the text passes all filters.
        """
        # TODO: Implement proper content filtering
        return True

    def generate_response(
        self,
        user_input: str,
        conversation_history: Optional[List[Dict]] = None,
        emotion_context: Optional[Dict] = None
    ) -> Dict:
        """
        Generate a response based on user input and context.
        
        Args:
            user_input (str): The user's message
            conversation_history (Optional[List[Dict]]): Previous conversation messages
            emotion_context (Optional[Dict]): Current emotional context
            
        Returns:
            Dict containing:
                - response: The generated response
                - safety_check: Whether the response passed safety filters
                - suggested_actions: List of suggested actions or resources
        """
        # Check input safety
        if not self._apply_safety_filters(user_input):
            return {
                "response": "I apologize, but I cannot process that input as it may violate our safety guidelines.",
                "safety_check": False,
                "suggested_actions": []
            }
        
        # Prepare conversation context
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        if emotion_context:
            emotion_prompt = f"Current emotional context: {json.dumps(emotion_context)}"
            messages.append({"role": "system", "content": emotion_prompt})
        
        messages.append({"role": "user", "content": user_input})
        
        # Generate response
        inputs = self.tokenizer.apply_chat_template(
            messages,
            return_tensors="pt"
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract the model's response from the full conversation
        response = response.split("assistant")[-1].strip()
        
        # Check response safety
        safety_check = self._apply_safety_filters(response)
        
        # Generate suggested actions based on the conversation
        suggested_actions = self._generate_suggested_actions(
            user_input,
            response,
            emotion_context
        )
        
        return {
            "response": response,
            "safety_check": safety_check,
            "suggested_actions": suggested_actions
        }

    def _generate_suggested_actions(
        self,
        user_input: str,
        response: str,
        emotion_context: Optional[Dict]
    ) -> List[str]:
        """
        Generate suggested actions or resources based on the conversation.
        """
        # TODO: Implement proper action suggestion logic
        return [
            "Try a guided meditation",
            "Practice deep breathing",
            "Write in your journal"
        ]

    def get_conversation_summary(self, conversation_history: List[Dict]) -> Dict:
        """
        Generate a summary of the conversation.
        
        Args:
            conversation_history (List[Dict]): List of conversation messages
            
        Returns:
            Dict containing conversation summary and key points
        """
        # TODO: Implement conversation summarization
        return {
            "summary": "Conversation summary placeholder",
            "key_points": ["Key point 1", "Key point 2"],
            "suggested_follow_up": "Follow-up suggestion"
        } 