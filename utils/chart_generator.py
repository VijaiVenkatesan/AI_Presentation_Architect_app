"""
Chart Generator Module
Creates various chart types for presentations
"""

import io
from typing import Dict, Optional
import plotly.graph_objects as go


class ChartGenerator:
    """Generates charts for PowerPoint presentations"""
    
    def __init__(self, color_scheme: Optional[Dict] = None):
        self.colors = ['#6366F1', '#8B5CF6', '#EC4899', '#10B981', '#F59E0B', '#EF4444', '#06B6D4', '#84CC16']
        if color_scheme:
            self.colors = color_scheme.get('colors', self.colors)
    
    def create_bar_chart(self, data: Dict, width: int = 800, height: int = 500) -> bytes:
        """Create a bar chart"""
        labels = data.get('labels', [])
        datasets = data.get('datasets', [])
        
        fig = go.Figure()
        
        for i, dataset in enumerate(datasets):
            fig.add_trace(go.Bar(
                name=dataset.get('name', f'Series {i+1}'),
                x=labels,
                y=dataset.get('values', []),
                marker_color=self.colors[i % len(self.colors)]
            ))
        
        fig.update_layout(
            title=data.get('title', ''),
            xaxis_title=data.get('x_axis_label', ''),
            yaxis_title=data.get('y_axis_label', ''),
            barmode='group',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            width=width,
            height=height
        )
        
        return fig.to_image(format='png', engine='kaleido')
    
    def create_line_chart(self, data: Dict, width: int = 800, height: int = 500) -> bytes:
        """Create a line chart"""
        labels = data.get('labels', [])
        datasets = data.get('datasets', [])
        
        fig = go.Figure()
        
        for i, dataset in enumerate(datasets):
            fig.add_trace(go.Scatter(
                name=dataset.get('name', f'Series {i+1}'),
                x=labels,
                y=dataset.get('values', []),
                mode='lines+markers',
                line=dict(color=self.colors[i % len(self.colors)], width=3),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            title=data.get('title', ''),
            xaxis_title=data.get('x_axis_label', ''),
            yaxis_title=data.get('y_axis_label', ''),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            width=width,
            height=height
        )
        
        return fig.to_image(format='png', engine='kaleido')
    
    def create_pie_chart(self, data: Dict, width: int = 700, height: int = 500) -> bytes:
        """Create a pie chart"""
        labels = data.get('labels', [])
        values = data.get('datasets', [{}])[0].get('values', [])
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=self.colors[:len(labels)]),
            textinfo='label+percent',
            textfont=dict(color='white')
        )])
        
        fig.update_layout(
            title=data.get('title', ''),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            width=width,
            height=height
        )
        
        return fig.to_image(format='png', engine='kaleido')
    
    def create_chart(self, chart_type: str, data: Dict, width: int = 800, height: int = 500) -> bytes:
        """Create a chart based on type"""
        creators = {
            'bar': self.create_bar_chart,
            'line': self.create_line_chart,
            'pie': self.create_pie_chart,
        }
        
        creator = creators.get(chart_type.lower(), self.create_bar_chart)
        return creator(data, width, height)
