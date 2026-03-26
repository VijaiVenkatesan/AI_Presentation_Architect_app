"""
LLM Handler Module
Interfaces with Groq API for content generation with real-time model fetching
"""

import json
import requests
from typing import Dict, List, Optional, Generator, Tuple
from groq import Groq
import streamlit as st
from datetime import datetime, timedelta


class LLMHandler:
    """Handles interactions with Groq LLM API with dynamic model fetching"""
    
    # Fallback models if API fetch fails
    FALLBACK_MODELS = {
        "llama-3.3-70b-versatile": {
            "name": "Llama 3.3 70B Versatile",
            "description": "Latest Llama model, excellent for complex tasks",
            "context_window": 128000,
            "active": True
        },
        "llama-3.1-70b-versatile": {
            "name": "Llama 3.1 70B Versatile", 
            "description": "Powerful general-purpose model",
            "context_window": 128000,
            "active": True
        },
        "mixtral-8x7b-32768": {
            "name": "Mixtral 8x7B",
            "description": "Mixture of experts, great for diverse tasks",
            "context_window": 32768,
            "active": True
        }
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LLM handler with Groq API key"""
        self.api_key = api_key or st.secrets.get("GROQ_API_KEY", "")
        self.client = None
        self._models_cache = None
        self._models_cache_time = None
        self._cache_duration = timedelta(minutes=10)
        
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                st.error(f"Failed to initialize Groq client: {e}")
    
    def is_configured(self) -> bool:
        """Check if the LLM handler is properly configured"""
        return self.client is not None and bool(self.api_key)
    
    def fetch_available_models(self, force_refresh: bool = False) -> Dict[str, Dict]:
        """
        Fetch available models from Groq API in real-time
        Returns a dictionary of model_id -> model_info
        """
        # Check cache first
        if not force_refresh and self._models_cache and self._models_cache_time:
            if datetime.now() - self._models_cache_time < self._cache_duration:
                return self._models_cache
        
        if not self.api_key:
            return self.FALLBACK_MODELS
        
        try:
            # Fetch models from Groq API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                "https://api.groq.com/openai/v1/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                models = {}
                
                for model in data.get('data', []):
                    model_id = model.get('id', '')
                    
                    # Filter for chat/completion models only
                    if self._is_chat_model(model_id):
                        models[model_id] = {
                            'name': self._format_model_name(model_id),
                            'description': self._get_model_description(model_id),
                            'context_window': model.get('context_window', 8192),
                            'created': model.get('created', 0),
                            'owned_by': model.get('owned_by', 'groq'),
                            'active': True
                        }
                
                if models:
                    # Sort by recommendation
                    models = dict(sorted(
                        models.items(),
                        key=lambda x: self._get_model_priority(x[0]),
                        reverse=True
                    ))
                    
                    self._models_cache = models
                    self._models_cache_time = datetime.now()
                    return models
            
            return self.FALLBACK_MODELS
            
        except Exception as e:
            st.warning(f"Could not fetch models from Groq API: {e}")
            return self.FALLBACK_MODELS
    
    def _is_chat_model(self, model_id: str) -> bool:
        """Check if model is suitable for chat/completion tasks"""
        # Exclude whisper (audio), and other non-chat models
        excluded_patterns = ['whisper', 'audio', 'vision', 'guard', 'tool']
        model_lower = model_id.lower()
        
        for pattern in excluded_patterns:
            if pattern in model_lower:
                return False
        
        # Include known good model families
        included_patterns = ['llama', 'mixtral', 'gemma', 'qwen']
        for pattern in included_patterns:
            if pattern in model_lower:
                return True
        
        return False
    
    def _format_model_name(self, model_id: str) -> str:
        """Format model ID into a readable name"""
        name_map = {
            'llama-3.3-70b-versatile': '🚀 Llama 3.3 70B Versatile',
            'llama-3.3-70b-specdec': '⚡ Llama 3.3 70B SpecDec',
            'llama-3.2-90b-vision-preview': '👁️ Llama 3.2 90B Vision',
            'llama-3.2-11b-vision-preview': '👁️ Llama 3.2 11B Vision',
            'llama-3.2-3b-preview': '💨 Llama 3.2 3B Preview',
            'llama-3.2-1b-preview': '💨 Llama 3.2 1B Preview',
            'llama-3.1-70b-versatile': '🎯 Llama 3.1 70B Versatile',
            'llama-3.1-8b-instant': '⚡ Llama 3.1 8B Instant',
            'llama3-70b-8192': '🦙 Llama 3 70B',
            'llama3-8b-8192': '🦙 Llama 3 8B',
            'mixtral-8x7b-32768': '🎨 Mixtral 8x7B',
            'gemma2-9b-it': '💎 Gemma 2 9B',
            'gemma-7b-it': '💎 Gemma 7B',
            'qwen-2.5-72b-instruct': '🌟 Qwen 2.5 72B',
            'qwen-2.5-32b-instruct': '🌟 Qwen 2.5 32B',
            'deepseek-r1-distill-llama-70b': '🔬 DeepSeek R1 70B',
        }
        
        if model_id in name_map:
            return name_map[model_id]
        
        # Auto-format unknown models
        formatted = model_id.replace('-', ' ').replace('_', ' ').title()
        return f"🤖 {formatted}"
    
    def _get_model_description(self, model_id: str) -> str:
        """Get description for a model"""
        descriptions = {
            'llama-3.3-70b-versatile': 'Latest & most capable Llama model. Best for complex presentations.',
            'llama-3.3-70b-specdec': 'Speculative decoding variant for faster inference.',
            'llama-3.1-70b-versatile': 'Powerful all-purpose model with 128K context.',
            'llama-3.1-8b-instant': 'Fast responses, ideal for quick iterations.',
            'llama3-70b-8192': 'Reliable large model with 8K context.',
            'llama3-8b-8192': 'Balanced speed and quality.',
            'mixtral-8x7b-32768': 'Mixture of experts with 32K context. Great creativity.',
            'gemma2-9b-it': 'Google\'s efficient instruction-tuned model.',
            'gemma-7b-it': 'Compact Google model for basic tasks.',
            'qwen-2.5-72b-instruct': 'Alibaba\'s powerful multilingual model.',
            'qwen-2.5-32b-instruct': 'Fast Qwen variant with great performance.',
            'deepseek-r1-distill-llama-70b': 'DeepSeek\'s reasoning-focused model.',
        }
        
        return descriptions.get(model_id, 'AI model for content generation')
    
    def _get_model_priority(self, model_id: str) -> int:
        """Get priority score for model sorting (higher = better)"""
        priority_map = {
            'llama-3.3-70b-versatile': 100,
            'qwen-2.5-72b-instruct': 95,
            'deepseek-r1-distill-llama-70b': 93,
            'llama-3.1-70b-versatile': 90,
            'qwen-2.5-32b-instruct': 85,
            'mixtral-8x7b-32768': 80,
            'llama-3.1-8b-instant': 70,
            'gemma2-9b-it': 65,
            'llama3-70b-8192': 60,
            'llama3-8b-8192': 50,
            'gemma-7b-it': 40,
        }
        
        return priority_map.get(model_id, 30)
    
    def get_models_for_ui(self) -> List[Tuple[str, str, str, bool]]:
        """
        Get models formatted for UI display
        Returns list of tuples: (model_id, display_name, description, is_recommended)
        """
        models = self.fetch_available_models()
        
        recommended_models = [
            'llama-3.3-70b-versatile',
            'qwen-2.5-72b-instruct',
            'deepseek-r1-distill-llama-70b',
            'llama-3.1-70b-versatile',
            'mixtral-8x7b-32768'
        ]
        
        result = []
        for model_id, info in models.items():
            is_recommended = model_id in recommended_models
            result.append((
                model_id,
                info['name'],
                info['description'],
                is_recommended
            ))
        
        return result
    
    def test_model_availability(self, model_id: str) -> bool:
        """Test if a specific model is available and working"""
        if not self.is_configured():
            return False
        
        try:
            response = self.client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            return True
        except Exception:
            return False
    
    def generate_presentation_content(
        self,
        prompt: str,
        model: str = "llama-3.3-70b-versatile",
        num_slides: int = 10,
        template_context: Optional[Dict] = None,
        real_time_data: Optional[str] = None,
        layout_preferences: Optional[Dict] = None
    ) -> Dict:
        """Generate presentation content based on prompt"""
        
        if not self.is_configured():
            return self._get_fallback_content(prompt, num_slides)
        
        # Build the system prompt
        system_prompt = self._build_system_prompt(num_slides, template_context, layout_preferences)
        
        # Build the user prompt
        user_prompt = self._build_user_prompt(prompt, real_time_data)
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=8000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            st.error(f"Error generating content: {e}")
            return self._get_fallback_content(prompt, num_slides)
    
    def generate_content_stream(
        self,
        prompt: str,
        model: str = "llama-3.3-70b-versatile"
    ) -> Generator[str, None, None]:
        """Generate content with streaming response"""
        
        if not self.is_configured():
            yield "LLM not configured. Please add your Groq API key to secrets."
            return
        
        try:
            stream = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful presentation content assistant. Provide clear, professional content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"Error: {e}"
    
    def generate_chart_data(
        self,
        chart_description: str,
        model: str = "llama-3.3-70b-versatile"
    ) -> Dict:
        """Generate chart data based on description"""
        
        if not self.is_configured():
            return self._get_fallback_chart_data()
        
        system_prompt = """You are a data analyst. Generate realistic chart data based on the description.
        Return JSON in this exact format:
        {
            "chart_type": "bar|line|pie|scatter",
            "title": "Chart Title",
            "labels": ["Label1", "Label2", "Label3", "Label4"],
            "datasets": [
                {
                    "name": "Series Name",
                    "values": [number1, number2, number3, number4]
                }
            ],
            "x_axis_label": "X Axis Label",
            "y_axis_label": "Y Axis Label"
        }
        Generate realistic, plausible data that matches the description."""
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Generate chart data for: {chart_description}"}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"Error generating chart data: {e}")
            return self._get_fallback_chart_data()
    
    def enhance_content(
        self,
        content: str,
        instruction: str,
        model: str = "llama-3.3-70b-versatile"
    ) -> str:
        """Enhance or modify existing content"""
        
        if not self.is_configured():
            return content
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional content editor for business presentations. Improve content while maintaining professionalism."
                    },
                    {
                        "role": "user", 
                        "content": f"Instruction: {instruction}\n\nContent to modify:\n{content}"
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            st.error(f"Error enhancing content: {e}")
            return content
    
    def _build_system_prompt(
        self,
        num_slides: int,
        template_context: Optional[Dict],
        layout_preferences: Optional[Dict] = None
    ) -> str:
        """Build the system prompt for presentation generation"""
        
        # Determine which layouts to include
        available_layouts = ['title', 'content', 'conclusion']
        if layout_preferences:
            if layout_preferences.get('include_charts', True):
                available_layouts.append('chart')
            if layout_preferences.get('include_tables', True):
                available_layouts.append('table')
            if layout_preferences.get('include_timeline', False):
                available_layouts.append('timeline')
            if layout_preferences.get('include_comparison', False):
                available_layouts.append('comparison')
            available_layouts.extend(['two_column', 'quote', 'metrics', 'image'])
        else:
            available_layouts = ['title', 'content', 'two_column', 'chart', 'table', 'quote', 'conclusion', 'metrics']
        
        layouts_str = '|'.join(available_layouts)
        
        prompt = f"""You are an expert enterprise presentation architect. Create professional, engaging presentation content.

Generate EXACTLY {num_slides} slides in valid JSON format with this structure:
{{
    "title": "Presentation Title",
    "subtitle": "Subtitle",
    "author": "Author Name",
    "date": "Date",
    "slides": [
        {{
            "slide_number": 1,
            "layout": "{layouts_str}",
            "title": "Slide Title",
            "subtitle": "Optional Subtitle",
            "content": {{
                "main_text": "Main content text (for content slides)",
                "bullet_points": ["Point 1", "Point 2", "Point 3"],
                "left_column": "Left column content or bullet points array",
                "right_column": "Right column content or bullet points array",
                "chart": {{
                    "type": "bar|line|pie|scatter|area|funnel",
                    "title": "Chart Title",
                    "labels": ["Q1", "Q2", "Q3", "Q4"],
                    "datasets": [{{"name": "Series", "values": [10, 20, 30, 40]}}],
                    "data_description": "Description of data"
                }},
                "table": {{
                    "headers": ["Column1", "Column2", "Column3"],
                    "rows": [["Row1Val1", "Row1Val2", "Row1Val3"]]
                }},
                "quote": "Quote text",
                "quote_author": "Quote Author",
                "image_description": "Description for image placeholder",
                "key_metrics": [
                    {{"label": "Revenue", "value": "$1.2M"}},
                    {{"label": "Growth", "value": "+25%"}}
                ],
                "timeline_items": [
                    {{"date": "Q1 2024", "event": "Phase 1 Launch"}}
                ],
                "comparison_items": [
                    {{"title": "Option A", "pros": ["Pro 1"], "cons": ["Con 1"]}}
                ]
            }},
            "speaker_notes": "Detailed notes for the presenter"
        }}
    ]
}}

IMPORTANT RULES:
1. Create EXACTLY {num_slides} slides
2. First slide MUST be layout "title"
3. Last slide SHOULD be layout "conclusion"
4. Use varied layouts for visual interest
5. Keep bullet points concise (max 5-6 per slide)
6. Include realistic data for charts
7. Add helpful speaker notes
8. Make content professional and engaging
9. Return ONLY valid JSON, no markdown formatting"""

        if template_context:
            prompt += f"""

TEMPLATE CONTEXT:
- Color scheme: {template_context.get('colors', {})}
- Fonts: {template_context.get('fonts', {})}
- Style: Professional, Clean, Modern
- Target: Enterprise/Business audience"""
        
        return prompt
    
    def _build_user_prompt(
        self,
        prompt: str,
        real_time_data: Optional[str]
    ) -> str:
        """Build the user prompt with optional real-time data"""
        
        user_prompt = f"Create a professional presentation about: {prompt}"
        
        if real_time_data:
            user_prompt += f"""

REAL-TIME DATA TO INCORPORATE:
{real_time_data}

Use this current data to make the presentation relevant and up-to-date. Include statistics, trends, and facts from this data where appropriate."""
        
        return user_prompt
    
    def _get_fallback_content(self, prompt: str, num_slides: int) -> Dict:
        """Generate fallback content when LLM is not available"""
        
        slides = []
        
        # Title slide
        slides.append({
            "slide_number": 1,
            "layout": "title",
            "title": prompt[:60] + ("..." if len(prompt) > 60 else ""),
            "subtitle": "Professional Presentation",
            "content": {
                "main_text": "Generated presentation"
            },
            "speaker_notes": "Welcome and introduction"
        })
        
        # Content slides
        for i in range(2, num_slides):
            slides.append({
                "slide_number": i,
                "layout": "content",
                "title": f"Section {i - 1}",
                "content": {
                    "bullet_points": [
                        "Add your content here",
                        "Include key points and insights",
                        "Support with data and examples",
                        "Keep it concise and impactful"
                    ]
                },
                "speaker_notes": f"Discuss section {i - 1} points"
            })
        
        # Conclusion slide
        slides.append({
            "slide_number": num_slides,
            "layout": "conclusion",
            "title": "Thank You",
            "content": {
                "bullet_points": [
                    "Summary of key points",
                    "Call to action",
                    "Next steps",
                    "Questions & Discussion"
                ],
                "call_to_action": "Let's discuss how we can move forward together"
            },
            "speaker_notes": "Wrap up and open for questions"
        })
        
        return {
            "title": prompt[:60] if len(prompt) > 60 else prompt,
            "subtitle": "Generated Presentation",
            "author": "Presentation Architect",
            "date": datetime.now().strftime("%B %d, %Y"),
            "slides": slides
        }
    
    def _get_fallback_chart_data(self) -> Dict:
        """Return fallback chart data"""
        return {
            "chart_type": "bar",
            "title": "Sample Data",
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "datasets": [
                {
                    "name": "Series 1",
                    "values": [65, 78, 90, 85]
                }
            ],
            "x_axis_label": "Quarter",
            "y_axis_label": "Value"
        }
