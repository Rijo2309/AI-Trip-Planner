import streamlit as st
from agent import generate_fast_plan
import re
import pandas as pd

# Set Page Config - Wide layout helps prevent the overlap seen in your mobile view screenshots
st.set_page_config(page_title="Rizzo | AI Trip Planner", layout="wide")

# ---------- Session State Initialization (Fixes AttributeError Line 144) ----------
if "plan" not in st.session_state:
    st.session_state.plan = None

# ---------- Advanced Custom Styling ----------
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
        border-bottom: 1px solid #334155;
        padding-bottom: 8px;
    }
    .timeline-item {
        padding: 12px 16px;
        border-left: 4px solid #3b82f6;
        background: #0f172a;
        border-radius: 0 12px 12px 0;
        margin: 12px 0;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Helper Functions ----------
def clean_text(text):
    # Aggressively removes artifacts like "---", "7)", and "..." seen in your images
    text = re.sub(r"^-+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\.+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+[\)\.]\s*", "", text, flags=re.MULTILINE)
    return text.strip()

def render_card(title, content, is_budget=False):
    content = clean_text(content)
    with st.container():
        # FIXED: Using triple quotes ensures line 89 does not cause a SyntaxError
        st.markdown(f"""
        <div class="card">
            <div class="section-title">{title}</div>
        """, unsafe_allow_html=True)
        
        st.markdown(content)
        
        if is_budget:
            # Extracts currency markers found in your Lucknow budget screenshot
            costs = re.findall(r"₹[\d,]+|[\d,]+\s?INR", content)
            if costs:
                st.markdown("---")
                st.table(pd.DataFrame({"Expense Item": ["Estimated"] * len(costs), "Amount": costs}))
                
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
        "budget": r"(budget|cost|expenses|safety tips|packing checklist)"
    }

    for line in lines:
        strip_line = line.strip()
        if not strip_line or strip_line.startswith("---"): continue
        
        lower_line = strip_line.lower()
        found_new = False
        for key, pattern in triggers.items():
            if re.search(pattern, lower_line):
                # FIXED: Logic to prevent "Day 2" from being sucked into the Food section
                if current == "day" and key == "food" and "guide" not in lower_line: continue
                current = key
                found_new = True
                break
        
        if found_new:
            if current == "day": sections[current] += f"\n### {strip_line}\n"
            continue
        sections[current] += line + "\n"
    return sections

# ---------- Sidebar ----------
with st.sidebar:
    st.title("🗺️ Rizzo Trip Planner")
    dest = st.text_input("Destination", placeholder="e.g. Lucknow")
    days = st.text_input("Days", placeholder="e.g. 2")
    budget_val = st.selectbox("Budget", ["Low", "Medium", "Luxury"])
    interests = st.text_input("Interests", placeholder="food, culture")
    generate = st.button("Generate Plan ⚡", use_container_width=True)

# ---------- Logic ----------
if generate:
    if not dest or not days:
        st.warning("Please fill in destination and days.")
    else:
        memory = {"destination": dest, "days": days, "budget": budget_val, "interests": interests}
        with st.spinner("Curating your plan..."):
            st.session_state.plan = generate_fast_plan(memory)

# Display results if the plan exists (Fixes the line 144 check)
if st.session_state.get("plan"):
    sections = split_sections(st.session_state.plan)
    
    # Organize content into Tabs for better UX (prevents the long scrolling issue)
    tab_itinerary, tab_logistics = st.tabs(["🗓 Itinerary", "🎒 Logistics & Budget"])
    
    with tab_itinerary:
        render_card("Trip Snapshot", sections["overview"])
        day_content = clean_text(sections["day"])
        for line in day_content.split("\n"):
            # Renders items with clock emojis or times in the styled timeline items
            if re.search(r"\d{1,2}:\d{2}", line) or "🕒" in line:
                st.markdown(f'<div class="timeline-item">{line}</div>', unsafe_allow_html=True)
            else:
                st.markdown(line)

    with tab_logistics:
        col1, col2 = st.columns(2)
        with col1:
            render_card("🍽 Food & Dining", sections["food"])
            render_card("🏨 Stay & Essentials", sections["stay"])
        with col2:
            render_card("🚕 Transport", sections["transport"])
            render_card("💸 Budget & Safety", sections["budget"], is_budget=True)

    # Dedicated Refinement Area for Follow-up details
    st.divider()
    st.subheader("🔄 Refine Your Plan")
    follow_up = st.text_area("Add preferences (e.g., 'I want more street food')", placeholder="Type here...")
    if st.button("Update Plan"):
        st.write("Updating with your preferences...")
