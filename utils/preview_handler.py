"""
Preview Handler Module - Uses Template Colors
Generates slide previews matching template styling
"""

import io
import base64
from typing import List, Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont


class PreviewHandler:
    """Handles preview generation with proper template colors"""
    
    def __init__(self, template_data: Optional[Dict] = None):
        # Use template colors if available, otherwise use light theme defaults
        if template_data and template_data.get('colors'):
            self.colors = template_data['colors']
        else:
            # Default to light theme (more common for business presentations)
            self.colors = {
                'background': '#FFFFFF',
                'primary': '#2563EB',
                'secondary': '#3B82F6',
                'accent': '#EF4444',
                'text_primary': '#1F2937',
                'text_secondary': '#6B7280'
            }
        
        # Get fonts from template
        if template_data and template_data.get('fonts'):
            self.fonts = template_data['fonts']
        else:
            self.fonts = {
                'title': {'name': 'Arial', 'size': 44},
                'subtitle': {'name': 'Arial', 'size': 28},
                'body': {'name': 'Arial', 'size': 18}
            }
        
        self.slide_width = 1280
        self.slide_height = 720
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        try:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except:
            return (255, 255, 255)
    
    def _is_dark_color(self, hex_color: str) -> bool:
        """Check if a color is dark"""
        r, g, b = self._hex_to_rgb(hex_color)
        # Calculate luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance < 0.5
    
    def _get_contrast_color(self, bg_hex: str) -> Tuple[int, int, int]:
        """Get a contrasting text color based on background"""
        if self._is_dark_color(bg_hex):
            return (255, 255, 255)  # White text on dark background
        else:
            return (31, 41, 55)  # Dark text on light background
    
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
        
        # Get background color
        bg_hex = self.colors.get('background', '#FFFFFF')
        bg_color = self._hex_to_rgb(bg_hex)
        
        # Create image with background
        img = Image.new('RGB', (self.slide_width, self.slide_height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Get text colors based on background
        title_color = self._get_contrast_color(bg_hex)
        body_color = self._get_contrast_color(bg_hex)
        
        # If template has specific text colors, use them
        if self.colors.get('text_primary'):
            title_color = self._hex_to_rgb(self.colors['text_primary'])
        if self.colors.get('text_secondary'):
            body_color = self._hex_to_rgb(self.colors.get('text_secondary', self.colors['text_primary']))
        
        # Get accent color for decorations
        accent_color = self._hex_to_rgb(self.colors.get('primary', '#2563EB'))
        
        # Load fonts
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        layout = slide_content.get('layout', 'content')
        
        # Draw based on layout
        if layout == 'title':
            self._draw_title_slide(draw, slide_content, title_font, body_font, title_color, body_color, accent_color)
        elif layout == 'quote':
            self._draw_quote_slide(draw, slide_content, title_font, body_font, title_color, body_color, accent_color)
        elif layout == 'conclusion':
            self._draw_conclusion_slide(draw, slide_content, title_font, body_font, title_color, body_color, accent_color)
        elif layout == 'chart':
            self._draw_chart_slide(draw, slide_content, title_font, body_font, title_color, body_color, accent_color)
        elif layout == 'two_column':
            self._draw_two_column_slide(draw, slide_content, title_font, body_font, title_color, body_color, accent_color)
        else:
            self._draw_content_slide(draw, slide_content, title_font, body_font, title_color, body_color, accent_color)
        
        # Add slide number
        slide_num = slide_content.get('slide_number', 0)
        if slide_num > 0:
            draw.text(
                (self.slide_width - 60, self.slide_height - 40),
                str(slide_num),
                fill=body_color,
                font=small_font
            )
        
        return img
    
    def _draw_title_slide(self, draw, content, title_font, body_font, title_color, body_color, accent_color):
        """Draw a title slide"""
        title = content.get('title', 'Presentation Title')
        subtitle = content.get('subtitle', '')
        
        # Center title
        try:
            title_bbox = draw.textbbox((0, 0), title[:50], font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
        except:
            title_width = 400
        
        title_x = (self.slide_width - title_width) // 2
        
        draw.text((title_x, 280), title[:50], fill=title_color, font=title_font)
        
        # Decorative line
        line_y = 360
        line_width = 200
        line_x = (self.slide_width - line_width) // 2
        draw.rectangle(
            [line_x, line_y, line_x + line_width, line_y + 4],
            fill=accent_color
        )
        
        # Subtitle
        if subtitle:
            try:
                sub_bbox = draw.textbbox((0, 0), subtitle[:60], font=body_font)
                sub_width = sub_bbox[2] - sub_bbox[0]
            except:
                sub_width = 300
            sub_x = (self.slide_width - sub_width) // 2
            draw.text((sub_x, 400), subtitle[:60], fill=body_color, font=body_font)
    
    def _draw_content_slide(self, draw, content, title_font, body_font, title_color, body_color, accent_color):
        """Draw a content slide"""
        title = content.get('title', '')
        
        # Title
        draw.text((60, 40), title[:60], fill=title_color, font=title_font)
        
        # Title underline
        draw.rectangle([60, 100, 300, 104], fill=accent_color)
        
        # Bullet points
        content_data = content.get('content', {})
        bullet_points = content_data.get('bullet_points', [])
        
        y_pos = 140
        for point in bullet_points[:7]:
            # Bullet
            draw.ellipse([70, y_pos + 8, 80, y_pos + 18], fill=accent_color)
            # Text
            draw.text((95, y_pos), point[:70], fill=body_color, font=body_font)
            y_pos += 50
    
    def _draw_chart_slide(self, draw, content, title_font, body_font, title_color, body_color, accent_color):
        """Draw a chart slide"""
        title = content.get('title', '')
        
        # Title
        draw.text((60, 40), title[:60], fill=title_color, font=title_font)
        draw.rectangle([60, 100, 300, 104], fill=accent_color)
        
        # Chart placeholder
        chart_x, chart_y = 100, 150
        chart_w, chart_h = self.slide_width - 200, 450
        
        # Chart background
        draw.rectangle(
            [chart_x, chart_y, chart_x + chart_w, chart_y + chart_h],
            outline=body_color,
            width=1
        )
        
        # Simple bar chart representation
        bar_width = 80
        bar_spacing = 100
        bars = [200, 280, 180, 320, 240, 300]
        colors = ['#6366F1', '#8B5CF6', '#EC4899', '#10B981', '#F59E0B', '#3B82F6']
        
        start_x = chart_x + 80
        for i, height in enumerate(bars):
            bar_x = start_x + (i * bar_spacing)
            bar_y = chart_y + chart_h - height - 30
            bar_color = self._hex_to_rgb(colors[i % len(colors)])
            draw.rectangle(
                [bar_x, bar_y, bar_x + bar_width, chart_y + chart_h - 30],
                fill=bar_color
            )
    
    def _draw_two_column_slide(self, draw, content, title_font, body_font, title_color, body_color, accent_color):
        """Draw a two-column slide"""
        title = content.get('title', '')
        
        # Title
        draw.text((60, 40), title[:60], fill=title_color, font=title_font)
        draw.rectangle([60, 100, 300, 104], fill=accent_color)
        
        # Divider
        mid_x = self.slide_width // 2
        draw.rectangle([mid_x - 1, 130, mid_x + 1, self.slide_height - 60], fill=body_color)
        
        # Left and right content
        content_data = content.get('content', {})
        
        left = content_data.get('left_column', [])
        right = content_data.get('right_column', [])
        
        y_pos = 160
        if isinstance(left, list):
            for item in left[:4]:
                draw.text((70, y_pos), f"• {item[:35]}", fill=body_color, font=body_font)
                y_pos += 45
        
        y_pos = 160
        if isinstance(right, list):
            for item in right[:4]:
                draw.text((mid_x + 30, y_pos), f"• {item[:35]}", fill=body_color, font=body_font)
                y_pos += 45
    
    def _draw_quote_slide(self, draw, content, title_font, body_font, title_color, body_color, accent_color):
        """Draw a quote slide"""
        content_data = content.get('content', {})
        quote = content_data.get('quote', 'Quote goes here')
        author = content_data.get('quote_author', '')
        
        # Large quote mark
        draw.text((100, 200), '"', fill=accent_color, font=title_font)
        
        # Quote text
        try:
            quote_bbox = draw.textbbox((0, 0), quote[:100], font=body_font)
            quote_width = quote_bbox[2] - quote_bbox[0]
        except:
            quote_width = 600
        
        x = (self.slide_width - min(quote_width, 900)) // 2
        draw.text((x, 300), quote[:100], fill=title_color, font=body_font)
        
        # Author
        if author:
            draw.text((self.slide_width - 300, 450), f"— {author}", fill=body_color, font=body_font)
    
    def _draw_conclusion_slide(self, draw, content, title_font, body_font, title_color, body_color, accent_color):
        """Draw a conclusion slide"""
        title = content.get('title', 'Thank You')
        
        # Center title
        try:
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
        except:
            title_width = 300
        
        x = (self.slide_width - title_width) // 2
        draw.text((x, 250), title, fill=title_color, font=title_font)
        
        # Decorative line
        line_x = (self.slide_width - 200) // 2
        draw.rectangle([line_x, 330, line_x + 200, 334], fill=accent_color)
        
        # Bullet points centered
        content_data = content.get('content', {})
        bullet_points = content_data.get('bullet_points', [])
        
        y_pos = 380
        for point in bullet_points[:4]:
            try:
                point_bbox = draw.textbbox((0, 0), point[:50], font=body_font)
                point_width = point_bbox[2] - point_bbox[0]
            except:
                point_width = 300
            x = (self.slide_width - point_width) // 2
            draw.text((x, y_pos), f"• {point[:50]}", fill=body_color, font=body_font)
            y_pos += 45
    
    def image_to_base64(self, img: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode()
