"""Slide validation and quality checks"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class SlideValidator:
    """Validates slide data before generation/export"""
    
    REQUIRED_FIELDS = ['slide_number', 'layout', 'title', 'content']
    
    @staticmethod
    def validate_slides(slides: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate all slides and return validation report"""
        errors = []
        warnings = []
        
        for slide in slides:
            slide_num = slide.get('slide_number', 'Unknown')
            layout = slide.get('layout', 'content')
            
            for field in SlideValidator.REQUIRED_FIELDS:
                if field not in slide:
                    errors.append(f"Slide {slide_num}: Missing required field '{field}'")
            
            content = slide.get('content', {})
            
            if layout == 'chart' and not content.get('chart'):
                warnings.append(f"Slide {slide_num}: Chart layout but missing chart data")
            
            if layout == 'table' and not content.get('table'):
                warnings.append(f"Slide {slide_num}: Table layout but no table data")
            
            if layout == 'metrics' and not content.get('key_metrics'):
                warnings.append(f"Slide {slide_num}: Metrics layout but no metrics data")
            
            if layout == 'image' and not content.get('image'):
                warnings.append(f"Slide {slide_num}: Image layout but no image data")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'total_slides': len(slides)
        }
