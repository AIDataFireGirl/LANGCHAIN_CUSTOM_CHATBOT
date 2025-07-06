"""
Streamlit Web Application for LangChain Custom Chatbot with Memory.
Provides a user-friendly interface for interacting with the chatbot.
"""

import streamlit as st
import json
import logging
from datetime import datetime
from src.chatbot import CustomChatbot
from src.config import config, security_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title=f"{config.chatbot_name} - AI Chatbot with Memory",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .memory-info {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff9800;
    }
    .sidebar-section {
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'chatbot' not in st.session_state:
        try:
            st.session_state.chatbot = CustomChatbot()
            st.session_state.messages = []
            st.session_state.memory_stats = {}
        except Exception as e:
            st.error(f"Failed to initialize chatbot: {e}")
            st.stop()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'memory_stats' not in st.session_state:
        st.session_state.memory_stats = {}

def display_header():
    """Display the main header and chatbot information."""
    st.markdown(f'<h1 class="main-header">🤖 {config.chatbot_name}</h1>', unsafe_allow_html=True)
    
    # Display chatbot info
    bot_info = st.session_state.chatbot.get_bot_info()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Model:** {bot_info['model']}")
    with col2:
        st.info(f"**Memory Type:** {bot_info['memory_type']}")
    with col3:
        st.info(f"**Security:** {len(bot_info['security_features'])} features active")

def display_sidebar():
    """Display sidebar with controls and information."""
    st.sidebar.title("🎛️ Controls")
    
    # Memory Information
    st.sidebar.markdown("### 📊 Memory Stats")
    memory_info = st.session_state.chatbot.get_memory_info()
    
    if 'memory_stats' in memory_info:
        stats = memory_info['memory_stats']
        st.sidebar.metric("Total Messages", stats.get('total_messages', 0))
        st.sidebar.metric("Window Size", stats.get('window_size', 10))
        st.sidebar.metric("Has Summary", "Yes" if stats.get('has_summary', False) else "No")
    
    # Controls
    st.sidebar.markdown("### ⚙️ Actions")
    
    if st.sidebar.button("🗑️ Clear Conversation", type="secondary"):
        if st.session_state.chatbot.clear_conversation():
            st.session_state.messages = []
            st.session_state.memory_stats = {}
            st.sidebar.success("Conversation cleared!")
            st.rerun()
        else:
            st.sidebar.error("Failed to clear conversation")
    
    if st.sidebar.button("📊 Export Conversation", type="secondary"):
        export_data = st.session_state.chatbot.export_conversation()
        if 'error' not in export_data:
            # Create downloadable JSON file
            json_str = json.dumps(export_data, indent=2, default=str)
            st.sidebar.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        else:
            st.sidebar.error("Failed to export conversation")
    
    # Security Information
    st.sidebar.markdown("### 🔒 Security Features")
    security_features = [
        f"✅ Max input length: {security_config.MAX_INPUT_LENGTH} chars",
        f"✅ Content sanitization",
        f"✅ Pattern detection",
        f"✅ Memory size limits"
    ]
    
    for feature in security_features:
        st.sidebar.text(feature)
    
    # Configuration
    st.sidebar.markdown("### ⚙️ Configuration")
    st.sidebar.text(f"Model: {config.model_name}")
    st.sidebar.text(f"Temperature: {config.temperature}")
    st.sidebar.text(f"Max Tokens: {config.max_tokens}")

def display_chat_interface():
    """Display the main chat interface."""
    st.markdown("### 💬 Chat Interface")
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Security: Validate input length
        if len(user_input) > security_config.MAX_INPUT_LENGTH:
            st.error(f"Message too long! Maximum {security_config.MAX_INPUT_LENGTH} characters allowed.")
            return
        
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get bot response
        with st.spinner("🤖 Thinking..."):
            response = st.session_state.chatbot.chat(user_input)
        
        if response['success']:
            # Add bot response to chat
            st.session_state.messages.append({"role": "assistant", "content": response['response']})
            
            # Update memory stats
            st.session_state.memory_stats = response.get('memory_stats', {})
            
            # Display memory info if available
            if 'conversation_summary' in response and response['conversation_summary']:
                with st.expander("📝 Conversation Summary"):
                    st.text(response['conversation_summary'])
        else:
            st.error(f"Error: {response.get('error', 'Unknown error')}")
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message bot-message">
                <strong>{config.chatbot_name}:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)

def display_memory_info():
    """Display detailed memory information."""
    st.markdown("### 🧠 Memory Information")
    
    memory_info = st.session_state.chatbot.get_memory_info()
    
    if 'memory_stats' in memory_info:
        stats = memory_info['memory_stats']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Memory Statistics:**")
            st.json(stats)
        
        with col2:
            st.markdown("**Conversation Summary:**")
            if 'conversation_summary' in memory_info:
                st.text(memory_info['conversation_summary'])
            else:
                st.text("No summary available")

def main():
    """Main application function."""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Display header
        display_header()
        
        # Create tabs for different sections
        tab1, tab2, tab3 = st.tabs(["💬 Chat", "🧠 Memory", "ℹ️ About"])
        
        with tab1:
            display_chat_interface()
        
        with tab2:
            display_memory_info()
        
        with tab3:
            st.markdown("### About This Chatbot")
            st.markdown("""
            This is a custom chatbot built with **LangChain** that features:
            
            - **Memory Capabilities**: Remembers conversation context
            - **Security Features**: Input validation and sanitization
            - **Modular Design**: Clean, maintainable code structure
            - **Web Interface**: User-friendly Streamlit interface
            
            **Features:**
            - Conversation memory with configurable window size
            - Automatic conversation summarization
            - Input length and content validation
            - Export conversation functionality
            - Real-time memory statistics
            
            **Security:**
            - Maximum input length limits
            - Content sanitization
            - Dangerous pattern detection
            - Memory size limits
            """)
            
            st.markdown("### Flowchart")
            st.markdown("""
            ```mermaid
            graph TD
                A[User Input] --> B[Input Validation]
                B --> C{Valid Input?}
                C -->|No| D[Error Message]
                C -->|Yes| E[Add to Memory]
                E --> F[Generate Response]
                F --> G[Add Response to Memory]
                G --> H[Update Statistics]
                H --> I[Display Response]
                I --> J[Show Memory Info]
                
                K[Clear Memory] --> L[Reset Conversation]
                M[Export Data] --> N[Download JSON]
            ```
            """)
        
        # Display sidebar
        display_sidebar()
        
    except Exception as e:
        st.error(f"Application error: {e}")
        logger.error(f"Application error: {e}")

if __name__ == "__main__":
    main() 