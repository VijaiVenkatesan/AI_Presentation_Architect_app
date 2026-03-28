from groq import Groq
import streamlit as st
import json

from core.search_engine import fetch_search_data
from utils.helpers import safe_json_load, ensure_slide_structure, validate_slide_count

def generate_content(prompt, model, slide_count):

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    search_context = fetch_search_data(prompt)

    final_prompt = f"""
STRICT JSON ONLY.

Generate {slide_count} enterprise slides.

Structure:
1 → Title
2 → Agenda
3+ → Content
Last → Summary

Topic: {prompt}

Use real-time data:
{search_context}

Format:
{{
 "slides":[
  {{
   "title":"",
   "bullet_points":[],
   "diagram_type":"",
   "image_prompt":""
  }}
 ]
}}
"""

    res = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": final_prompt}],
    )

    raw = res.choices[0].message.content

    data = safe_json_load(raw)
    data = ensure_slide_structure(data)
    data = validate_slide_count(data)

    return json.dumps(data)
