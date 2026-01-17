from openai import OpenAI

client = OpenAI()

def generate_initial_plan(memory):
    prompt = f"""
Rizzo, your autonomous AI travel planner.

User preferences:
- Destination: {memory['destination']}
- Days: {memory['days']}
- Budget: {memory['budget']}
- Interests: {memory['interests']}
- Travel style: {memory['style']}

Create a complete personalized travel plan with:
1. Overview
2. Where to stay
3. Day-by-day itinerary
4. Food recommendations
5. Transportation tips
6. Budget guidance
7. Packing checklist
8. Safety tips

End by asking 2–3 smart follow-up questions to refine the plan.
"""

    response = client.chat.completions.create(
        model="gpt-5.2",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content


def refine_plan(existing_plan, user_message):
    prompt = f"""
You are refining an existing travel plan.

Here is the current plan:
{existing_plan}

User refinement request:
{user_message}

Update the plan accordingly and clearly explain what changed.
"""

    response = client.chat.completions.create(
        model="gpt-5.2",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content
