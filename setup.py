#!/usr/bin/env python3
"""
Setup script for LangChain Custom Chatbot with Memory.
Helps users install dependencies and configure the environment.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print setup banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║              🤖 LangChain Custom Chatbot Setup 🤖            ║
║                    with Memory Capabilities                  ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    
    try:
        # Check if pip is available
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ pip is not available!")
        return False
    
    try:
        # Install dependencies from requirements.txt
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file from template."""
    print("\n🔧 Setting up environment configuration...")
    
    env_template = "env_example.txt"
    env_file = ".env"
    
    if os.path.exists(env_file):
        print(f"⚠️  {env_file} already exists, skipping...")
        return True
    
    if not os.path.exists(env_template):
        print(f"❌ Template file {env_template} not found!")
        return False
    
    try:
        shutil.copy(env_template, env_file)
        print(f"✅ Created {env_file} from template")
        print("   Please edit the file and add your OpenAI API key")
        return True
    except Exception as e:
        print(f"❌ Failed to create {env_file}: {e}")
        return False

def check_openai_key():
    """Check if OpenAI API key is configured."""
    print("\n🔑 Checking OpenAI API key...")
    
    # Check environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✅ OpenAI API key found in environment variables")
        return True
    
    # Check .env file
    env_file = ".env"
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                if "OPENAI_API_KEY=your_openai_api_key_here" in content:
                    print("⚠️  OpenAI API key not configured in .env file")
                    print("   Please edit .env file and add your API key")
                    return False
                elif "OPENAI_API_KEY=" in content:
                    print("✅ OpenAI API key found in .env file")
                    return True
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
            return False
    
    print("❌ OpenAI API key not found!")
    print("   Please set OPENAI_API_KEY environment variable or configure .env file")
    return False

def test_installation():
    """Test the installation."""
    print("\n🧪 Testing installation...")
    
    try:
        # Test importing the chatbot
        from src.chatbot import CustomChatbot
        print("✅ Chatbot module imported successfully")
        
        # Test configuration
        from src.config import config
        print("✅ Configuration loaded successfully")
        
        # Test memory manager
        from src.memory_manager import SecureMemoryManager
        print("✅ Memory manager imported successfully")
        
        print("✅ All modules imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def show_next_steps():
    """Show next steps for the user."""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Configure your OpenAI API key:")
    print("   - Edit .env file and add your API key")
    print("   - Or set OPENAI_API_KEY environment variable")
    print("\n2. Start the chatbot:")
    print("   Web Interface: streamlit run app.py")
    print("   CLI Interface: python cli.py chat")
    print("   Test Suite: python test_chatbot.py")
    print("\n3. Documentation:")
    print("   - Read README.md for detailed instructions")
    print("   - Run 'python cli.py help' for CLI help")
    print("\n🚀 Happy chatting!")

def main():
    """Main setup function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed! Please install dependencies manually:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Create environment file
    create_env_file()
    
    # Check OpenAI API key
    api_key_configured = check_openai_key()
    
    # Test installation
    if not test_installation():
        print("\n❌ Installation test failed!")
        sys.exit(1)
    
    # Show next steps
    show_next_steps()
    
    if not api_key_configured:
        print("\n⚠️  Remember to configure your OpenAI API key before using the chatbot!")

if __name__ == "__main__":
    main() 