"""
Preview Component
"""

import streamlit as st
from typing import Dict, List
from PIL import Image

from utils.preview_handler import PreviewHandler


def render_preview(content: Dict, template_data: Dict) -> None:
    """Render the presentation preview"""
    
    if not content or 'slides' not in content:
        st.info("Generate content to see preview")
        return
    
    preview_handler = PreviewHandler(template_data)
    previews = preview_handler.generate_previews(content)
    
    if not previews:
        st.warning("Could not generate previews")
        return
    
    view_mode = st.radio("View", ["Single", "Grid"], horizontal=True, label_visibility="collapsed")
    
    if view_mode == "Single":
        if 'current_slide' not in st.session_state:
            st.session_state.current_slide = 0
        
        idx = st.session_state.current_slide
        
        col1, col2, col3 = st.columns([1, 6, 1])
        
        with col1:
            if st.button("◀", disabled=idx == 0):
                st.session_state.current_slide -= 1
                st.rerun()
        
        with col2:
            st.markdown(f"<p style='text-align:center;color:#94A3B8;'>Slide {idx + 1} of {len(previews)}</p>", unsafe_allow_html=True)
        
        with col3:
            if st.button("▶", disabled=idx >= len(previews) - 1):
                st.session_state.current_slide += 1
                st.rerun()
        
        if 0 <= idx < len(previews):
            # UPDATED: use_container_width=True → width="stretch"
            st.image(previews[idx], width="stretch")
            
            slide = content['slides'][idx]
            st.markdown(f"**{slide.get('title', 'Untitled')}** — Layout: {slide.get('layout', 'content').title()}")
    
    else:
        cols_per_row = 3
        for row_start in range(0, len(previews), cols_per_row):
            cols = st.columns(cols_per_row)
            for i, col in enumerate(cols):
                slide_idx = row_start + i
                if slide_idx < len(previews):
                    with col:
                        # UPDATED: use_container_width=True → width="stretch"
                        st.image(previews[slide_idx].resize((320, 180)), width="stretch")
                        st.caption(f"{slide_idx + 1}. {content['slides'][slide_idx].get('title', '')[:20]}...")
