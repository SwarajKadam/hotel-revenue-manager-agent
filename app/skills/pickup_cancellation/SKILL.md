---
name: pickup-cancellation
description: Use this skill for recent booking pickup, new reservations, booking pace, cancellations, lost revenue, cancellation impact, and recent changes in future hotel demand.
---

# Pickup and Cancellation Skill

Use this skill when the user asks about recent pickup, new reservations, booking pace, cancellations, lost revenue, or recent changes in demand.

## Core business rules

- Pickup means reservations created recently for future stay dates.
- Use `create_datetime` for pickup.
- Use `stay_date` to understand which future months are affected.
- Analyze cancellations separately from reserved/on-the-books business.
- Cancelled revenue is not current OTB revenue, but it shows lost demand or risk.

## How to reason

1. For pickup, identify newly created future business.
2. For cancellations, identify cancelled reservations, room nights, and lost revenue by stay month.
3. If pickup is strong but cancellations are also high, explain that net demand may be weaker than gross pickup.
4. Recommend actions based on the signal.

## Tool guidance

- Use `pickup_last_7_days_tool` for recent new reservations.
- Use `cancellations_by_month_tool` for cancellation impact.
- Use `revenue_by_month_tool` if comparing against current OTB position.

## Recommendation examples

If pickup is strong:

- protect rates in strong months
- reduce unnecessary discounts
- monitor room type availability

If cancellations are high:

- review cancellation windows
- check whether specific segments are cancelling
- avoid overreacting unless replacement demand is weak

If pickup is weak:

- consider targeted promotions
- use email/direct campaigns
- use OTA selectively for low-demand months