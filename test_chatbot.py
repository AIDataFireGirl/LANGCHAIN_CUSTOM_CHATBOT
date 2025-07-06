"""
Test script for the LangChain Custom Chatbot with Memory.
Demonstrates functionality and validates features.
"""

import json
import logging
from datetime import datetime
from src.chatbot import CustomChatbot
from src.config import config, security_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_chatbot_initialization():
    """Test chatbot initialization."""
    print("🧪 Testing Chatbot Initialization...")
    try:
        chatbot = CustomChatbot()
        print("✅ Chatbot initialized successfully")
        return chatbot
    except Exception as e:
        print(f"❌ Chatbot initialization failed: {e}")
        return None

def test_basic_chat(chatbot):
    """Test basic chat functionality."""
    print("\n🧪 Testing Basic Chat Functionality...")
    
    test_messages = [
        "Hello, how are you?",
        "What's your name?",
        "Can you remember our conversation?",
        "What did I just ask you?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Test Message {i} ---")
        print(f"User: {message}")
        
        response = chatbot.chat(message)
        
        if response['success']:
            print(f"Bot: {response['response']}")
            print(f"Memory Stats: {response.get('memory_stats', {})}")
        else:
            print(f"❌ Error: {response.get('error', 'Unknown error')}")

def test_memory_features(chatbot):
    """Test memory-related features."""
    print("\n🧪 Testing Memory Features...")
    
    # Test conversation history
    history = chatbot.get_conversation_history()
    print(f"✅ Conversation History: {len(history)} exchanges")
    
    # Test memory info
    memory_info = chatbot.get_memory_info()
    print(f"✅ Memory Info: {memory_info.get('total_messages', 0)} total messages")
    
    # Test conversation summary
    if 'conversation_summary' in memory_info:
        print(f"✅ Conversation Summary: {memory_info['conversation_summary'][:100]}...")

def test_security_features(chatbot):
    """Test security features."""
    print("\n🧪 Testing Security Features...")
    
    # Test input length validation
    long_message = "A" * (security_config.MAX_INPUT_LENGTH + 100)
    response = chatbot.chat(long_message)
    if not response['success']:
        print("✅ Input length validation working")
    else:
        print("❌ Input length validation failed")
    
    # Test dangerous pattern detection
    dangerous_message = "Hello <script>alert('xss')</script>"
    response = chatbot.chat(dangerous_message)
    if not response['success']:
        print("✅ Dangerous pattern detection working")
    else:
        print("❌ Dangerous pattern detection failed")

def test_export_functionality(chatbot):
    """Test export functionality."""
    print("\n🧪 Testing Export Functionality...")
    
    export_data = chatbot.export_conversation()
    if 'error' not in export_data:
        print("✅ Export functionality working")
        print(f"   - Messages: {len(export_data.get('messages', []))}")
        print(f"   - Metadata: {export_data.get('metadata', {})}")
    else:
        print(f"❌ Export failed: {export_data.get('error')}")

def test_memory_clear(chatbot):
    """Test memory clearing functionality."""
    print("\n🧪 Testing Memory Clear Functionality...")
    
    # Get initial message count
    initial_stats = chatbot.get_memory_info()
    initial_count = initial_stats.get('memory_stats', {}).get('total_messages', 0)
    
    # Clear memory
    success = chatbot.clear_conversation()
    if success:
        print("✅ Memory cleared successfully")
        
        # Check if memory is actually cleared
        after_stats = chatbot.get_memory_info()
        after_count = after_stats.get('memory_stats', {}).get('total_messages', 0)
        
        if after_count == 0:
            print("✅ Memory verification successful")
        else:
            print(f"❌ Memory verification failed: {after_count} messages remaining")
    else:
        print("❌ Memory clear failed")

def test_bot_info(chatbot):
    """Test bot information retrieval."""
    print("\n🧪 Testing Bot Information...")
    
    bot_info = chatbot.get_bot_info()
    print(f"✅ Bot Name: {bot_info.get('name', 'Unknown')}")
    print(f"✅ Model: {bot_info.get('model', 'Unknown')}")
    print(f"✅ Memory Type: {bot_info.get('memory_type', 'Unknown')}")
    print(f"✅ Security Features: {len(bot_info.get('security_features', []))}")

def run_comprehensive_test():
    """Run comprehensive test suite."""
    print("🚀 Starting Comprehensive Chatbot Test Suite")
    print("=" * 50)
    
    # Initialize chatbot
    chatbot = test_chatbot_initialization()
    if not chatbot:
        return
    
    # Run all tests
    test_basic_chat(chatbot)
    test_memory_features(chatbot)
    test_security_features(chatbot)
    test_export_functionality(chatbot)
    test_memory_clear(chatbot)
    test_bot_info(chatbot)
    
    print("\n" + "=" * 50)
    print("🎉 Test Suite Completed!")
    print("=" * 50)

def interactive_demo():
    """Interactive demo mode."""
    print("🎮 Interactive Demo Mode")
    print("Type 'quit' to exit, 'clear' to clear memory, 'stats' for memory stats")
    print("-" * 50)
    
    chatbot = CustomChatbot()
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'clear':
                if chatbot.clear_conversation():
                    print("✅ Memory cleared!")
                else:
                    print("❌ Failed to clear memory")
                continue
            elif user_input.lower() == 'stats':
                memory_info = chatbot.get_memory_info()
                print(f"📊 Memory Stats: {memory_info}")
                continue
            elif not user_input:
                continue
            
            response = chatbot.chat(user_input)
            
            if response['success']:
                print(f"Bot: {response['response']}")
            else:
                print(f"❌ Error: {response.get('error', 'Unknown error')}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        interactive_demo()
    else:
        run_comprehensive_test() 