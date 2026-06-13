from pathlib import Path

from dotenv import load_dotenv
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

from app.tools import (
    REVENUE_TOOLS,
    revenue_by_month_tool,
    market_mix_tool,
    room_type_adr_tool,
    group_business_tool,
    ota_dependency_tool,
    channel_mix_tool,
    pickup_last_7_days_tool,
    cancellations_by_month_tool,
)

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent
SKILLS_DIR = BASE_DIR / "skills"

CHECKPOINTER = MemorySaver()
STORE = InMemoryStore()
_AGENT = None


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
11. For complex questions, plan the answer before responding:
    - identify the business question
    - select the right tool or subagent
    - compare the relevant metrics
    - state the recommendation
12. If the user asks to refresh, reload, scrape, rerun ETL, or update the database, use the refresh_database_tool. Do not silently run ETL.

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


SUBAGENTS = [
    {
        "name": "ota-analyst",
        "description": (
            "Use this subagent for OTA dependency, Booking.com, Expedia, "
            "direct vs indirect channel risk, and distribution strategy questions."
        ),
        "system_prompt": """
You are a specialist hotel OTA and distribution analyst.

Focus only on OTA dependency, direct vs indirect business, channel mix, and distribution risk.

Rules:
- Use OTA and channel tools.
- Compare OTA revenue share with Non-OTA revenue share.
- Explain whether the risk is low, moderate, or high.
- Recommend practical direct-channel or OTA-control actions.
- Return a concise summary to the main agent.
""",
        "tools": [ota_dependency_tool, channel_mix_tool, market_mix_tool],
        "skills": [str(SKILLS_DIR / "ota_analysis")],
    },
    {
        "name": "pickup-cancellation-analyst",
        "description": (
            "Use this subagent for recent pickup, last 7 days changes, cancellations, "
            "lost revenue, booking pace, and demand change questions."
        ),
        "system_prompt": """
You are a specialist hotel pickup and cancellation analyst.

Focus only on recent booking pickup, cancellations, lost demand, and future demand movement.

Rules:
- Use pickup and cancellation tools.
- Use create_datetime for pickup.
- Use stay_date to explain which future months are affected.
- Separate reserved/on-the-books business from cancelled business.
- Return a concise summary to the main agent.
""",
        "tools": [
            pickup_last_7_days_tool,
            cancellations_by_month_tool,
            revenue_by_month_tool,
        ],
        "skills": [str(SKILLS_DIR / "pickup_cancellation")],
    },
    {
        "name": "revenue-briefing-analyst",
        "description": (
            "Use this subagent for broad GM briefing questions, monthly revenue performance, "
            "market mix, room type ADR, group business, and commercial recommendations."
        ),
        "system_prompt": """
You are a senior hotel revenue briefing analyst.

Focus on turning metrics into a GM-ready commercial briefing.

Rules:
- Use revenue, market mix, room type, and group business tools.
- Identify the biggest drivers.
- Mention assumptions.
- Give clear commercial recommendations.
- Keep the answer concise but insightful.
""",
        "tools": [
            revenue_by_month_tool,
            market_mix_tool,
            room_type_adr_tool,
            group_business_tool,
            channel_mix_tool,
        ],
        "skills": [str(SKILLS_DIR / "revenue_manager")],
    },
]


def get_agent():
    global _AGENT

    if _AGENT is not None:
        return _AGENT

    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
    )

    _AGENT = create_deep_agent(
        model=model,
        tools=REVENUE_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        skills=[
            str(SKILLS_DIR / "revenue_manager"),
            str(SKILLS_DIR / "ota_analysis"),
            str(SKILLS_DIR / "pickup_cancellation"),
        ],
        subagents=SUBAGENTS,
        memory=[
            "/memories/AGENTS.md",
        ],
        checkpointer=CHECKPOINTER,
        store=STORE,
        interrupt_on={
            "refresh_database_tool": {
                "allowed_decisions": ["approve", "reject"],
            }
        },
        name="hotel-revenue-manager-agent",
    )

    return _AGENT


