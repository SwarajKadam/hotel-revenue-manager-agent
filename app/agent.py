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
10. Mention assumptions when the question could be interpreted in more than one way.
11. For complex questions, break the analysis into clear steps before giving the final recommendation.

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


def extract_agent_activity(result: dict) -> dict:
    """
    Extract tool usage and skill usage from Deep Agents / LangChain messages.

    This gives the frontend a visible activity trail:
    - tools_used
    - skills_used
    - activity events
    """
    messages = result.get("messages", [])

    tools_used = []
    skills_used = []
    activity = []

    for message in messages:
        # AI messages may contain tool_calls
        tool_calls = getattr(message, "tool_calls", None)

        if tool_calls:
            for call in tool_calls:
                if isinstance(call, dict):
                    tool_name = call.get("name")
                    args = call.get("args", {})
                else:
                    tool_name = getattr(call, "name", None)
                    args = getattr(call, "args", {})

                if tool_name:
                    tools_used.append(tool_name)
                    activity.append(
                        {
                            "type": "tool_call",
                            "name": tool_name,
                            "args": args,
                        }
                    )

                # If Deep Agents exposes skill loading through filesystem tools,
                # capture skill names from file paths.
                args_text = str(args)

                if "revenue_manager" in args_text:
                    skills_used.append("revenue_manager")

                if "ota_analysis" in args_text:
                    skills_used.append("ota_analysis")

                if "pickup_cancellation" in args_text:
                    skills_used.append("pickup_cancellation")

        # Tool result messages may have a name
        message_name = getattr(message, "name", None)

        if message_name:
            tools_used.append(message_name)
            activity.append(
                {
                    "type": "tool_result",
                    "name": message_name,
                }
            )

    # Fallback skill inference from business tools.
    # This ensures the UI still shows skill usage even if the Deep Agents
    # file-read activity is not exposed by your installed package version.
    inferred_skill_map = {
        "revenue_by_month_tool": "revenue_manager",
        "market_mix_tool": "revenue_manager",
        "room_type_adr_tool": "revenue_manager",
        "group_business_tool": "revenue_manager",
        "channel_mix_tool": "ota_analysis",
        "ota_dependency_tool": "ota_analysis",
        "pickup_last_7_days_tool": "pickup_cancellation",
        "cancellations_by_month_tool": "pickup_cancellation",
    }

    for tool_name in tools_used:
        if tool_name in inferred_skill_map:
            skills_used.append(inferred_skill_map[tool_name])

    return {
        "tools_used": sorted(set(tools_used)),
        "skills_used": sorted(set(skills_used)),
        "activity": activity,
    }


def ask_agent(question: str) -> dict:
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
        answer = "No response generated."
    else:
        final_message = messages[-1]

        if hasattr(final_message, "content"):
            answer = final_message.content
        elif isinstance(final_message, dict):
            answer = final_message.get("content", "No response content.")
        else:
            answer = str(final_message)

    activity = extract_agent_activity(result)

    return {
        "answer": answer,
        "tools_used": activity["tools_used"],
        "skills_used": activity["skills_used"],
        "activity": activity["activity"],
    }