"""
AI Chat Interface Component
Updated to get llm_handler and model from session_state
"""
import streamlit as st
from typing import Dict, List, Any, Optional
import time

def render_chat_interface():
    """Render the AI chat interface - gets llm_handler from session_state"""
    
    # Get llm_handler from session_state
    llm_handler = st.session_state.get('llm_handler', None)
    model = st.session_state.get('config', None)
    model_name = model.default_model if model else "llama-3.3-70b-versatile"
    
    if not llm_handler:
        st.error("❌ LLM Handler not initialized. Please configure API key first.")
        return
    
    if not llm_handler.is_configured():
        st.error("❌ API not configured. Please set GROQ_API_KEY in sidebar.")
        return
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Chat interface header
    st.markdown("""
    <style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        gap: 1rem;
    }
    .chat-message.user {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
    }
    .chat-message.assistant {
        background-color: #f5f5f5;
        border-left: 4px solid #4CAF50;
    }
    .chat-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }
    .chat-content {
        flex: 1;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display chat history
    st.subheader("💬 Chat History")
    
    if not st.session_state.chat_history:
        st.info("👋 Start a conversation! Ask me to help with your presentation.")
    
    for message in st.session_state.chat_history:
        role = message.get('role', 'user')
        content = message.get('content', '')
        
        avatar = "👤" if role == 'user' else "🤖"
        css_class = "user" if role == 'user' else "assistant"
        
        st.markdown(f"""
        <div class="chat-message {css_class}">
            <div class="chat-avatar">{avatar}</div>
            <div class="chat-content">
                <strong>{'You' if role == 'user' else 'AI Assistant'}</strong>
                <p>{content}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Chat input
    st.subheader("✉️ Send a Message")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Your message",
            placeholder="e.g., Add a slide about AI trends",
            label_visibility="collapsed",
            key="chat_input"
        )
    
    with col2:
        send_button = st.button("📤 Send", use_container_width=True)
    
    # Quick action buttons
    st.markdown("### ⚡ Quick Actions")
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if st.button("📊 Add Chart Slide", use_container_width=True):
            user_input = "Add a chart slide showing AI adoption trends"
            st.session_state.chat_input = user_input
            st.rerun()
    
    with col_b:
        if st.button("📋 Add Table Slide", use_container_width=True):
            user_input = "Add a table slide comparing AI solutions"
            st.session_state.chat_input = user_input
            st.rerun()
    
    with col_c:
        if st.button("🎯 Improve Content", use_container_width=True):
            user_input = "Improve the content of the current slides"
            st.session_state.chat_input = user_input
            st.rerun()
    
    st.divider()
    
    # Process message
    if send_button and user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input
        })
        
        # Show processing indicator
        with st.spinner("🤔 AI is thinking..."):
            try:
                # Build context from current presentation
                context = ""
                if st.session_state.get('slides', []):
                    context = f"Current presentation has {len(st.session_state.slides)} slides.\n"
                    context += f"Title: {st.session_state.get('presentation_title', 'Untitled')}\n"
                    context += "Slides:\n"
                    for i, slide in enumerate(st.session_state.slides[:3], 1):
                        context += f"  {i}. {slide.get('title', 'Untitled')} ({slide.get('layout', 'content')})\n"
                
                # Create prompt with context
                prompt = f"""
                You are an AI presentation assistant. Help the user improve their presentation.
                
                {context}
                
                User request: {user_input}
                
                Provide helpful, actionable suggestions. If the user wants to modify slides,
                explain what changes you recommend. Be concise and professional.
                """
                
                # Get AI response
                response = llm_handler.generate_response(
                    prompt=prompt,
                    model=model_name,
                    max_tokens=1000
                )
                
                # Add assistant response to history
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response or "Sorry, I couldn't generate a response."
                })
                
                st.success("✅ Response received!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': f"Sorry, I encountered an error: {str(e)}"
                })
                st.rerun()
    
    # Clear chat history
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
    
    # Settings
    with st.expander("⚙️ Chat Settings"):
        st.selectbox(
            "Model",
            options=["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
            index=0,
            key="chat_model"
        )
        
        st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Higher values = more creative, Lower values = more focused"
        )
        
        st.slider(
            "Max Tokens",
            min_value=100,
            max_value=4000,
            value=1000,
            step=100
        )
