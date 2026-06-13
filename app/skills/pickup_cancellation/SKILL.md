# Pickup and Cancellation Skill

Use this skill when the user asks about recent pickup, new reservations, booking pace, cancellations, lost revenue, or recent changes in demand.

## How to reason

1. Pickup means new reservations created recently for future stay dates.
2. Use create_datetime to analyze pickup.
3. Use stay_date to understand which future months are affected.
4. Cancellations should be analyzed separately from reserved/on-the-books business.
5. When discussing cancellations, mention both cancelled reservations and cancelled room nights/revenue.
6. If pickup is strong but cancellations are also high, explain that net demand may be weaker than gross pickup suggests.

## Recommended tool usage

- Use `pickup_last_7_days_tool` for recent booking pickup.
- Use `cancellations_by_month_tool` for cancellation impact.
- Use `revenue_by_month_tool` to compare pickup/cancellations against current on-the-books revenue.

## Answer style

The answer should include:

- what changed
- affected months
- demand signal
- risk or opportunity
- recommended action

## Recommendation examples

If pickup is strong:
- protect rates in high-demand months
- reduce unnecessary discounts
- monitor room type availability

If cancellations are high:
- review cancellation windows
- check whether specific segments are cancelling
- avoid overreacting unless replacement demand is weak

If pickup is weak:
- consider targeted promotions
- increase direct/email campaigns
- use OTA selectively for low-demand dates