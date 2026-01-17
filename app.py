import streamlit as st
from agent import generate_fast_plan
import re
import pandas as pd

# Set Page Config
st.set_page_config(page_title="Rizzo | AI Trip Planner", layout="wide", initial_sidebar_state="expanded")

# ---------- Advanced Custom Styling ----------
st.markdown("""
<style>
    /* Main Background & Font */
    .main { background-color: #0f172a; }
    
    /* Modern Glassmorphism Cards */
    .card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        color: #f1f5f9;
        padding: 24px;
        border-radius: 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.2s ease;
    }
    .card:hover { border-color: #3b82f6; }
    
    .section-title {
        color: #60a5fa;
        font-weight: 800;
        font-size: 1.3rem;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Timeline Styles */
    .timeline-item {
        padding: 15px;
        border-left: 3px solid #3b82f6;
        background: rgba(15, 23, 42, 0.5);
        border-radius: 0 15px 15px 0;
        margin: 10px 0;
        font-size: 0.95rem;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] { background-color: #3b82f6 !important; color: white !important; }

    /* Hide standard Streamlit header/footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------- Helper Functions ----------
def clean_text(text):
    text = re.sub(r"^-+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\.+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+[\)\.]\s*", "", text, flags=re.MULTILINE)
    return text.strip()

def render_card(title, icon, content, is_budget=False):
    content = clean_text(content)
    with st.container():
        st.markdown(f"""
        <div class="card">
            <div class="section-title"><span>{icon}</span> {title}</div>
        """, unsafe_allow_html=True)
        
        st.markdown(content)
        
        if is_budget:
            costs = re.findall(r"₹[\d,]+|[\d,]+\s?INR", content)
            if costs:
                st.markdown("---")
                st.markdown("**Estimated Costs**")
                df = pd.DataFrame({"Category": ["Budget Item"] * len(costs), "Amount": costs})
                st.table(df)
        st.markdown('</div>', unsafe_allow_html=True)

def split_sections(text):
    sections = {"overview": "", "day": "", "stay": "", "food": "", "transport": "", "budget": ""}
    lines = text.split("\n")
    current = "overview"
    triggers = {
        "day": r"^(day\s*\d+|itinerary|daily plan)", 
        "stay": r"(where to stay|accommodation|hotel|packing list)",
        "food": r"(must-try dishes|dining guide|restaurant recommendations|food guide)",
        "transport": r"(transport|getting around|taxi/cab)",
        "budget": r"(budget|cost|expenses|safety tips)"
    }
    for line in lines:
        strip_line = line.strip()
        if not strip_line or strip_line.startswith("---"): continue
        found_new = False
        lower_line = strip_line.lower()
        for
