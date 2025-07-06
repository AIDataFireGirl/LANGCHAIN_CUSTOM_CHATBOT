"""
Configuration module for the LangChain Custom Chatbot with Memory.
Handles environment variables, security settings, and validation.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseSettings, validator

# Load environment variables from .env file
load_dotenv()

class SecurityConfig:
    """Security configuration and validation settings."""
    
    # Maximum input length to prevent abuse
    MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", "1000"))
    
    # Allowed file types for document uploads
    ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", "txt,pdf,doc,docx").split(",")
    
    # Maximum file size in MB
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    
    @staticmethod
    def validate_input_length(text: str) -> bool:
        """Validate input length for security."""
        return len(text) <= SecurityConfig.MAX_INPUT_LENGTH
    
    @staticmethod
    def validate_file_type(filename: str) -> bool:
        """Validate file type for security."""
        file_extension = filename.split('.')[-1].lower()
        return file_extension in SecurityConfig.ALLOWED_FILE_TYPES
    
    @staticmethod
    def validate_file_size(file_size_bytes: int) -> bool:
        """Validate file size for security."""
        max_size_bytes = SecurityConfig.MAX_FILE_SIZE_MB * 1024 * 1024
        return file_size_bytes <= max_size_bytes

class ChatbotConfig(BaseSettings):
    """Configuration for the chatbot settings."""
    
    # OpenAI API Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Chatbot Identity
    chatbot_name: str = os.getenv("CHATBOT_NAME", "MemoryBot")
    chatbot_personality: str = os.getenv(
        "CHATBOT_PERSONALITY", 
        "You are a helpful AI assistant with memory capabilities. You remember conversations and provide contextual responses."
    )
    
    # Memory Configuration
    memory_max_tokens: int = int(os.getenv("MEMORY_MAX_TOKENS", "2000"))
    memory_return_messages: bool = os.getenv("MEMORY_RETURN_MESSAGES", "True").lower() == "true"
    
    # Model Configuration
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000
    
    @validator("openai_api_key")
    def validate_api_key(cls, v):
        """Validate that OpenAI API key is provided."""
        if not v:
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY environment variable.")
        return v
    
    @validator("memory_max_tokens")
    def validate_memory_tokens(cls, v):
        """Validate memory token limit."""
        if v < 100 or v > 10000:
            raise ValueError("Memory max tokens must be between 100 and 10000")
        return v

# Global configuration instance
config = ChatbotConfig()
security_config = SecurityConfig() 