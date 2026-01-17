import streamlit as st
from agent import generate_initial_plan, refine_plan

st.set_page_config(page_title="AI Trip Planner", layout="wide")
st.title("🌍 Autonomous AI Trip Planner")

# Session state
if "plan" not in st.session_state:
    st.session_state.plan = None

if "chat" not in st.session_state:
    st.session_state.chat = []

# Sidebar form
with st.sidebar:
    st.header("Trip Preferences")

    destination = st.text_input("Destination")
    days = st.text_input("Number of days")
    budget = st.selectbox("Budget", ["Low", "Medium", "Luxury"])
    interests = st.text_input("Interests (food, history, shopping, etc.)")
    style = st.selectbox("Travel style", ["Relaxed", "Balanced", "Packed"])

    generate = st.button("Generate Trip Plan 🚀")

# Main logic
if generate:
    if not destination or not days:
        st.warning("Please fill in destination and days.")
    else:
        memory = {
            "destination": destination,
            "days": days,
            "budget": budget,
            "interests": interests,
            "style": style
        }

        with st.spinner("Planning your trip..."):
            plan = generate_initial_plan(memory)

        st.session_state.plan = plan
        st.session_state.chat = []

        st.success("Your initial trip plan is ready!")

# Display plan
if st.session_state.plan:
    st.subheader("📋 Your Trip Plan")
    st.markdown(st.session_state.plan)

    st.divider()
    st.subheader("💬 Refine Your Plan")

    # Show chat history
    for msg in st.session_state.chat:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Agent:** {msg['content']}")

    user_input = st.text_input("Type your refinement request (e.g., 'I arrive at 10am and prefer veg food')")

    if st.button("Refine Plan"):
        if user_input:
            st.session_state.chat.append({"role": "user", "content": user_input})

            with st.spinner("Refining your plan..."):
                refined = refine_plan(st.session_state.plan, user_input)

            st.session_state.chat.append({"role": "agent", "content": refined})
            st.session_state.plan = refined
            st.experimental_rerun()
