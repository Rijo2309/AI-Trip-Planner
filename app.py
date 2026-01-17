import streamlit as st
from agent import generate_fast_plan
import re
import pandas as pd

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
    .card ul {
        margin-left: 20px;
    }
    /* Style for the budget table */
    .stDataFrame {
        background: #0f172a;
        border-radius: 8px;
        padding: 10px;
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
    days = st.text_input("Days", placeholder="e.g. 2")
    budget_val = st.selectbox("Budget", ["Low💲", "Medium 💲💲", "Luxury 💲💲💲"])
    interests = st.text_input("Interests", placeholder="food, culture, history")
    style = st.selectbox("Travel style", ["Relaxed", "Balanced", "Packed"])
    generate = st.button("Generate Plan ⚡", use_container_width=True)

# ---------- Session ----------
if "plan" not in st.session_state:
    st.session_state.plan = None

# ---------- Improved Helpers ----------
def clean_text(text):
    # Remove separators like "---" or "..." visible in images
    text = re.sub(r"^-+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\.+$", "", text, flags=re.MULTILINE)
    # Remove leading numbers like "7)" or "3)" from your screenshots
    text = re.sub(r"^\d+[\)\.]\s*", "", text, flags=re.MULTILINE)
    return text.strip()

def card(title, content, is_budget=False):
    content = clean_text(content)
    with st.container():
        st.markdown(f"""
        <div class="card">
            <div class="section-title">{title}</div>
        """, unsafe_allow_html=True)
        
        st.markdown(content)
        
        # Insert the Budget Table if requested
        if is_budget:
            st.markdown("