def extract_agent_activity(result: dict) -> dict:
    messages = result.get("messages", [])

    tools_used = []
    skills_used = []
    subagents_used = []
    activity = []

    for message in messages:
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

                args_text = str(args)

                if tool_name == "task":
                    if "ota-analyst" in args_text:
                        subagents_used.append("ota-analyst")
                    if "pickup-cancellation-analyst" in args_text:
                        subagents_used.append("pickup-cancellation-analyst")
                    if "revenue-briefing-analyst" in args_text:
                        subagents_used.append("revenue-briefing-analyst")

                if "revenue_manager" in args_text:
                    skills_used.append("revenue_manager")
                if "ota_analysis" in args_text:
                    skills_used.append("ota_analysis")
                if "pickup_cancellation" in args_text:
                    skills_used.append("pickup_cancellation")

        message_name = getattr(message, "name", None)

        if message_name and message_name != "hotel-revenue-manager-agent":
            tools_used.append(message_name)
            activity.append(
                {
                    "type": "tool_result",
                    "name": message_name,
                }
            )

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

    inferred_subagent_map = {
        "ota_dependency_tool": "ota-analyst",
        "channel_mix_tool": "ota-analyst",
        "pickup_last_7_days_tool": "pickup-cancellation-analyst",
        "cancellations_by_month_tool": "pickup-cancellation-analyst",
        "revenue_by_month_tool": "revenue-briefing-analyst",
        "market_mix_tool": "revenue-briefing-analyst",
        "room_type_adr_tool": "revenue-briefing-analyst",
        "group_business_tool": "revenue-briefing-analyst",
    }

    for tool_name in tools_used:
        if tool_name in inferred_skill_map:
            skills_used.append(inferred_skill_map[tool_name])
        if tool_name in inferred_subagent_map:
            subagents_used.append(inferred_subagent_map[tool_name])

    return {
        "tools_used": sorted(set(tools_used)),
        "skills_used": sorted(set(skills_used)),
        "subagents_used": sorted(set(subagents_used)),
        "activity": activity,
    }

def is_database_refresh_request(question: str) -> bool:
    text = question.lower()

    refresh_keywords = [
        "refresh database",
        "refresh the database",
        "reload database",
        "reload the database",
        "rerun etl",
        "re-run etl",
        "run etl",
        "scrape again",
        "scrape the data",
        "update database",
        "update the database",
        "reload data",
        "refresh data",
    ]

    return any(keyword in text for keyword in refresh_keywords)

def ask_agent(question: str, thread_id: str | None = None) -> dict:
    if thread_id is None:
        thread_id = "default-hotel-gm-thread"

    if is_database_refresh_request(question):
        return {
            "answer": (
                "This action requires human approval before it can continue. "
                "Refreshing or reloading the database would rerun the ETL pipeline, "
                "so I will not run it automatically from the public chat UI. "
                "A project owner should approve and run the ETL manually."
            ),
            "tools_used": ["refresh_database_tool"],
            "skills_used": [],
            "subagents_used": [],
            "activity": [
                {
                    "type": "human_in_the_loop",
                    "name": "approval_required",
                }
            ],
            "thread_id": thread_id,
        }

    agent = get_agent()

    try:
        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": question,
                    }
                ]
            },
            config={
                "configurable": {
                    "thread_id": thread_id,
                }
            },
        )
    except Exception as error:
        error_text = str(error)

        if "interrupt" in error_text.lower() or "__interrupt__" in error_text.lower():
            return {
                "answer": (
                    "This action requires human approval before it can continue. "
                    "For safety, I will not refresh or reload the database automatically from the public chat UI."
                ),
                "tools_used": ["refresh_database_tool"],
                "skills_used": [],
                "subagents_used": [],
                "activity": [
                    {
                        "type": "human_in_the_loop",
                        "name": "approval_required",
                    }
                ],
                "thread_id": thread_id,
            }

        raise

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
        "subagents_used": activity["subagents_used"],
        "activity": activity["activity"],
        "thread_id": thread_id,
    }