"""
Slide Editor Component
"""
import streamlit as st
from typing import Dict, List, Any, Optional

def render_slide_editor():
    """Render the slide editor interface"""
    
    if not st.session_state.get('slides', []):
        st.info("No slides available. Generate content first.")
        return
    
    slides = st.session_state.slides
    
    # Slide navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("◀ Previous", use_container_width=True):
            if st.session_state.current_slide_index > 0:
                st.session_state.current_slide_index -= 1
                st.rerun()
    
    with col2:
        current_idx = st.session_state.current_slide_index
        total_slides = len(slides)
        st.write(f"**Slide {current_idx + 1} of {total_slides}**")
    
    with col3:
        if st.button("Next ▶", use_container_width=True):
            if st.session_state.current_slide_index < total_slides - 1:
                st.session_state.current_slide_index += 1
                st.rerun()
    
    st.divider()
    
    # Edit current slide
    current_slide = slides[st.session_state.current_slide_index]
    
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        # Edit title
        new_title = st.text_input(
            "Slide Title",
            value=current_slide.get('title', ''),
            key=f"title_{st.session_state.current_slide_index}"
        )
        
        # Edit layout
        layout_options = [
            'title', 'content', 'two_column', 'chart', 'table',
            'quote', 'metrics', 'timeline', 'image', 'conclusion'
        ]
        new_layout = st.selectbox(
            "Slide Layout",
            options=layout_options,
            index=layout_options.index(current_slide.get('layout', 'content')) if current_slide.get('layout') in layout_options else 1,
            key=f"layout_{st.session_state.current_slide_index}"
        )
    
    with col_b:
        st.metric("Layout", current_slide.get('layout', 'content'))
        st.metric("Slide #", current_slide.get('slide_number', st.session_state.current_slide_index + 1))
    
    st.divider()
    
    # Edit content based on layout
    st.subheader("📝 Content")
    
    content = current_slide.get('content', {})
    
    if new_layout == 'content':
        main_text = st.text_area("Main Text", value=content.get('main_text', ''), height=100)
        bullet_points = st.text_area("Bullet Points (one per line)", value="\n".join(content.get('bullet_points', [])), height=150)
        
        if st.button("💾 Save Changes", key="save_content"):
            slides[st.session_state.current_slide_index]['title'] = new_title
            slides[st.session_state.current_slide_index]['layout'] = new_layout
            slides[st.session_state.current_slide_index]['content'] = {
                'main_text': main_text,
                'bullet_points': [p.strip() for p in bullet_points.split('\n') if p.strip()]
            }
            st.session_state.slides = slides
            st.success("✅ Slide saved!")
    
    elif new_layout == 'two_column':
        left_col = st.text_area("Left Column", value="\n".join(content.get('left_column', [])) if isinstance(content.get('left_column'), list) else content.get('left_column', ''), height=200)
        right_col = st.text_area("Right Column", value="\n".join(content.get('right_column', [])) if isinstance(content.get('right_column'), list) else content.get('right_column', ''), height=200)
        
        if st.button("💾 Save Changes", key="save_two_column"):
            slides[st.session_state.current_slide_index]['title'] = new_title
            slides[st.session_state.current_slide_index]['layout'] = new_layout
            slides[st.session_state.current_slide_index]['content'] = {
                'left_column': [p.strip() for p in left_col.split('\n') if p.strip()],
                'right_column': [p.strip() for p in right_col.split('\n') if p.strip()]
            }
            st.session_state.slides = slides
            st.success("✅ Slide saved!")
    
    elif new_layout == 'chart':
        chart_title = st.text_input("Chart Title", value=content.get('chart', {}).get('title', ''))
        chart_desc = st.text_area("Chart Description", value=content.get('chart', {}).get('description', ''), height=100)
        chart_data = st.text_area("Chart Data (key: value per line)", value="\n".join([f"{k}: {v}" for k, v in content.get('chart', {}).get('data', {}).items()]), height=200)
        
        if st.button("💾 Save Changes", key="save_chart"):
            data_dict = {}
            for line in chart_data.split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1)
                    data_dict[k.strip()] = v.strip()
            
            slides[st.session_state.current_slide_index]['title'] = new_title
            slides[st.session_state.current_slide_index]['layout'] = new_layout
            slides[st.session_state.current_slide_index]['content'] = {
                'chart': {
                    'title': chart_title,
                    'description': chart_desc,
                    'data': data_dict
                }
            }
            st.session_state.slides = slides
            st.success("✅ Slide saved!")
    
    elif new_layout == 'table':
        headers = st.text_input("Headers (comma-separated)", value=",".join(content.get('table', {}).get('headers', [])))
        table_rows = st.text_area("Table Rows (one row per line, comma-separated values)", value="\n".join([",".join(row) for row in content.get('table', {}).get('data', [])]), height=200)
        
        if st.button("💾 Save Changes", key="save_table"):
            slides[st.session_state.current_slide_index]['title'] = new_title
            slides[st.session_state.current_slide_index]['layout'] = new_layout
            slides[st.session_state.current_slide_index]['content'] = {
                'table': {
                    'headers': [h.strip() for h in headers.split(',') if h.strip()],
                    'data': [[cell.strip() for cell in row.split(',')] for row in table_rows.split('\n') if row.strip()]
                }
            }
            st.session_state.slides = slides
            st.success("✅ Slide saved!")
    
    elif new_layout == 'quote':
        quote_text = st.text_area("Quote", value=content.get('quote', ''), height=100)
        quote_author = st.text_input("Author", value=content.get('quote_author', ''))
        
        if st.button("💾 Save Changes", key="save_quote"):
            slides[st.session_state.current_slide_index]['title'] = new_title
            slides[st.session_state.current_slide_index]['layout'] = new_layout
            slides[st.session_state.current_slide_index]['content'] = {
                'quote': quote_text,
                'quote_author': quote_author
            }
            st.session_state.slides = slides
            st.success("✅ Slide saved!")
    
    elif new_layout == 'metrics':
        metrics_input = st.text_area("Metrics (label: value per line)", value="\n".join([f"{m.get('label', '')}: {m.get('value', '')}" for m in content.get('key_metrics', [])]), height=200)
        
        if st.button("💾 Save Changes", key="save_metrics"):
            metrics_list = []
            for line in metrics_input.split('\n'):
                if ':' in line:
                    label, value = line.split(':', 1)
                    metrics_list.append({'label': label.strip(), 'value': value.strip()})
            
            slides[st.session_state.current_slide_index]['title'] = new_title
            slides[st.session_state.current_slide_index]['layout'] = new_layout
            slides[st.session_state.current_slide_index]['content'] = {
                'key_metrics': metrics_list
            }
            st.session_state.slides = slides
            st.success("✅ Slide saved!")
    
    elif new_layout == 'image':
        image_desc = st.text_area("Image Description", value=content.get('image', '') if isinstance(content.get('image'), str) and not content.get('image').startswith('data:') else '', height=100)
        st.info("📌 Note: Images are auto-generated by AI. Manual upload coming soon.")
        
        if st.button("💾 Save Changes", key="save_image"):
            slides[st.session_state.current_slide_index]['title'] = new_title
            slides[st.session_state.current_slide_index]['layout'] = new_layout
            slides[st.session_state.current_slide_index]['content'] = {
                'image': image_desc
            }
            st.session_state.slides = slides
            st.success("✅ Slide saved!")
    
    elif new_layout == 'timeline':
        timeline_input = st.text_area("Timeline Items (date: description per line)", value="\n".join([f"{t.get('date', '')}: {t.get('description', '')}" for t in content.get('timeline_items', [])]), height=200)
        
        if st.button("💾 Save Changes", key="save_timeline"):
            timeline_list = []
            for line in timeline_input.split('\n'):
                if ':' in line:
                    date, desc = line.split(':', 1)
                    timeline_list.append({'date': date.strip(), 'description': desc.strip()})
            
            slides[st.session_state.current_slide_index]['title'] = new_title
            slides[st.session_state.current_slide_index]['layout'] = new_layout
            slides[st.session_state.current_slide_index]['content'] = {
                'timeline_items': timeline_list
            }
            st.session_state.slides = slides
            st.success("✅ Slide saved!")
    
    elif new_layout == 'conclusion':
        main_text = st.text_area("Conclusion Text", value=content.get('main_text', ''), height=100)
        bullet_points = st.text_area("Key Points (one per line)", value="\n".join(content.get('bullet_points', [])), height=150)
        
        if st.button("💾 Save Changes", key="save_conclusion"):
            slides[st.session_state.current_slide_index]['title'] = new_title
            slides[st.session_state.current_slide_index]['layout'] = new_layout
            slides[st.session_state.current_slide_index]['content'] = {
                'main_text': main_text,
                'bullet_points': [p.strip() for p in bullet_points.split('\n') if p.strip()]
            }
            st.session_state.slides = slides
            st.success("✅ Slide saved!")
    
    else:
        st.warning(f"Unknown layout: {new_layout}")
    
    # Slide management
    st.divider()
    st.subheader("⚙️ Slide Management")
    
    col_x, col_y, col_z = st.columns(3)
    
    with col_x:
        if st.button("➕ Add New Slide", use_container_width=True):
            new_slide = {
                'slide_number': len(slides) + 1,
                'layout': 'content',
                'title': 'New Slide',
                'content': {'main_text': '', 'bullet_points': []}
            }
            slides.append(new_slide)
            st.session_state.slides = slides
            st.session_state.current_slide_index = len(slides) - 1
            st.rerun()
    
    with col_y:
        if st.button("🗑️ Delete Current Slide", use_container_width=True, disabled=len(slides) <= 1):
            slides.pop(st.session_state.current_slide_index)
            # Renumber slides
            for i, slide in enumerate(slides):
                slide['slide_number'] = i + 1
            st.session_state.slides = slides
            if st.session_state.current_slide_index >= len(slides):
                st.session_state.current_slide_index = len(slides) - 1
            st.rerun()
    
    with col_z:
        if st.button("📋 Duplicate Slide", use_container_width=True):
            import copy
            new_slide = copy.deepcopy(slides[st.session_state.current_slide_index])
            new_slide['slide_number'] = len(slides) + 1
            new_slide['title'] = f"{new_slide['title']} (Copy)"
            slides.insert(st.session_state.current_slide_index + 1, new_slide)
            # Renumber slides
            for i, slide in enumerate(slides):
                slide['slide_number'] = i + 1
            st.session_state.slides = slides
            st.session_state.current_slide_index += 1
            st.rerun()
