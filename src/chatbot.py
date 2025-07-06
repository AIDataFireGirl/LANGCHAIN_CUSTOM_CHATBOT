"""
Main Chatbot Class for LangChain Custom Chatbot with Memory.
Integrates LangChain components with memory management and security features.
"""

import logging
from typing import Dict, Any, Optional, List
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from .config import config, security_config
from .memory_manager import SecureMemoryManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomChatbot:
    """
    Custom chatbot with memory capabilities using LangChain.
    Includes security features, input validation, and conversation management.
    """
    
    def __init__(self):
        """Initialize the chatbot with memory and security features."""
        try:
            # Initialize memory manager
            self.memory_manager = SecureMemoryManager()
            
            # Initialize OpenAI chat model
            self.llm = ChatOpenAI(
                api_key=config.openai_api_key,
                model_name=config.model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
            
            # Create conversation chain with memory
            self.conversation_chain = ConversationChain(
                llm=self.llm,
                memory=self.memory_manager.memory,
                verbose=False
            )
            
            # Custom prompt template for better control
            self.prompt_template = PromptTemplate(
                input_variables=["history", "input"],
                template=f"""You are {config.chatbot_name}, {config.chatbot_personality}

Current conversation:
{{history}}
Human: {{input}}
{config.chatbot_name}:"""
            )
            
            logger.info("Chatbot initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing chatbot: {e}")
            raise
    
    def chat(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input and generate response with security validation.
        
        Args:
            user_input: The user's message
            
        Returns:
            Dict containing response and metadata
        """
        try:
            # Security: Validate input
            if not self._validate_input(user_input):
                return {
                    "response": "I'm sorry, but your input doesn't meet our security requirements. Please try a shorter message.",
                    "success": False,
                    "error": "Input validation failed"
                }
            
            # Add user message to memory
            if not self.memory_manager.add_message(user_input, is_human=True):
                return {
                    "response": "I'm sorry, but I couldn't process your message. Please try again.",
                    "success": False,
                    "error": "Failed to add message to memory"
                }
            
            # Generate response using conversation chain
            response = self.conversation_chain.predict(input=user_input)
            
            # Add AI response to memory
            self.memory_manager.add_message(response, is_human=False)
            
            # Get memory statistics
            memory_stats = self.memory_manager.get_memory_stats()
            
            return {
                "response": response,
                "success": True,
                "memory_stats": memory_stats,
                "conversation_summary": self.memory_manager.get_conversation_summary()
            }
            
        except Exception as e:
            logger.error(f"Error in chat method: {e}")
            return {
                "response": "I'm sorry, but I encountered an error. Please try again.",
                "success": False,
                "error": str(e)
            }
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history.
        
        Returns:
            List of conversation messages
        """
        try:
            messages = self.memory_manager.memory.chat_memory.messages
            history = []
            
            for i in range(0, len(messages), 2):
                if i + 1 < len(messages):
                    history.append({
                        "human": messages[i].content,
                        "ai": messages[i + 1].content
                    })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def clear_conversation(self) -> bool:
        """
        Clear the conversation memory.
        
        Returns:
            bool: True if cleared successfully
        """
        try:
            return self.memory_manager.clear_memory()
        except Exception as e:
            logger.error(f"Error clearing conversation: {e}")
            return False
    
    def get_memory_info(self) -> Dict[str, Any]:
        """
        Get detailed memory information and statistics.
        
        Returns:
            Dict containing memory information
        """
        try:
            stats = self.memory_manager.get_memory_stats()
            summary = self.memory_manager.get_conversation_summary()
            
            return {
                "memory_stats": stats,
                "conversation_summary": summary,
                "total_messages": len(self.memory_manager.memory.chat_memory.messages),
                "memory_type": "ConversationBufferWindowMemory with Summary"
            }
            
        except Exception as e:
            logger.error(f"Error getting memory info: {e}")
            return {"error": "Failed to get memory information"}
    
    def export_conversation(self) -> Dict[str, Any]:
        """
        Export the current conversation for backup or analysis.
        
        Returns:
            Dict containing exported conversation data
        """
        try:
            return self.memory_manager.export_memory()
        except Exception as e:
            logger.error(f"Error exporting conversation: {e}")
            return {"error": "Failed to export conversation"}
    
    def _validate_input(self, user_input: str) -> bool:
        """
        Validate user input for security and safety.
        
        Args:
            user_input: The user's input message
            
        Returns:
            bool: True if input is valid, False otherwise
        """
        try:
            # Check input length
            if not security_config.validate_input_length(user_input):
                logger.warning(f"Input too long: {len(user_input)} characters")
                return False
            
            # Check for empty or whitespace-only input
            if not user_input.strip():
                logger.warning("Empty input received")
                return False
            
            # Basic content validation (can be extended)
            dangerous_patterns = [
                "script", "javascript:", "data:", "vbscript:",
                "<script", "</script>", "onload=", "onerror="
            ]
            
            input_lower = user_input.lower()
            for pattern in dangerous_patterns:
                if pattern in input_lower:
                    logger.warning(f"Dangerous pattern detected: {pattern}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating input: {e}")
            return False
    
    def get_bot_info(self) -> Dict[str, str]:
        """
        Get information about the chatbot.
        
        Returns:
            Dict containing bot information
        """
        return {
            "name": config.chatbot_name,
            "personality": config.chatbot_personality,
            "model": config.model_name,
            "memory_type": "ConversationBufferWindowMemory with Summary",
            "security_features": [
                "Input length validation",
                "Content sanitization",
                "Dangerous pattern detection",
                "Memory size limits"
            ]
        } 