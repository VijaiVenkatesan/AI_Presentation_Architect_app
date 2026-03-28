import streamlit as st
from PIL import Image, ImageDraw

def generate_slide_preview(slides_data):
    """
    Generate simple preview images for slides
    (fast + works on Streamlit Cloud)
    """
    previews = []

    for slide in slides_data:
        img = Image.new("RGB", (800, 450), "white")
        draw = ImageDraw.Draw(img)

        # Title
        draw.text((20, 20), slide.get("title", ""), fill="black")

        # Bullets
        y = 80
        for b in slide.get("bullet_points", []):
            draw.text((40, y), f"- {b}", fill="black")
            y += 30

        previews.append(img)

    return previews


def show_preview(slides_data):
    previews = generate_slide_preview(slides_data)

    st.subheader("🖼 Slide Preview")

    cols = st.columns(2)

    for i, img in enumerate(previews):
        cols[i % 2].image(img, caption=f"Slide {i+1}")
