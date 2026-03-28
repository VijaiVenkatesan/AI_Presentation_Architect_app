import streamlit as st
import json

# Core modules
from core.db import init_db, save_project
from core.auth import login, signup
from core.groq_models import get_active_models
from core.content_engine import generate_content
from core.ppt_generator import generate_ppt
from core.editor_engine import render_editor
from core.pdf_export import export_pdf

# ---------------------------
# INIT DB
# ---------------------------
init_db()

st.set_page_config(layout="wide")

# ---------------------------
# SESSION INIT
# ---------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if "content" not in st.session_state:
    st.session_state.content = None

# ---------------------------
# LOGIN / SIGNUP
# ---------------------------
if not st.session_state.user:

    st.title("🔐 Login / Signup")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    # LOGIN
    if col1.button("Login"):
        if not u or not p:
            st.warning("Please enter username and password")
        else:
            success, result = login(u, p)

            if success:
                st.session_state.user = result
                st.success("Login successful ✅")
                st.rerun()
            else:
                st.error(result)

    # SIGNUP
    if col2.button("Signup"):
        if not u or not p:
            st.warning("Username & password required")
        else:
            success, msg = signup(u, p)

            if success:
                st.success("Signup successful 🎉 Now login")
            else:
                st.error(f"Signup failed: {msg}")

    st.stop()

# ---------------------------
# MAIN APP
# ---------------------------
st.title("🚀 Enterprise AI PPT Architect")

st.success(f"Logged in as: {st.session_state.user[1]}")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Controls")

    template = st.file_uploader("Upload PPT Template", type=["pptx"])

    slides = st.slider("Number of Slides", 1, 100, 10)

    models = get_active_models()
    model = st.selectbox("Select Model", models)

    if st.button("Reset Session"):
        st.session_state.content = None
        st.rerun()

# Prompt input
prompt = st.text_area("🧠 Enter Topic / Content")

# ---------------------------
# GENERATE CONTENT
# ---------------------------
if st.button("Generate Slides"):

    if not prompt:
        st.warning("Please enter a topic")
    else:
        with st.spinner("Generating slides using AI..."):
            try:
                content = generate_content(prompt, model, slides)
                st.session_state.content = content
                st.success("Slides generated successfully 🚀")
            except Exception as e:
                st.error(f"Generation failed: {e}")

# ---------------------------
# EDITOR + OUTPUT
# ---------------------------
if st.session_state.content:

    st.subheader("✏️ Edit Slides")

    try:
        edited_data = render_editor(st.session_state.content)
        st.session_state.content = json.dumps(edited_data)
    except Exception as e:
        st.error(f"Editor error: {e}")

    st.divider()

    col1, col2, col3 = st.columns(3)

    # ---------------------------
    # GENERATE PPT
    # ---------------------------
    if col1.button("📥 Generate PPT"):
        if not template:
            st.warning("Upload a template PPT first")
        else:
            with st.spinner("Building PPT..."):
                try:
                    file = generate_ppt(template, st.session_state.content)

                    with open(file, "rb") as f:
                        st.download_button(
                            "⬇️ Download PPT",
                            f,
                            file_name="generated.pptx"
                        )

                except Exception as e:
                    st.error(f"PPT generation failed: {e}")

    # ---------------------------
    # PDF EXPORT
    # ---------------------------
    if col2.button("📄 Download PDF"):
        try:
            pdf = export_pdf(st.session_state.content)

            with open(pdf, "rb") as f:
                st.download_button(
                    "⬇️ Download PDF",
                    f,
                    file_name="generated.pdf"
                )

        except Exception as e:
            st.error(f"PDF export failed: {e}")

    # ---------------------------
    # SAVE PROJECT
    # ---------------------------
    if col3.button("💾 Save Project"):
        try:
            save_project(st.session_state.user[0], st.session_state.content)
            st.success("Project saved successfully ✅")
        except Exception as e:
            st.error(f"Save failed: {e}")
