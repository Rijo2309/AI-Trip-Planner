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
        for key, pattern in triggers.items():
            if re.search(pattern, lower_line):
                if current == "day" and key == "food" and "guide" not in lower_line: continue
                current = key
                found_new = True
                break
        if found_new:
            if current == "day": sections[current] += f"\n### {strip_line}\n"
            continue
        sections[current] += line + "\n"
    return sections

# ---------- Sidebar Inputs ----------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/826/826070.png", width=80)
    st.title("Trip Settings")
    
    with st.container(border=True):
        dest = st.text_input("📍 Destination", placeholder="e.g. Lucknow, India")
        days = st.number_input("📅 Number of Days", min_value=1, max_value=30, value=2)
        budget = st.select_slider("💰 Budget Level", options=["Budget", "Value", "Luxury"])
    
    with st.expander("✨ Personalize"):
        interests = st.multiselect("Interests", ["Food", "History", "Culture", "Shopping", "Nature"], default=["Food"])
        style = st.radio("Pacing", ["Relaxed", "Balanced", "Packed"])

    generate = st.button("Generate My Plan ⚡", use_container_width=True, type="primary")

# ---------- Main Logic ----------
if generate:
    if not dest:
        st.error("Please provide a destination.")
    else:
        memory = {"destination": dest, "days": str(days), "budget": budget, "interests": ", ".join(interests), "style": style}
        with st.spinner("Analyzing top spots and local secrets..."):
            st.session_state.plan = generate_fast_plan(memory)

# ---------- Result Display ----------
if st.session_state.plan:
    sections = split_sections(st.session_state.plan)
    
    # 1. Header Snapshot
    st.markdown(f"# 🗺️ {dest.title()} Itinerary")
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Duration", f"{days} Days")
    col_b.metric("Budget", budget)
    col_c.metric("Style", style)

    # 2. Tabbed Content
    tab1, tab2 = st.tabs(["🗓 Daily Itinerary", "🎒 Travel Essentials"])

    with tab1:
        if sections["day"].strip():
            day_content = clean_text(sections["day"])
            for line in day_content.split("\n"):
                if re.search(r"\d{1,2}:\d{2}", line) or "🕒" in line or "Morning" in line or "Afternoon" in line:
                    st.markdown(f'<div class="timeline-item"><b>{line}</b></div>', unsafe_allow_html=True)
                elif "###" in line:
                    st.subheader(line.replace("###", ""))
                else:
                    st.write(line)

    with tab2:
        l_col, r_col = st.columns(2)
        with l_col:
            render_card("Food & Dining", "🍽️", sections["food"])
            render_card("Stay & Logistics", "🏨", sections["stay"])
        with r_col:
            render_card("Getting Around", "🚕", sections["transport"])
            render_card("Budget & Safety", "💸", sections["budget"], is_budget=True)

    # 3. Follow-up / Refinement Area
    st.write("---")
    st.subheader("🔄 Refine this plan?")
    refine_col1, refine_col2 = st.columns([3, 1])
    with refine_col1:
        refine_input = st.text_input("Mention changes (e.g. 'I'm vegetarian' or 'Visiting in Winter')", key="refine_input")
    with refine_col2:
        if st.button("Update Plan"):
            st.toast("Feature coming soon: Integrating refinement agent!")

else:
    # Landing State
    st.info("Enter your details in the sidebar and click **Generate** to create your visual trip guide.")
    st.markdown("""
    ### What you'll get:
    * **Optimized Timeline**: A minute-by-minute plan of your stay.
    * **Foodie Guide**: Local must-try dishes and restaurant picks.
    * **Logistics Support**: Transport hacks and budget estimations.
    """)
