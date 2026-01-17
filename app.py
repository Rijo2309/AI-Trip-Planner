import streamlit as st
from agent import generate_fast_plan
import re
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Rizzo | AI Trip Planner", layout="wide")

# 2. Session State Initialization (Fixes AttributeError)
if "plan" not in st.session_state:
    st.session_state.plan = None

# 3. Modern & Concise UI Styling
st.markdown("""
<style>
    .day-container {
        background: #1e293b;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 25px;
        color: #f1f5f9;
    }
    .time-slot {
        color: #60a5fa;
        font-weight: 800;
        text-transform: uppercase;
        font-size: 0.85rem;
        margin-top: 15px;
        display: block;
        letter-spacing: 0.5px;
    }
    .card {
        background: #0f172a;
        padding: 18px;
        border-radius: 10px;
        border: 1px solid #334155;
        margin-bottom: 15px;
        color: #f1f5f9;
    }
    .section-header {
        color: #94a3b8;
        font-size: 0.75rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 12px;
        border-bottom: 1px solid #1e293b;
        padding-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# 4. Logic: Intelligent Text Splitting
def get_itinerary_days(text):
    """Splits full text into separate blocks for each Day found."""
    # Detects Day 1, Day 2, etc. and splits text
    days = re.split(r'(Day\s*\d+[:\s\-]*)', text)
    day_list = []
    if len(days) > 1:
        for i in range(1, len(days), 2):
            header = days[i].strip()
            content = days[i+1] if (i+1) < len(days) else ""
            # Stop day content if it runs into other logistics headers
            content = re.split(r'(Food|Logistics|Transport|Stay|Budget)', content)[0]
            day_list.append((header, content.strip()))
    return day_list

def extract_section(text, section_name):
    """Extracts specific logistics sections using regex."""
    pattern = rf"{section_name}.*?:?(.*?)(?=(Food|Logistics|Transport|Stay|Budget|Day\s*\d|$))"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else "No specific details provided."

# 5. Sidebar Navigation
with st.sidebar:
    st.title("🗺️ Rizzo Planner")
    dest = st.text_input("Destination", placeholder="e.g. Paris")
    days_val = st.number_input("Days", min_value=1, max_value=10, value=3)
    budget = st.selectbox("Budget", ["Budget 💲", "Balanced 💲💲", "Luxury 💲💲💲"])
    style = st.selectbox("Travel Style", ["Relaxed", "Balanced", "Packed"])
    interests = st.text_input("Interests", placeholder="Food, Art, Hidden Gems")
    
    generate = st.button("Generate Plan ⚡", use_container_width=True, type="primary")

# 6. Generation Trigger
if generate:
    if not dest:
        st.error("Please enter a destination!")
    else:
        # Style and interests are passed to agent to ensure concise output
        memory = {
            "destination": dest, 
            "days": str(days_val), 
            "budget": budget, 
            "style": style, 
            "interests": interests
        }
        with st.spinner(f"Curating your {days_val}-day trip to {dest}..."):
            st.session_state.plan = generate_fast_plan(memory)

# 7. Main Display (Fixes cut-off and visual clutter)
if st.session_state.plan:
    full_text = st.session_state.plan
    
    # Use tabs to separate the detailed daily schedule from logistics
    tab_itinerary, tab_logistics = st.tabs(["🗓 Daily Itinerary", "🎒 Logistics & Essentials"])

    with tab_itinerary:
        st.markdown(f"## 📍 {dest.title()}")
        
        # Display Overview/Snapshot
        overview = extract_section(full_text, "Overview")
        if overview:
            st.info(overview)

        # Process and Display ALL Days (Fixes Day 2/3 missing issue)
        itinerary_data = get_itinerary_days(full_text)
        
        if itinerary_data:
            for header, content in itinerary_data:
                # Formatting time blocks for high scannability
                formatted = content.replace("Morning:", '<span class="time-slot">🕒 Morning</span>')
                formatted = formatted.replace("Afternoon:", '<span class="time-slot">☀️ Afternoon</span>')
                formatted = formatted.replace("Evening:", '<span class="time-slot">🌙 Evening</span>')
                
                st.markdown(f"""
                <div class="day-container">
                    <h3 style='margin:0;'>{header}</h3>
                    <div style='margin-top:10px;'>{formatted}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Fallback if text format is unexpected
            st.markdown(full_text)

    with tab_logistics:
        l_col, r_col = st.columns(2)
        
        with l_col:
            st.markdown('<div class="card"><div class="section-header">🍽 Food & Dining</div>', unsafe_allow_html=True)
            st.write(extract_section(full_text, "Food"))
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="card"><div class="section-header">🏨 Recommended Stay</div>', unsafe_allow_html=True)
            st.write(extract_section(full_text, "Stay"))
            st.markdown('</div>', unsafe_allow_html=True)

        with r_col:
            st.markdown('<div class="card"><div class="section-header">🚕 Transport</div>', unsafe_allow_html=True)
            st.write(extract_section(full_text, "Transport"))
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="card"><div class="section-header">💸 Budget & Safety</div>', unsafe_allow_html=True)
            st.write(extract_section(full_text, "Budget"))
            st.markdown('</div>', unsafe_allow_html=True)

    # Refinement Section (Bottom)
    st.divider()
    with st.expander("🔄 Refine this plan"):
        refine_input = st.text_input("Change something (e.g., 'Make it more kid-friendly' or 'I am vegetarian')")
        if st.button("Update Plan"):
            st.toast("Updating based on your preferences...")
else:
    st.info("👈 Enter your trip details in the sidebar and click **Generate** to see your full plan!")
