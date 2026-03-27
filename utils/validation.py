"""Slide validation"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class SlideValidator:
    REQUIRED = ['slide_number', 'layout', 'title', 'content']
    
    @staticmethod
    def validate_slides(slides: List[Dict[str, Any]]) -> Dict[str, Any]:
        errors, warnings = [], []
        for s in slides:
            sn = s.get('slide_number', '?')
            for f in SlideValidator.REQUIRED:
                if f not in s: errors.append(f"Slide {sn}: missing '{f}'")
            c = s.get('content', {})
            l = s.get('layout')
            if l == 'chart' and not c.get('chart'): warnings.append(f"Slide {sn}: chart layout but no chart data")
            if l == 'table' and not c.get('table'): warnings.append(f"Slide {sn}: table layout but no table data")
            if l == 'metrics' and not c.get('key_metrics'): warnings.append(f"Slide {sn}: metrics layout but no metrics")
            if l == 'image' and not c.get('image'): warnings.append(f"Slide {sn}: image layout but no image")
        return {'valid': len(errors)==0, 'errors': errors, 'warnings': warnings, 'total_slides': len(slides)}
