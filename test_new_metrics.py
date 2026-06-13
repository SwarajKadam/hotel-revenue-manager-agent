from app.metrics import (
    get_rate_plan_performance,
    get_financial_status_summary,
    get_market_mix,
)

print("\nRATE PLAN PERFORMANCE")
print(get_rate_plan_performance())

print("\nFINANCIAL STATUS SUMMARY")
print(get_financial_status_summary())

print("\nMARKET MIX")
print(get_market_mix())