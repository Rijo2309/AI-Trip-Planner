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
            st.markdown("---")
            st.markdown("**Estimated Cost Breakdown**")
            # Logic to extract numbers from text could be complex, 
            # so we provide a clean manual input template or a parsed table
            costs = re.findall(r"₹[\d,]+|[\d,]+\s?INR", content)
            if costs:
                df = pd.DataFrame({
                    "Item": ["Est. Expense" for _ in costs],
                    "Amount": costs
                })
                st.table(df)
                
        st.markdown('</div>', unsafe_allow_html=True)

def split_sections(text):
    sections = {"overview": "", "day": "", "stay": "", "food": "", "transport": "", "budget": ""}
    lines = text.split("\n")
    current = "overview"

    # Triggers optimized for your screenshots to prevent "Day 2" in "Food"
    triggers = {
        "day": r"^(day\s*\d+|itinerary|daily plan)", 
        "stay": r"(where to stay|accommodation|hotel|packing list)",
        "food": r"(must-try dishes|dining guide|restaurant recommendations|food guide)",
        "transport": r"(transport|getting around|taxi/cab)",
        "budget": r"(budget|cost|expenses|safety tips)"
    }

    for line in lines:
        strip_line = line.strip()
        if not strip_line or strip_line.startswith("---"):
            continue

        found_new_section = False
        lower_line = strip_line.lower()
        
        for key, pattern in triggers.items():
            if re.search(pattern, lower_line):
                # Lock 'day' state: Prevents meal names from triggering section changes
                if current == "day" and key == "food" and not any(x in lower_line for x in ["guide", "essentials"]):
                    continue
                current = key
                found_new_section = True
                break
        
        if found_new_section:
            if current == "day":
                sections[current] += f"\n### {strip_line}\n"
            continue

        sections[current] += line + "\n"
    return sections

# ---------- Main Logic ----------
if generate:
    if not destination or not days:
        st.warning("Please enter a destination and days.")
    else:
        memory = {"destination": destination, "days": days, "budget": budget_val, "interests": interests, "style": style}
        with st.spinner("Curating your trip..."):
            st.session_state.plan = generate_fast_plan(memory)

if st.session_state.plan:
    sections = split_sections(st.session_state.plan)

    # 1. Overview
    with st.expander("🧭 Trip Snapshot", expanded=True):
        card("Snapshot", f"**{destination}** | {days} Days | {budget_val}\n\n" + sections["overview"])

    # 2. Itinerary (Fixes Day 1/Day 2 split)
    if sections["day"].strip():
        with st.expander("🗓 Itinerary", expanded=True):
            day_content = clean_text(sections["day"])
            for line in day_content.split("\n"):
                if re.search(r"\d{1,2}:\d{2}", line) or "🕒" in line:
                    st.markdown(f'<div class="timeline-item">{line}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(line)

    # 3. Logistics Grid (Fixes Budget overlap/missing issue)
    col1, col2 = st.columns(2)
    with col1:
        if sections["food"].strip():
            card("🍽 Food & Dining", sections["food"])
        if sections["stay"].strip():
            card("🏨 Stay & Essentials", sections["stay"])
    with col2:
        if sections["transport"].strip():
            card("🚕 Transport", sections["transport"])
        if sections["budget"].strip():
            card("💸 Budget & Safety", sections["budget"], is_budget=True)
