import streamlit as st
from agent import generate_fast_plan
import re

st.set_page_config(page_title="Your AI Trip Planner", layout="centered")

# ---------- Styling ----------
st.markdown("""
<style>
.card {
    background: #1f2937;
    color: #f9fafb;
    padding: 16px;
    border-radius: 16px;
    margin-bottom: 12px;
    border: 1px solid #2f3a4a;
}
.section-title {
    font-weight: 600;
    font-size: 1.1rem;
    margin-bottom: 6px;
}
.timeline-item {
    padding: 8px 12px;
    border-left: 3px solid #3b82f6;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

# ---------- Title ----------
st.title("🌍 Your AI Trip Planner")
st.caption("Fast • Visual • Efficient")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Your Trip")
    destination = st.text_input("Destination")
    days = st.text_input("Days")
    budget = st.selectbox("Budget", ["Low💲", "Medium 💲💲", "Luxury 💲💲💲"])
    interests = st.text_input("Interests (food, culture, shopping, etc.)")
    style = st.selectbox("Travel style", ["Relaxed", "Balanced", "Packed"])
    generate = st.button("Generate ⚡")

# ---------- Session ----------
if "plan" not in st.session_state:
    st.session_state.plan = None

# ---------- Generate ----------
if generate:
    if not destination or not days:
        st.warning("Enter destination and days.")
    else:
        memory = {
            "destination": destination,
            "days": days,
            "budget": budget,
            "interests": interests,
            "style": style
        }
        with st.spinner("Building your trip..."):
            st.session_state.plan = generate_fast_plan(memory)

# ---------- Helpers ----------
def clean_text(text):
    # Remove Markdown headers (e.g., #, ##, ###)
    text = re.sub(r"#+\s*", "", text)  
    # Remove bold markers
    text = re.sub(r"\*\*", "", text)  
    # Standardize bullet points
    text = re.sub(r"- ", "• ", text)  
    return text.strip()

def card(title, content):
    content = clean_text(content)
    content = content.replace("\n", "<br>")
    st.markdown(f"""
    <div class="card">
        <div class="section-title">{title}</div>
        {content}
    </div>
    """, unsafe_allow_html=True)

def split_sections(text):
    sections = {
        "overview": "",
        "day": "",
        "stay": "",
        "food": "",
        "transport": "",
        "budget": ""
    }

    lines = text.split("\n")
    current = "overview"

    # Define keywords/regex for each section to make it "smarter"
    triggers = {
        "day": r"(day\s*plan|itinerary|daily)",
        "stay": r"(stay|accommodation|hotel|where to stay)",
        "food": r"(food|dining|restaurant|meals)",
        "transport": r"(transport|getting around|travel)",
        "budget": r"(budget|cost|expenses)"
    }

    for line in lines:
        clean_line = line.lower().strip()
        
        # Check if the line is a header for a new section
        found_new_section = False
        for key, pattern in triggers.items():
            if re.search(pattern, clean_line):
                current = key
                found_new_section = True
                break
        
        # Skip adding the header line itself to the content
        if found_new_section:
            continue

        sections[current] += line + "\n"

    return sections

# ---------- Display ----------
if st.session_state.plan:
    st.subheader("Your Plan")

    sections = split_sections(st.session_state.plan)

    # Combine sidebar inputs into the Overview card
    with st.expander("🧭 Overview", expanded=True):
        trip_summary = f"""
        • **Destination:** {destination}
        • **Days:** {days}
        • **Budget:** {budget}
        • **Style:** {style}
        • **Interests:** {interests}
        
        """
        # Join user options with AI-generated overview text
        full_overview = trip_summary + sections["overview"]
        card("Trip Snapshot", full_overview)

    if sections["day"].strip():
        with st.expander("🗓 Day Plan"):
            for line in clean_text(sections["day"]).split("\n"):
                if re.search(r"\d{1,2}:\d{2}", line):
                    st.markdown(f'<div class="timeline-item">🕒 {line}</div>', unsafe_allow_html=True)
                else:
                    st.write(line)

    if sections["stay"].strip():
        with st.expander("🏨 Stay"):
            card("Where to stay", sections["stay"])

    if sections["food"].strip():
        with st.expander("🍽 Food"):
            card("Food", sections["food"])

    if sections["transport"].strip():
        with st.expander("🚕 Transport"):
            card("Transport", sections["transport"])

    if sections["budget"].strip():
        with st.expander("💸 Budget"):
            card("Budget", sections["budget"])

