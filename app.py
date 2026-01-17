import streamlit as st
from agent import generate_fast_plan
import re

st.set_page_config(page_title="Rizzo, Your Trip Planner", layout="centered")

# ---------- Improved Styling ----------
st.markdown("""
<style>
    .card {
        background: #1e293b;
        color: #f1f5f9;
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 20px;
        border: 1px solid #334155;
        line-height: 1.6;
    }
    .section-title {
        color: #60a5fa;
        font-weight: 800;
        font-size: 1.2rem;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-bottom: 1px solid #334155;
        padding-bottom: 8px;
    }
    .timeline-item {
        padding: 12px 16px;
        border-left: 4px solid #3b82f6;
        background: #0f172a;
        border-radius: 0 12px 12px 0;
        margin: 12px 0;
        font-family: monospace;
    }
    /* Fix for list spacing inside cards */
    .card ul {
        margin-left: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Title ----------
st.title("🌍 Your AI Trip Planner")
st.caption("Fast • Visual • Efficient")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Your Trip")
    destination = st.text_input("Destination", placeholder="e.g. Lucknow, India")
    days = st.text_input("Days", placeholder="e.g. 3")
    budget = st.selectbox("Budget", ["Low💲", "Medium 💲💲", "Luxury 💲💲💲"])
    interests = st.text_input("Interests", placeholder="food, culture, history")
    style = st.selectbox("Travel style", ["Relaxed", "Balanced", "Packed"])
    generate = st.button("Generate Plan ⚡", use_container_width=True)

# ---------- Session ----------
if "plan" not in st.session_state:
    st.session_state.plan = None

# ---------- Generate ----------
if generate:
    if not destination or not days:
        st.warning("Please enter a destination and number of days.")
    else:
        memory = {
            "destination": destination,
            "days": days,
            "budget": budget,
            "interests": interests,
            "style": style
        }
        with st.spinner("Curating your perfect itinerary..."):
            st.session_state.plan = generate_fast_plan(memory)

# ---------- Improved Helpers ----------
def clean_text(text):
    # Remove weird artifacts like "---" or "7)" at the start of lines
    text = re.sub(r"^-+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+[\)\.]\s*", "", text, flags=re.MULTILINE)
    # We keep ** for bolding and # for structure now
    return text.strip()

def card(title, content):
    content = clean_text(content)
    # Use st.markdown INSIDE the div wrapper for proper rendering
    st.markdown(f"""
    <div class="card">
        <div class="section-title">{title}</div>
    """, unsafe_allow_html=True)
    st.markdown(content) # This allows Streamlit to handle bullet points and bolding
    st.markdown('</div>', unsafe_allow_html=True)

def split_sections(text):
    sections = {"overview": "", "day": "", "stay": "", "food": "", "transport": "", "budget": ""}
    lines = text.split("\n")
    current = "overview"
