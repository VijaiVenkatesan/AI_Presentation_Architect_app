from pptx import Presentation
from pptx.util import Inches
import json
import os

from core.template_parser import detect_layouts
from core.image_engine import generate_image
from core.diagram_engine import add_diagram
from utils.helpers import safe_json_load


def generate_ppt(template_file, content_json, output_file="output.pptx"):

    prs = Presentation(template_file)

    data = safe_json_load(content_json)
    slides_data = data.get("slides", [])

    layout_map = detect_layouts(prs)
    total = len(slides_data)

    for i, slide_data in enumerate(slides_data):

        try:
            # Slide type logic
            if i == 0:
                layout = layout_map["title"]
            elif i == 1:
                layout = layout_map["content"]
            elif i == total - 1:
                layout = layout_map["blank"]
            else:
                layout = layout_map["content"]

            slide = prs.slides.add_slide(layout)

            for shape in slide.shapes:
                if shape.has_text_frame:
                    tf = shape.text_frame
                    tf.clear()

                    if "title" in str(shape.placeholder_format.type).lower():
                        tf.text = slide_data.get("title", "")
                    else:
                        for b in slide_data.get("bullet_points", []):
                            p = tf.add_paragraph()
                            p.text = b

            # Image
            if slide_data.get("image_prompt"):
                img = generate_image(slide_data["image_prompt"])
                if img:
                    path = f"temp_{i}.png"
                    img.save(path)
                    slide.shapes.add_picture(path, Inches(1), Inches(4), width=Inches(4))
                    os.remove(path)

            # Diagram
            if slide_data.get("diagram_type"):
                add_diagram(slide, slide_data["diagram_type"])

        except Exception as e:
            print(f"Slide {i} failed: {e}")

    prs.save(output_file)
    return output_file
