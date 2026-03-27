"""
PDF Generator Module
Converts presentation content to PDF format
"""

import io
from typing import Dict, List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage


class PDFGenerator:
    """Generates PDF from presentation content"""
    
    def __init__(self, template_data: Optional[Dict] = None):
        self.template_data = template_data or self._get_default_template()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _get_default_template(self) -> Dict:
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
                'title': {'name': 'Helvetica-Bold', 'size': 32, 'color': '#F8FAFC'},
                'subtitle': {'name': 'Helvetica', 'size': 20, 'color': '#94A3B8'},
                'body': {'name': 'Helvetica', 'size': 14, 'color': '#F8FAFC'}
            }
        }
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple (0-1 range)"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    
    def _hex_to_reportlab_color(self, hex_color: str):
        """Convert hex to reportlab color"""
        r, g, b = self._hex_to_rgb(hex_color)
        return colors.Color(r, g, b)
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        title_color = self._hex_to_reportlab_color(
            self.template_data['colors'].get('text_primary', '#F8FAFC')
        )
        self.styles.add(ParagraphStyle(
            name='SlideTitle',
            fontName='Helvetica-Bold',
            fontSize=32,
            textColor=title_color,
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        # Subtitle style
        subtitle_color = self._hex_to_reportlab_color(
            self.template_data['colors'].get('text_secondary', '#94A3B8')
        )
        self.styles.add(ParagraphStyle(
            name='SlideSubtitle',
            fontName='Helvetica',
            fontSize=20,
            textColor=subtitle_color,
            alignment=TA_CENTER,
            spaceAfter=15
        ))
        
        # Body style
        body_color = self._hex_to_reportlab_color(
            self.template_data['colors'].get('text_primary', '#F8FAFC')
        )
        self.styles.add(ParagraphStyle(
            name='SlideBody',
            fontName='Helvetica',
            fontSize=14,
            textColor=body_color,
            alignment=TA_LEFT,
            spaceAfter=10,
            leftIndent=20
        ))
        
        # Bullet style
        self.styles.add(ParagraphStyle(
            name='SlideBullet',
            fontName='Helvetica',
            fontSize=14,
            textColor=body_color,
            alignment=TA_LEFT,
            spaceAfter=8,
            leftIndent=40,
            bulletIndent=20
        ))
    
    def generate_pdf(self, content: Dict) -> io.BytesIO:
        """Generate PDF from presentation content"""
        output = io.BytesIO()
        
        # Create document with landscape orientation
        doc = SimpleDocTemplate(
            output,
            pagesize=landscape(LETTER),
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Build story (content)
        story = []
        slides = content.get('slides', [])
        
        for i, slide in enumerate(slides):
            # Add slide content
            slide_elements = self._create_slide_elements(slide)
            story.extend(slide_elements)
            
            # Add page break between slides (except last)
            if i < len(slides) - 1:
                story.append(PageBreak())
        
        # Build PDF
        try:
            doc.build(story, onFirstPage=self._add_background, onLaterPages=self._add_background)
        except Exception as e:
            print(f"Error building PDF: {e}")
            # Fallback to simple build
            doc.build(story)
        
        output.seek(0)
        return output
    
    def _add_background(self, canvas, doc):
        """Add background color to page"""
        try:
            bg_color = self._hex_to_reportlab_color(
                self.template_data['colors'].get('background', '#0F172A')
            )
            canvas.saveState()
            canvas.setFillColor(bg_color)
            canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=True, stroke=False)
            canvas.restoreState()
        except Exception as e:
            print(f"Error adding background: {e}")
    
    def _create_slide_elements(self, slide: Dict) -> List:
        """Create PDF elements for a single slide"""
        elements = []
        layout = slide.get('layout', 'content')
        
        # Add spacer at top
        elements.append(Spacer(1, 0.5*inch))
        
        # Create based on layout type
        if layout == 'title':
            elements.extend(self._create_title_slide(slide))
        elif layout == 'quote':
            elements.extend(self._create_quote_slide(slide))
        elif layout == 'conclusion':
            elements.extend(self._create_conclusion_slide(slide))
        else:
            elements.extend(self._create_content_slide(slide))
        
        return elements
    
    def _create_title_slide(self, slide: Dict) -> List:
        """Create title slide elements"""
        elements = []
        
        # Add vertical space to center content
        elements.append(Spacer(1, 2*inch))
        
        # Title
        title = slide.get('title', 'Presentation Title')
        elements.append(Paragraph(title, self.styles['SlideTitle']))
        
        # Subtitle
        subtitle = slide.get('subtitle', '')
        if subtitle:
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph(subtitle, self.styles['SlideSubtitle']))
        
        return elements
    
    def _create_content_slide(self, slide: Dict) -> List:
        """Create content slide elements"""
        elements = []
        
        # Title
        title = slide.get('title', '')
        if title:
            elements.append(Paragraph(title, self.styles['SlideTitle']))
            elements.append(Spacer(1, 0.3*inch))
        
        # Content
        content_data = slide.get('content', {})
        
        # Bullet points
        bullet_points = content_data.get('bullet_points', [])
        for point in bullet_points:
            bullet_text = f"• {point}"
            elements.append(Paragraph(bullet_text, self.styles['SlideBullet']))
        
        # Main text
        main_text = content_data.get('main_text', '')
        if main_text:
            elements.append(Paragraph(main_text, self.styles['SlideBody']))
        
        # Table
        table_info = content_data.get('table', {})
        if table_info:
            table_elements = self._create_table(table_info)
            if table_elements:
                elements.extend(table_elements)
        
        # Key metrics
        metrics = content_data.get('key_metrics', [])
        if metrics:
            elements.extend(self._create_metrics(metrics))
        
        return elements
    
    def _create_quote_slide(self, slide: Dict) -> List:
        """Create quote slide elements"""
        elements = []
        
        content_data = slide.get('content', {})
        quote = content_data.get('quote', '')
        author = content_data.get('quote_author', '')
        
        # Add vertical space
        elements.append(Spacer(1, 1.5*inch))
        
        # Quote
        quote_style = ParagraphStyle(
            name='Quote',
            fontName='Helvetica-Oblique',
            fontSize=24,
            textColor=self._hex_to_reportlab_color(
                self.template_data['colors'].get('text_primary', '#F8FAFC')
            ),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        elements.append(Paragraph(f'"{quote}"', quote_style))
        
        # Author
        if author:
            author_style = ParagraphStyle(
                name='QuoteAuthor',
                fontName='Helvetica',
                fontSize=16,
                textColor=self._hex_to_reportlab_color(
                    self.template_data['colors'].get('text_secondary', '#94A3B8')
                ),
                alignment=TA_RIGHT
            )
            elements.append(Paragraph(f"— {author}", author_style))
        
        return elements
    
    def _create_conclusion_slide(self, slide: Dict) -> List:
        """Create conclusion slide elements"""
        elements = []
        
        # Add vertical space
        elements.append(Spacer(1, 1.5*inch))
        
        # Title
        title = slide.get('title', 'Thank You')
        elements.append(Paragraph(title, self.styles['SlideTitle']))
        
        # Content
        content_data = slide.get('content', {})
        bullet_points = content_data.get('bullet_points', [])
        
        if bullet_points:
            elements.append(Spacer(1, 0.5*inch))
            for point in bullet_points:
                bullet_text = f"• {point}"
                centered_bullet = ParagraphStyle(
                    name='CenteredBullet',
                    fontName='Helvetica',
                    fontSize=14,
                    textColor=self._hex_to_reportlab_color(
                        self.template_data['colors'].get('text_primary', '#F8FAFC')
                    ),
                    alignment=TA_CENTER,
                    spaceAfter=8
                )
                elements.append(Paragraph(bullet_text, centered_bullet))
        
        return elements
    
    def _create_table(self, table_info: Dict) -> List:
        """Create table elements"""
        elements = []
        
        headers = table_info.get('headers', [])
        rows = table_info.get('rows', [])
        
        if not headers:
            return elements
        
        # Build table data
        table_data = [headers] + rows
        
        # Create table
        table = Table(table_data, repeatRows=1)
        
        # Style table
        primary_color = self._hex_to_reportlab_color(
            self.template_data['colors'].get('primary', '#6366F1')
        )
        text_color = self._hex_to_reportlab_color(
            self.template_data['colors'].get('text_primary', '#F8FAFC')
        )
        bg_color = self._hex_to_reportlab_color('#1E293B')
        
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), bg_color),
            ('TEXTCOLOR', (0, 1), (-1, -1), text_color),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.2, 0.2, 0.3)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ])
        
        table.setStyle(style)
        
        elements.append(Spacer(1, 0.3*inch))
        elements.append(table)
        
        return elements
    
    def _create_metrics(self, metrics: List[Dict]) -> List:
        """Create metrics display"""
        elements = []
        
        # Create metrics as a table
        metric_data = []
        values_row = []
        labels_row = []
        
        for metric in metrics[:4]:
            values_row.append(str(metric.get('value', '')))
            labels_row.append(metric.get('label', ''))
        
        if values_row:
            metric_data = [values_row, labels_row]
            
            table = Table(metric_data, colWidths=[2*inch] * len(values_row))
            
            accent_color = self._hex_to_reportlab_color(
                self.template_data['colors'].get('accent', '#EC4899')
            )
            text_color = self._hex_to_reportlab_color(
                self.template_data['colors'].get('text_secondary', '#94A3B8')
            )
            
            style = TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 28),
                ('TEXTCOLOR', (0, 0), (-1, 0), accent_color),
                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, 1), 12),
                ('TEXTCOLOR', (0, 1), (-1, 1), text_color),
                ('TOPPADDING', (0, 0), (-1, -1), 15),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ])
            
            table.setStyle(style)
            
            elements.append(Spacer(1, 0.5*inch))
            elements.append(table)
        
        return elements
