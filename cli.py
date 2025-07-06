"""
Command Line Interface for LangChain Custom Chatbot with Memory.
Provides a simple CLI alternative to the web interface.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from src.chatbot import CustomChatbot
from src.config import config, security_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def print_banner():
    """Print application banner."""
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                    🤖 {config.chatbot_name} 🤖                    ║
║              LangChain Custom Chatbot with Memory            ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def print_help():
    """Print help information."""
    help_text = """
Commands:
  chat                    Start interactive chat mode
  test                    Run comprehensive tests
  info                    Show chatbot information
  stats                   Show memory statistics
  clear                   Clear conversation memory
  export                  Export conversation data
  help                    Show this help message
  quit                    Exit the application

Special commands in chat mode:
  /clear                  Clear conversation memory
  /stats                  Show memory statistics
  /info                   Show chatbot information
  /export                 Export conversation data
  /help                   Show help
  /quit                   Exit chat mode
"""
    print(help_text)

def interactive_chat():
    """Start interactive chat mode."""
    print(f"\n🎮 Starting interactive chat with {config.chatbot_name}...")
    print("Type '/help' for available commands")
    print("-" * 60)
    
    try:
        chatbot = CustomChatbot()
        print(f"✅ {config.chatbot_name} initialized successfully!")
        
        while True:
            try:
                # Get user input
                user_input = input(f"\n💬 You: ").strip()
                
                # Handle special commands
                if user_input.startswith('/'):
                    handle_special_command(user_input, chatbot)
                    continue
                
                # Handle empty input
                if not user_input:
                    continue
                
                # Security: Validate input length
                if len(user_input) > security_config.MAX_INPUT_LENGTH:
                    print(f"❌ Message too long! Maximum {security_config.MAX_INPUT_LENGTH} characters allowed.")
                    continue
                
                # Process message
                print("🤖 Thinking...")
                response = chatbot.chat(user_input)
                
                if response['success']:
                    print(f"🤖 {config.chatbot_name}: {response['response']}")
                    
                    # Show memory stats if available
                    if 'memory_stats' in response:
                        stats = response['memory_stats']
                        if 'memory_stats' in stats:
                            total_msgs = stats['memory_stats'].get('total_messages', 0)
                            print(f"📊 Memory: {total_msgs} messages in history")
                else:
                    print(f"❌ Error: {response.get('error', 'Unknown error')}")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        return False
    
    return True

def handle_special_command(command, chatbot):
    """Handle special commands in chat mode."""
    cmd = command.lower()
    
    if cmd == '/clear':
        if chatbot.clear_conversation():
            print("✅ Conversation memory cleared!")
        else:
            print("❌ Failed to clear memory")
    
    elif cmd == '/stats':
        memory_info = chatbot.get_memory_info()
        if 'memory_stats' in memory_info:
            stats = memory_info['memory_stats']
            print(f"📊 Memory Statistics:")
            print(f"   Total Messages: {stats.get('total_messages', 0)}")
            print(f"   Window Size: {stats.get('window_size', 10)}")
            print(f"   Has Summary: {'Yes' if stats.get('has_summary', False) else 'No'}")
        else:
            print("❌ Failed to get memory statistics")
    
    elif cmd == '/info':
        bot_info = chatbot.get_bot_info()
        print(f"🤖 Bot Information:")
        print(f"   Name: {bot_info.get('name', 'Unknown')}")
        print(f"   Model: {bot_info.get('model', 'Unknown')}")
        print(f"   Memory Type: {bot_info.get('memory_type', 'Unknown')}")
        print(f"   Security Features: {len(bot_info.get('security_features', []))}")
    
    elif cmd == '/export':
        export_data = chatbot.export_conversation()
        if 'error' not in export_data:
            filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                print(f"✅ Conversation exported to {filename}")
            except Exception as e:
                print(f"❌ Failed to export: {e}")
        else:
            print(f"❌ Export failed: {export_data.get('error')}")
    
    elif cmd == '/help':
        print("""
