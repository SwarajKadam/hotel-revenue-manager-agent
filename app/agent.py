import os
from pathlib import Path

from dotenv import load_dotenv
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI

from app.tools import REVENUE_TOOLS

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent
SKILLS_DIR = BASE_DIR / "skills"


SYSTEM_PROMPT = """
You are an AI Revenue Manager assistant for a hotel General Manager.

Your job is to answer business questions using the available hotel revenue tools.
You must behave like a practical hotel revenue manager, not just a data reporter.

Important rules:
1. Use tools whenever the question needs numbers, revenue, ADR, room nights, segments, channels, OTA, cancellations, or pickup.
2. Do not invent numbers.
3. Do not write raw SQL in the answer.
4. Use stay_date for hotel performance unless the user asks about booking creation or pickup.
5. Exclude cancelled reservations unless the user asks about cancellations.
6. Explain the business meaning of the numbers.
7. Give clear recommendations when useful.
8. Keep answers concise and executive-friendly.
9. Use € as the currency symbol when presenting revenue and ADR.

Available business concepts:
- On-the-books revenue
- Room nights
- ADR
- Total revenue
- OTA dependency
- Channel mix
- Market mix
- Room type ADR
- Group/block business
- Pickup in the last 7 days
- Cancellations

When answering:
- Start with the direct answer.
- Mention the key numbers.
- Explain what it means.
- Give one or two practical recommendations.
"""


def get_agent():
    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
    )

    agent = create_deep_agent(
        tools=REVENUE_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        model=model,
        skills=[
            str(SKILLS_DIR / "revenue_manager"),
            str(SKILLS_DIR / "ota_analysis"),
            str(SKILLS_DIR / "pickup_cancellation"),
        ],
    )

    return agent


def ask_agent(question: str) -> str:
    agent = get_agent()

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        }
    )

    messages = result.get("messages", [])

    if not messages:
        return "No response generated."

    final_message = messages[-1]

    if hasattr(final_message, "content"):
        return final_message.content

    if isinstance(final_message, dict):
        return final_message.get("content", "No response content.")

    return str(final_message)