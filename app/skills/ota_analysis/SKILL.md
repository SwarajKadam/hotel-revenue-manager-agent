---
name: ota-analysis
description: Use this skill for OTA dependency, Booking.com, Expedia, online travel agency risk, direct versus indirect bookings, channel mix, distribution strategy, and OTA commercial recommendations.
---

# OTA Analysis Skill

Use this skill when the user asks about OTA dependency, Booking.com, Expedia, direct bookings, indirect bookings, channel risk, or distribution strategy.

## Core business rules

- OTA includes `market_code = OTA` and source names such as Booking.com or Expedia.
- OTA is useful for demand generation but can create margin risk due to commission.
- Do not say OTA is bad automatically. Judge the risk from revenue share, room-night share, and business context.
- Compare OTA against Non-OTA.

## How to reason

1. Check OTA revenue share.
2. Check OTA room nights and reservations.
3. Compare OTA with Non-OTA.
4. Explain whether dependence is low, moderate, or high.
5. Recommend direct-channel actions only if useful.

## Tool guidance

- Use `ota_dependency_tool` for OTA vs Non-OTA split.
- Use `channel_mix_tool` for detailed channel contribution.
- Use `market_mix_tool` if segment-level demand matters.

## Recommendation examples

If OTA share is high:

- strengthen direct booking offers
- protect direct inventory on high-demand dates
- avoid unnecessary OTA discounting
- use OTA mainly for low-demand periods

If OTA share is moderate or low:

- keep OTA active as a demand generator
- focus on direct conversion
- avoid overcorrecting if OTA is not a major dependency