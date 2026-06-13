from langchain_core.tools import tool

from app.metrics import (
    get_revenue_by_month,
    get_channel_mix,
    get_ota_dependency,
    get_cancellations_by_month,
    get_room_type_adr,
    get_group_business_summary,
    get_pickup_last_7_days,
    get_market_mix,
)


@tool
def revenue_by_month_tool() -> dict:
    """Use this when the user asks about on-the-books revenue, monthly revenue, future stay revenue, room nights, reservations, or ADR by month."""
    return get_revenue_by_month()


@tool
def channel_mix_tool() -> dict:
    """Use this when the user asks about booking channels, channel mix, direct vs indirect channels, web bookings, reception bookings, email bookings, or walk-in contribution."""
    return get_channel_mix()


@tool
def ota_dependency_tool() -> dict:
    """Use this when the user asks about OTA dependency, Booking.com, Expedia, online travel agencies, direct vs indirect business, or OTA revenue risk."""
    return get_ota_dependency()


@tool
def cancellations_by_month_tool() -> dict:
    """Use this when the user asks about cancellations, cancelled reservations, lost revenue, cancellation impact, or cancelled room nights by month."""
    return get_cancellations_by_month()


@tool
def room_type_adr_tool() -> dict:
    """Use this when the user asks which room type has the highest ADR, room revenue, room class performance, Executive King, Standard King, or Standard Twin comparison."""
    return get_room_type_adr()


@tool
def group_business_tool() -> dict:
    """Use this when the user asks about group business, block bookings, MICE demand, corporate groups, conference groups, SMERF groups, or transient versus group business."""
    return get_group_business_summary()


@tool
def pickup_last_7_days_tool() -> dict:
    """Use this when the user asks what changed recently, booking pickup, new reservations, recent demand, last 7 days performance, or newly created future business."""
    return get_pickup_last_7_days()


@tool
def market_mix_tool() -> dict:
    """Use this when the user asks about market segments, market mix, corporate demand, leisure demand, MICE, OTA, BAR, promotional, FIT, or segment-level performance."""
    return get_market_mix()


REVENUE_TOOLS = [
    revenue_by_month_tool,
    channel_mix_tool,
    ota_dependency_tool,
    cancellations_by_month_tool,
    room_type_adr_tool,
    group_business_tool,
    pickup_last_7_days_tool,
    market_mix_tool,
]