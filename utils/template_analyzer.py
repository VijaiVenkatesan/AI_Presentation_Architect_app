"""
Template Analyzer Module
Extracts styling, layout, and design elements from uploaded templates
"""

import io
import re
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image
import numpy as np
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE_TYPE
from collections import Counter
import colorsys


class TemplateAnalyzer:
    """Analyzes PowerPoint templates and images to extract styling information"""
    
    def __init__(self):
        self.template_data = self._get_default_template()
    
    def _get_default_template(self) -> Dict:
        """Return default template settings"""
        return {
            'colors': {
                'primary': '#6366F1',
                'secondary': '#8B5CF6',
                'accent': '#EC4899',
                'background': '#0F172A',
                'text_primary': '#F8FAFC',
                'text_secondary': '#94A3B8'
            },
            'fonts': {
                'title': {'name': 'Arial', 'size': 44, 'bold': True},
                'subtitle': {'name': 'Arial', 'size': 28, 'bold': False},
                'body': {'name': 'Arial', 'size': 18, 'bold': False},
                'caption': {'name': 'Arial', 'size': 12, 'bold': False}
            },
            'layouts': [],
            'slide_size': {'width': 13.333, 'height': 7.5},
            'has_logo': False,
            'logo_position': None,
            'chart_styles': {},
            'shape_styles': {},
            'master_layouts': []
        }
    
    def analyze_pptx(self, pptx_file: io.BytesIO) -> Dict[str, Any]:
        """Analyze a PowerPoint file and extract template information"""
        try:
            prs = Presentation(pptx_file)
            
            # Extract slide size
            self.template_data['slide_size'] = {
                'width': prs.slide_width.inches,
                'height': prs.slide_height.inches
            }
            
            # Analyze slides
            colors = []
            fonts = []
            layouts = []
            
            for slide_idx, slide in enumerate(prs.slides):
                slide_analysis = self._analyze_slide(slide, slide_idx)
                colors.extend(slide_analysis['colors'])
                fonts.extend(slide_analysis['fonts'])
                layouts.append(slide_analysis['layout'])
            
            # Process extracted data
            self._process_colors(colors)
            self._process_fonts(fonts)
            self.template_data['layouts'] = layouts
            
            return self.template_data
            
        except Exception as e:
            print(f"Error analyzing PPTX: {e}")
            return self.template_data
    
    def analyze_image(self, image_file: io.BytesIO) -> Dict[str, Any]:
        """Analyze an image (screenshot) of a slide to extract styling"""
        try:
            image = Image.open(image_file)
            
            # Extract dominant colors
            colors = self._extract_colors_from_image(image)
            self._process_colors(colors)
            
            return self.template_data
            
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return self.template_data
    
    def _analyze_slide(self, slide, slide_idx: int) -> Dict[str, Any]:
        """Analyze a single slide"""
        analysis = {
            'colors': [],
            'fonts': [],
            'layout': {
                'slide_index': slide_idx,
                'shapes': [],
                'has_title': False,
                'has_content': False,
                'has_chart': False,
                'has_table': False,
                'has_image': False
            }
        }
        
        for shape in slide.shapes:
            shape_info = self._analyze_shape(shape)
            analysis['layout']['shapes'].append(shape_info)
            
            if shape_info.get('fill_color'):
                analysis['colors'].append(shape_info['fill_color'])
            if shape_info.get('text_color'):
                analysis['colors'].append(shape_info['text_color'])
            if shape_info.get('font'):
                analysis['fonts'].append(shape_info['font'])
            
            if shape_info['type'] == 'title':
                analysis['layout']['has_title'] = True
            elif shape_info['type'] == 'text':
                analysis['layout']['has_content'] = True
            elif shape_info['type'] == 'chart':
                analysis['layout']['has_chart'] = True
            elif shape_info['type'] == 'table':
                analysis['layout']['has_table'] = True
            elif shape_info['type'] == 'picture':
                analysis['layout']['has_image'] = True
        
        return analysis
    
    def _analyze_shape(self, shape) -> Dict[str, Any]:
        """Analyze a single shape"""
        shape_info = {
            'type': 'unknown',
            'left': shape.left.inches if shape.left else 0,
            'top': shape.top.inches if shape.top else 0,
            'width': shape.width.inches if shape.width else 0,
            'height': shape.height.inches if shape.height else 0
        }
        
        if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
            shape_info['type'] = 'picture'
        elif shape.shape_type == MSO_SHAPE_TYPE.CHART:
            shape_info['type'] = 'chart'
        elif shape.shape_type == MSO_SHAPE_TYPE.TABLE:
            shape_info['type'] = 'table'
        elif hasattr(shape, 'text_frame'):
            shape_info['type'] = 'text'
            text_info = self._analyze_text_frame(shape.text_frame)
            shape_info.update(text_info)
            
            if hasattr(shape, 'placeholder_format'):
                ph_type = str(shape.placeholder_format.type)
                if 'TITLE' in ph_type:
                    shape_info['type'] = 'title'
        
        return shape_info
    
    def _analyze_text_frame(self, text_frame) -> Dict[str, Any]:
        """Analyze text frame for font and color information"""
        result = {}
        
        if not text_frame.paragraphs:
            return result
        
        for paragraph in text_frame.paragraphs:
            if not paragraph.runs:
                continue
            
            for run in paragraph.runs:
                font = run.font
                
                font_info = {
                    'name': font.name if font.name else 'Arial',
                    'size': font.size.pt if font.size else 18,
                    'bold': font.bold if font.bold is not None else False,
                    'italic': font.italic if font.italic is not None else False
                }
                result['font'] = font_info
                
                if font.color and font.color.rgb:
                    result['text_color'] = self._rgb_to_hex(font.color.rgb)
                
                break
            break
        
        return result
    
    def _extract_colors_from_image(self, image: Image.Image) -> List[str]:
        """Extract dominant colors from an image"""
        image = image.resize((150, 150))
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        pixels = list(image.getdata())
        
        color_counts = Counter()
        for pixel in pixels:
            rounded = (pixel[0] // 32 * 32, pixel[1] // 32 * 32, pixel[2] // 32 * 32)
            color_counts[rounded] += 1
        
        top_colors = color_counts.most_common(10)
        hex_colors = [self._rgb_tuple_to_hex(color) for color, count in top_colors]
        
        return hex_colors
    
    def _process_colors(self, colors: List[str]):
        """Process extracted colors and determine color scheme"""
        if not colors:
            return
        
        valid_colors = [c for c in colors if c and re.match(r'^#[0-9A-Fa-f]{6}$', c)]
        
        if not valid_colors:
            return
        
        color_counts = Counter(valid_colors)
        sorted_colors = [color for color, _ in color_counts.most_common(6)]
        
        dark_colors = []
        light_colors = []
        mid_colors = []
        
        for color in sorted_colors:
            lightness = self._get_lightness(color)
            if lightness < 0.3:
                dark_colors.append(color)
            elif lightness > 0.7:
                light_colors.append(color)
            else:
                mid_colors.append(color)
        
        if dark_colors:
            self.template_data['colors']['background'] = dark_colors[0]
        if light_colors:
            self.template_data['colors']['text_primary'] = light_colors[0]
        if mid_colors:
            self.template_data['colors']['primary'] = mid_colors[0]
            if len(mid_colors) > 1:
                self.template_data['colors']['secondary'] = mid_colors[1]
            if len(mid_colors) > 2:
                self.template_data['colors']['accent'] = mid_colors[2]
    
    def _process_fonts(self, fonts: List[Dict]):
        """Process extracted fonts"""
        if not fonts:
            return
        
        large_fonts = [f for f in fonts if f.get('size', 0) >= 36]
        medium_fonts = [f for f in fonts if 24 <= f.get('size', 0) < 36]
        small_fonts = [f for f in fonts if f.get('size', 0) < 24]
        
        if large_fonts:
            self.template_data['fonts']['title'] = large_fonts[0]
        if medium_fonts:
            self.template_data['fonts']['subtitle'] = medium_fonts[0]
        if small_fonts:
            self.template_data['fonts']['body'] = small_fonts[0]
    
    def _rgb_to_hex(self, rgb: RGBColor) -> str:
        """Convert RGBColor to hex string"""
        try:
            return f'#{rgb.red:02X}{rgb.green:02X}{rgb.blue:02X}'
        except:
            return '#000000'
    
    def _rgb_tuple_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex string"""
        return f'#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}'
    
    def _get_lightness(self, hex_color: str) -> float:
        """Get lightness value of a hex color (0-1)"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255
        
        _, lightness, _ = colorsys.rgb_to_hls(r, g, b)
        return lightness
    
    def get_template_summary(self) -> str:
        """Generate a summary of the analyzed template"""
        summary = []
        summary.append("## Template Analysis Summary\n")
        
        summary.append("### Colors")
        for name, color in self.template_data['colors'].items():
            summary.append(f"- {name}: {color}")
        
        summary.append("\n### Fonts")
        for name, font in self.template_data['fonts'].items():
            summary.append(f"- {name}: {font['name']} {font['size']}pt")
        
        return "\n".join(summary)
