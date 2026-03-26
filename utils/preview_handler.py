"""
Preview Handler Module
Generates slide previews
"""

import io
import base64
from typing import List, Dict, Optional
from PIL import Image, ImageDraw, ImageFont


class PreviewHandler:
    """Handles preview generation for presentations"""
    
    def __init__(self, template_data: Optional[Dict] = None):
        self.template_data = template_data or {
            'colors': {
                'background': '#0F172A',
                'primary': '#6366F1',
                'text_primary': '#F8FAFC',
                'text_secondary': '#94A3B8'
            }
        }
        self.slide_width = 1280
        self.slide_height = 720
    
    def generate_previews(self, content: Dict) -> List[Image.Image]:
        """Generate preview images for all slides"""
        previews = []
        slides = content.get('slides', [])
        
        for slide in slides:
            preview = self._generate_slide_preview(slide)
            previews.append(preview)
        
        return previews
    
    def _generate_slide_preview(self, slide_content: Dict) -> Image.Image:
        """Generate a preview image for a single slide"""
        bg_color = self._hex_to_rgb(self.template_data['colors']['background'])
        img = Image.new('RGB', (self.slide_width, self.slide_height), bg_color)
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
        
        layout = slide_content.get('layout', 'content')
        
        if layout == 'title':
            self._draw_title_slide(draw, slide_content, title_font, body_font)
        else:
            self._draw_content_slide(draw, slide_content, title_font, body_font)
        
        slide_num = slide_content.get('slide_number', 0)
        if slide_num > 0:
            draw.text(
                (self.slide_width - 50, self.slide_height - 40),
                str(slide_num),
                fill=self._hex_to_rgb(self.template_data['colors']['text_secondary']),
                font=body_font
            )
        
        return img
    
    def _draw_title_slide(self, draw, content, title_font, body_font):
        title = content.get('title', 'Presentation Title')
        subtitle = content.get('subtitle', '')
        
        draw.text((self.slide_width // 2 - 200, 280), title[:40], 
                  fill=self._hex_to_rgb(self.template_data['colors']['text_primary']), font=title_font)
        
        draw.rectangle([(self.slide_width // 2 - 100, 360), (self.slide_width // 2 + 100, 364)],
                       fill=self._hex_to_rgb(self.template_data['colors']['primary']))
        
        if subtitle:
            draw.text((self.slide_width // 2 - 150, 400), subtitle[:50],
                      fill=self._hex_to_rgb(self.template_data['colors']['text_secondary']), font=body_font)
    
    def _draw_content_slide(self, draw, content, title_font, body_font):
        title = content.get('title', '')
        
        draw.text((60, 40), title[:50], 
                  fill=self._hex_to_rgb(self.template_data['colors']['text_primary']), font=title_font)
        
        draw.rectangle([(60, 100), (260, 104)],
                       fill=self._hex_to_rgb(self.template_data['colors']['primary']))
        
        content_data = content.get('content', {})
        bullet_points = content_data.get('bullet_points', [])
        
        y_pos = 150
        for point in bullet_points[:6]:
            draw.text((80, y_pos), f"• {point[:60]}", 
                      fill=self._hex_to_rgb(self.template_data['colors']['text_primary']), font=body_font)
            y_pos += 50
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def image_to_base64(self, img: Image.Image) -> str:
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode()
