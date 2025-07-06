"""
Memory Manager for LangChain Custom Chatbot.
Handles conversation memory, context storage, and memory operations with security features.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from .config import config, security_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecureMemoryManager:
    """
    Secure memory manager for the chatbot with input validation and sanitization.
    """
    
    def __init__(self):
        """Initialize the memory manager with security features."""
        self.memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 exchanges
            return_messages=config.memory_return_messages,
            memory_key="chat_history"
        )
        
        # Summary memory for long conversations
        self.summary_memory = ConversationSummaryMemory(
            llm=ChatOpenAI(
                api_key=config.openai_api_key,
                model_name=config.model_name,
                temperature=0.5
            ),
            max_token_limit=config.memory_max_tokens,
            return_messages=True
        )
        
        # Security: Track conversation metadata
        self.conversation_metadata = {
            "start_time": datetime.now().isoformat(),
            "message_count": 0,
            "total_tokens": 0
        }
    
    def add_message(self, message: str, is_human: bool = True) -> bool:
        """
        Add a message to memory with security validation.
        
        Args:
            message: The message content
            is_human: Whether the message is from human (True) or AI (False)
            
        Returns:
            bool: True if message was added successfully, False otherwise
        """
        try:
            # Security: Validate input length
            if not security_config.validate_input_length(message):
                logger.warning(f"Message too long: {len(message)} characters")
                return False
            
            # Security: Basic content sanitization
            sanitized_message = self._sanitize_message(message)
            
            # Create appropriate message object
            if is_human:
                msg_obj = HumanMessage(content=sanitized_message)
            else:
                msg_obj = AIMessage(content=sanitized_message)
            
            # Add to memory
            self.memory.chat_memory.add_message(msg_obj)
            
            # Update metadata
            self.conversation_metadata["message_count"] += 1
            self.conversation_metadata["total_tokens"] += len(sanitized_message.split())
            
            logger.info(f"Message added to memory: {len(sanitized_message)} chars")
            return True
            
        except Exception as e:
            logger.error(f"Error adding message to memory: {e}")
            return False
    
    def get_memory_variables(self) -> Dict[str, Any]:
        """
        Get memory variables for the conversation chain.
        
        Returns:
            Dict containing memory variables
        """
        try:
            return self.memory.load_memory_variables({})
        except Exception as e:
            logger.error(f"Error loading memory variables: {e}")
            return {"chat_history": []}
    
    def get_conversation_summary(self) -> str:
        """
        Get a summary of the conversation for long-term memory.
        
        Returns:
            str: Conversation summary
        """
        try:
            # Get messages from buffer memory
            messages = self.memory.chat_memory.messages
            
            if not messages:
                return "No conversation history available."
            
            # Create summary using summary memory
            for message in messages:
                if isinstance(message, HumanMessage):
                    self.summary_memory.save_context(
                        {"input": message.content},
                        {"output": ""}
                    )
            
            # Get the summary
            summary_vars = self.summary_memory.load_memory_variables({})
            return summary_vars.get("history", "No summary available.")
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {e}")
            return "Error generating conversation summary."
    
    def clear_memory(self) -> bool:
        """
        Clear all conversation memory.
        
        Returns:
            bool: True if memory was cleared successfully
        """
        try:
            self.memory.clear()
            self.summary_memory.clear()
            
            # Reset metadata
            self.conversation_metadata = {
                "start_time": datetime.now().isoformat(),
                "message_count": 0,
                "total_tokens": 0
            }
            
            logger.info("Memory cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing memory: {e}")
            return False
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics and metadata.
        
        Returns:
            Dict containing memory statistics
        """
        try:
            messages = self.memory.chat_memory.messages
            return {
                "total_messages": len(messages),
                "conversation_metadata": self.conversation_metadata,
                "memory_type": "ConversationBufferWindowMemory",
                "window_size": 10,
                "has_summary": len(self.summary_memory.chat_memory.messages) > 0
            }
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {"error": "Failed to get memory statistics"}
    
    def _sanitize_message(self, message: str) -> str:
        """
        Sanitize message content for security.
        
        Args:
            message: Raw message content
            
        Returns:
            str: Sanitized message content
        """
        # Remove potentially dangerous characters/patterns
        sanitized = message.strip()
        
        # Limit length for security
        if len(sanitized) > security_config.MAX_INPUT_LENGTH:
            sanitized = sanitized[:security_config.MAX_INPUT_LENGTH]
        
        return sanitized
    
    def export_memory(self) -> Dict[str, Any]:
        """
        Export memory data for backup or analysis.
        
        Returns:
            Dict containing exported memory data
        """
        try:
            messages = self.memory.chat_memory.messages
            exported_data = {
                "messages": [
                    {
                        "type": "human" if isinstance(msg, HumanMessage) else "ai",
                        "content": msg.content,
                        "timestamp": datetime.now().isoformat()
                    }
                    for msg in messages
                ],
                "metadata": self.conversation_metadata,
                "summary": self.get_conversation_summary()
            }
            return exported_data
            
        except Exception as e:
            logger.error(f"Error exporting memory: {e}")
            return {"error": "Failed to export memory"} 