Special Commands:
  /clear    - Clear conversation memory
  /stats    - Show memory statistics
  /info     - Show chatbot information
  /export   - Export conversation data
  /help     - Show this help
  /quit     - Exit chat mode
        """)
    
    elif cmd == '/quit':
        print("👋 Goodbye!")
        sys.exit(0)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Type '/help' for available commands")

def show_bot_info():
    """Show chatbot information."""
    try:
        chatbot = CustomChatbot()
        bot_info = chatbot.get_bot_info()
        
        print(f"\n🤖 {config.chatbot_name} Information:")
        print("=" * 50)
        print(f"Name: {bot_info.get('name', 'Unknown')}")
        print(f"Model: {bot_info.get('model', 'Unknown')}")
        print(f"Memory Type: {bot_info.get('memory_type', 'Unknown')}")
        print(f"Personality: {config.chatbot_personality}")
        print(f"Security Features: {len(bot_info.get('security_features', []))}")
        
        print("\nSecurity Features:")
        for feature in bot_info.get('security_features', []):
            print(f"  ✅ {feature}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def show_memory_stats():
    """Show memory statistics."""
    try:
        chatbot = CustomChatbot()
        memory_info = chatbot.get_memory_info()
        
        print(f"\n📊 Memory Statistics:")
        print("=" * 50)
        
        if 'memory_stats' in memory_info:
            stats = memory_info['memory_stats']
            print(f"Total Messages: {stats.get('total_messages', 0)}")
            print(f"Window Size: {stats.get('window_size', 10)}")
            print(f"Has Summary: {'Yes' if stats.get('has_summary', False) else 'No'}")
            
            if 'conversation_metadata' in stats:
                metadata = stats['conversation_metadata']
                print(f"Start Time: {metadata.get('start_time', 'Unknown')}")
                print(f"Message Count: {metadata.get('message_count', 0)}")
                print(f"Total Tokens: {metadata.get('total_tokens', 0)}")
        else:
            print("No memory statistics available")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def clear_conversation():
    """Clear conversation memory."""
    try:
        chatbot = CustomChatbot()
        if chatbot.clear_conversation():
            print("✅ Conversation memory cleared successfully!")
        else:
            print("❌ Failed to clear conversation memory")
    except Exception as e:
        print(f"❌ Error: {e}")

def export_conversation():
    """Export conversation data."""
    try:
        chatbot = CustomChatbot()
        export_data = chatbot.export_conversation()
        
        if 'error' not in export_data:
            filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            print(f"✅ Conversation exported to {filename}")
            
            # Show export summary
            messages = export_data.get('messages', [])
            print(f"   Messages exported: {len(messages)}")
            
            if 'metadata' in export_data:
                metadata = export_data['metadata']
                print(f"   Start time: {metadata.get('start_time', 'Unknown')}")
                print(f"   Message count: {metadata.get('message_count', 0)}")
        else:
            print(f"❌ Export failed: {export_data.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description=f"{config.chatbot_name} - LangChain Custom Chatbot with Memory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py chat          # Start interactive chat
  python cli.py info          # Show bot information
  python cli.py stats         # Show memory statistics
  python cli.py test          # Run tests
        """
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        default='chat',
        choices=['chat', 'test', 'info', 'stats', 'clear', 'export', 'help'],
        help='Command to execute'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Handle commands
    if args.command == 'chat':
        interactive_chat()
    elif args.command == 'test':
        from test_chatbot import run_comprehensive_test
        run_comprehensive_test()
    elif args.command == 'info':
        show_bot_info()
    elif args.command == 'stats':
        show_memory_stats()
    elif args.command == 'clear':
        clear_conversation()
    elif args.command == 'export':
        export_conversation()
    elif args.command == 'help':
        print_help()
    else:
        print(f"❌ Unknown command: {args.command}")
        print_help()

if __name__ == "__main__":
    main() 