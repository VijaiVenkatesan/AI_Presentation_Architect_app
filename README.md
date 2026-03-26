# 🎯 AI Presentation Architect

Enterprise-level AI-powered PowerPoint presentation generator with template matching, real-time data integration, and advanced editing capabilities.

## Features

- 📁 **Template Analysis**: Upload PPTX or images to extract styling
- 🤖 **AI Content Generation**: Multiple Groq LLM models with real-time selection
- 🔍 **Real-time Data**: Integrate current web data into presentations
- 📊 **Smart Charts**: Auto-generate charts, tables, and diagrams
- ✏️ **Live Editor**: Edit slides with real-time preview
- 💾 **Export Options**: Download as PPTX or PDF

## Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Add your Groq API key to `.streamlit/secrets.toml`
4. Run: `streamlit run app.py`

## Deployment

### Streamlit Cloud
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Add `GROQ_API_KEY` to secrets

### Vercel
1. Use the Streamlit adapter
2. Configure environment variables

## License

MIT License
