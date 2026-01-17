from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_fast_plan(memory):
    prompt = f"""
You are an expert travel planner.

Create a trip plan with these sections clearly labeled:

Overview:
Day Plan:
Stay:
Food:
Transport:
Budget:

User preferences:
Destination: {memory.get('destination', 'Not specified')}
Days: {memory.get('days', 'Not specified')}
Budget: {memory.get('budget', 'Not specified')}
Interests: {memory.get('interests', 'Not specified')}
Style: {memory.get('style', 'Not specified')}

Keep it concise, structured, and helpful.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )

    return response.choices[0].message.content
