import streamlit as st
from agent import generate_fast_plan
import re
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Rizzo | AI Trip Planner", layout="wide")

# 2. Session State Initialization (Fixes AttributeError)
if "plan" not in st.session_state:
    st.session_state.plan = None

# 3. Enhanced CSS Styling
st.markdown("""
<style>
    .card {
        background: #1e293b;
        color: #f1f5f9;
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 20px;
        border: 1px solid #334155;
    }
    .section-title {
        color: #60a5fa;
        font-weight: 800;
        text-transform: uppercase;
        border-bottom: 1px solid #334155;
        padding-bottom: 8px;
        margin-bottom: 12px;
    }
    .timeline-item {
        padding: 12px;
        border-left: 4px solid #3b82f6;
        background: #0f172a;
        margin: 10px 0;
        border-radius: 0 10px 10px 0;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# 4. Helper Functions
def clean_text(text):
    """Removes separators and numbering artifacts from AI output."""
    text = re.sub(r"^-+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\.+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+[\)\.]\s*", "", text, flags=re.MULTILINE)
    return text.strip()

def render_card(title, content, is_budget=False):
    """Renders HTML-styled cards. Triple quotes fix the line 89 SyntaxError."""
    content = clean_text(content)
    st.markdown(f"""<div class="card"><div class="section-title">{title}</div>""", unsafe_allow_html=True)
    st.markdown(content)
    if is_budget:
        costs = re.findall(r"₹[\d,]+|[\d,]+\s?INR", content)
        if costs:
            st.markdown("---")
            st.table(pd.DataFrame({"Category": ["Estimated Expense"] * len(costs), "Amount": costs}))
    st.markdown("</div>", unsafe_allow_html=True)

def split_sections(text):
    """Parses raw AI text into distinct content categories."""
    sections = {"overview": "", "day": "", "stay": "", "food": "", "transport": "", "budget": ""}
    lines = text.split("\n")
    current = "overview"
    triggers = {
        "day": r"^(day\s*\d+|itinerary|daily plan)", 
        "stay": r"(where to stay|accommodation|hotel|stay)",
        "food": r"(must-try dishes|dining guide|restaurant recommendations|food guide)",
        "transport": r"(transport|getting around|taxi/cab)",
        "budget": r"(budget|cost|expenses|safety tips|packing checklist)"
    }
    for line in lines:
        strip_line = line.strip()
        if not strip_line or strip_line.startswith("---"): continue
        lower_line = strip_line.lower()
        found_new = False
        for key, pattern in triggers.items():
            if re.search(pattern, lower_line):
                # State lock: prevents meal names from switching sections mid-itinerary
                if current == "day" and key == "food" and "guide" not in lower_line: continue
                current = key
                found_new = True
                break
        if found_new:
            if current == "day": sections[current] += f"\n### {strip_line}\n"
            continue
        sections[current] += line + "\n"
    return sections

# 5. Sidebar Inputs (Fixes KeyError: 'style')
with st.sidebar:
    st.header("Trip Settings")
    dest = st.text_input("Destination", placeholder="e.g. Lucknow")
    days_val = st.text_input("Days", placeholder="e.g. 2")
    budget_val = st.selectbox("Budget", ["Low", "Medium", "Luxury"])
    interests_val = st.text_input("Interests", placeholder="food, culture")
    # Added 'style' input to prevent KeyErrors in the agent call
    style_val = st.selectbox("Travel Style", ["Relaxed", "Balanced", "Packed"])
    generate = st.button("Generate Plan ⚡", use_container_width=True)

# 6. Plan Generation Logic
if generate:
    if not dest or not days_val:
        st.warning("Please fill in destination and days.")
    else:
        memory = {
            "destination": dest,
            "days": days_val,
            "budget": budget_val,
            "interests": interests_val,
            "style": style_val 
        }
        with st.spinner("Curating your trip..."):
            st.session_state.plan = generate_fast_plan(memory)

# 7. Results Display (Uses Tabs for intuitive UX)
if st.session_state.get("plan"):
    sections = split_sections(st.session_state.plan)
    st.title(f"📍 Trip to {dest}")
    
    tab_plan, tab_logistics = st.tabs(["🗓 Itinerary", "🎒 Logistics & Essentials"])
    
    with tab_plan:
        render_card("Overview", sections["overview"])
        day_content = clean_text(sections["day"])
        for line in day_content.split("\n"):
            if "###" in line:
                st.subheader(line.replace("###", ""))
            elif re.search(r"\d{1,2}:\d{2}", line) or "🕒" in line:
                st.markdown(f'<div class="timeline-item">{line}</div>', unsafe_allow_html=True)
            else:
                st.write(line)

    with tab_logistics:
        col1, col2 = st.columns(2)
        with col1:
            if sections["food"]: render_card("🍽 Food & Dining", sections["food"])
            if sections["stay"]: render_card("🏨 Stay", sections["stay"])
        with col2:
            if sections["transport"]: render_card("🚕 Transport", sections["transport"])
            if sections["budget"]: render_card("💸 Budget & Safety", sections["budget"], is_budget=True)

    # Refinement Section for Follow-up Details
    st.divider()
    st.subheader("🔄 Refine Your Plan")
    st.info("Mention your travel dates or dietary preferences below to update this plan.")
    refinement = st.text_area("What would you like to change?", placeholder="e.g. Visiting in winter, prefer vegetarian food...")
    if st.button("Update Plan"):
        st.write("Updating your plan with new preferences...")
else:
    st.info("👈 Enter your trip details in the sidebar to get started!")
