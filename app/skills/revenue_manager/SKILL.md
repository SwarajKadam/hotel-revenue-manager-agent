# Revenue Manager Skill

Use this skill when the user asks about hotel revenue performance, monthly revenue, room nights, ADR, market mix, room type performance, or business drivers.

## How to reason

1. Always identify the relevant stay period first.
2. Use stay_date-based metrics for hotel performance.
3. Exclude cancelled reservations unless the user specifically asks about cancellations.
4. Use reservation count, room nights, room revenue, total revenue, and ADR together.
5. Do not judge performance only from revenue. Also consider room nights and ADR.
6. When explaining performance, identify the biggest drivers:
   - month
   - room type
   - market segment
   - channel
   - group/block business

## Recommended tool usage

- Use `revenue_by_month_tool` for monthly revenue, room nights, ADR, and on-the-books performance.
- Use `market_mix_tool` for segment-level drivers.
- Use `room_type_adr_tool` for room type pricing and ADR comparison.
- Use `group_business_tool` for group/block versus transient business.

## Answer style

Answer like a practical hotel revenue manager.

The answer should include:

- direct summary
- key numbers
- business interpretation
- recommended action

Avoid giving only raw data.

## Example reasoning

If one month has high revenue but low ADR, explain that demand may be volume-driven rather than price-driven.

If Executive King has the highest ADR, mention that premium room types are stronger and may support rate protection.

If MICE/group segments dominate, mention that the hotel should monitor group displacement risk and protect high-value transient demand.