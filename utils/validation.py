"""Slide validation - Fixed to handle various data types"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class SlideValidator:
    REQUIRED = ['slide_number', 'layout', 'title', 'content']
    
    @staticmethod
    def validate_slides(slides: List[Dict[str, Any]]) -> Dict[str, Any]:
        errors, warnings = [], []
        
        for s in slides:
            if not isinstance(s, dict):
                errors.append(f"Slide: not a dictionary (got {type(s).__name__})")
                continue
            
            sn = s.get('slide_number', '?')
            
            # Check required fields
            for f in SlideValidator.REQUIRED:
                if f not in s:
                    errors.append(f"Slide {sn}: missing '{f}'")
            
            # Get content safely
            content = s.get('content', {})
            if not isinstance(content, dict):
                # Try to convert or warn
                logger.warning(f"Slide {sn}: content is {type(content).__name__}, not dict")
                content = {}  # Reset to empty dict for validation
                warnings.append(f"Slide {sn}: invalid content format")
            
            layout = s.get('layout', 'content')
            
            # Layout-specific validation
            if layout == 'chart':
                chart = content.get('chart', {})
                if not chart or not isinstance(chart, dict):
                    warnings.append(f"Slide {sn}: chart layout but no chart data")
            
            if layout == 'table':
                table = content.get('table', {})
                if not table or not isinstance(table, dict):
                    warnings.append(f"Slide {sn}: table layout but no table data")
            
            if layout == 'metrics':
                metrics = content.get('key_metrics', [])
                if not metrics or not isinstance(metrics, list):
                    warnings.append(f"Slide {sn}: metrics layout but no metrics")
            
            if layout == 'image':
                img = content.get('image', '')
                if not img:
                    warnings.append(f"Slide {sn}: image layout but no image")
            
            if layout == 'quote':
                quote = content.get('quote', '')
                if not quote:
                    warnings.append(f"Slide {sn}: quote layout but no quote text")
            
            if layout == 'two_column':
                left = content.get('left_column', '')
                right = content.get('right_column', '')
                if not left and not right:
                    warnings.append(f"Slide {sn}: two_column layout but both columns empty")
            
            if layout == 'timeline':
                items = content.get('timeline_items', [])
                if not items or not isinstance(items, list):
                    warnings.append(f"Slide {sn}: timeline layout but no timeline items")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'total_slides': len(slides)
        }
