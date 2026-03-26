"""
Chat Interface Component
"""

import streamlit as st
from typing import Optional, Callable
from utils.llm_handler import LLMHandler


def render_chat_interface(llm_handler: LLMHandler, model: str, on_generate: Optional[Callable] = None) -> Optional[str]:
    """Render the chat interface"""
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    st.markdown("### 💬 Content Generator")
    
    # Display chat history
    if not st.session_state.chat_history:
        st.markdown("""
        <div style="text-align:center;padding:2rem;color:#64748B;">
            <p style="font-size:3rem;">💡</p>
            <h4 style="color:#94A3B8;">Start Creating</h4>
            <p>Describe your presentation or paste content below.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history[-5:]:
            role = msg['role']
            content = msg['content']
            
            if role == 'user':
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#6366F1,#8B5CF6);padding:1rem;border-radius:12px;margin:0.5rem 0 0.5rem 20%;">
                    <p style="margin:0;color:white;">{content[:200]}...</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#1E293B;padding:1rem;border-radius:12px;margin:0.5rem 20% 0.5rem 0;border:1px solid #334155;">
                    <p style="margin:0;color:#F8FAFC;">{content[:200]}...</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.divider()
    
    # Quick prompts
    st.markdown("**Quick Prompts:**")
    
    cols = st.columns(4)
    prompts = [
        ("📊 Business", "Create a business proposal presentation for"),
        ("📈 Sales", "Create a sales pitch presentation for"),
        ("🎓 Training", "Create a training presentation about"),
        ("🚀 Product", "Create a product launch presentation for")
    ]
    
    for col, (label, template) in zip(cols, prompts):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.quick_prompt = template
    
    # Input area
    default = st.session_state.get('quick_prompt', '')
    
    user_input = st.text_area(
        "Describe your presentation",
        value=default,
        height=100,
        placeholder="E.g., Create a quarterly business review presentation for our tech startup focusing on growth metrics, product updates, and future roadmap..."
    )
    
    col1, col2 = st.columns([4, 1])
    
    with col2:
        generate_clicked = st.button("🚀 Generate", type="primary", use_container_width=True)
    
    if generate_clicked and user_input:
        st.session_state.chat_history.append({'role': 'user', 'content': user_input})
        st.session_state.quick_prompt = ''
        return user_input
    
    return None
