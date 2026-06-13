from app.db import fetch_all


def get_revenue_by_month():
    query = """
    SELECT
        TO_CHAR(DATE_TRUNC('month', stay_date), 'YYYY-MM') AS month,
        COUNT(DISTINCT reservation_id) AS reservations,
        SUM(number_of_spaces) AS room_nights,
        ROUND(SUM(daily_room_revenue_before_tax), 2) AS room_revenue,
        ROUND(SUM(daily_total_revenue_before_tax), 2) AS total_revenue,
        ROUND(
            SUM(daily_room_revenue_before_tax)
            / NULLIF(SUM(number_of_spaces), 0),
            2
        ) AS adr
    FROM reservations_hackathon
    WHERE reservation_status = 'Reserved'
      AND stay_date >= CURRENT_DATE
    GROUP BY DATE_TRUNC('month', stay_date)
    ORDER BY DATE_TRUNC('month', stay_date);
    """

    return {
        "metric": "revenue_by_month",
        "assumption": "Uses stay_date, excludes cancelled reservations, includes only future/on-the-books stays.",
        "data": fetch_all(query),
    }


def get_channel_mix():
    query = """
    SELECT
        r.channel_code,
        c.channel_name,
        c.channel_group,
        COUNT(DISTINCT r.reservation_id) AS reservations,
        SUM(r.number_of_spaces) AS room_nights,
        ROUND(SUM(r.daily_total_revenue_before_tax), 2) AS total_revenue,
        ROUND(
            100.0 * SUM(r.daily_total_revenue_before_tax)
            / NULLIF(SUM(SUM(r.daily_total_revenue_before_tax)) OVER (), 0),
            2
        ) AS revenue_share_pct
    FROM reservations_hackathon r
    LEFT JOIN channel_code_lookup c
        ON r.channel_code = c.channel_code
    WHERE r.reservation_status = 'Reserved'
      AND r.stay_date >= CURRENT_DATE
    GROUP BY r.channel_code, c.channel_name, c.channel_group
    ORDER BY total_revenue DESC;
    """

    return {
        "metric": "channel_mix",
        "assumption": "Uses future reserved stay dates only. Revenue share is based on total revenue before tax.",
        "data": fetch_all(query),
    }


def get_ota_dependency():
    query = """
    SELECT
        CASE
            WHEN market_code = 'OTA'
              OR LOWER(source_name) LIKE '%%booking%%'
              OR LOWER(source_name) LIKE '%%expedia%%'
            THEN 'OTA'
            ELSE 'Non-OTA'
        END AS booking_type,
        COUNT(DISTINCT reservation_id) AS reservations,
        SUM(number_of_spaces) AS room_nights,
        ROUND(SUM(daily_total_revenue_before_tax), 2) AS total_revenue,
        ROUND(
            100.0 * SUM(daily_total_revenue_before_tax)
            / NULLIF(SUM(SUM(daily_total_revenue_before_tax)) OVER (), 0),
            2
        ) AS revenue_share_pct
    FROM reservations_hackathon
    WHERE reservation_status = 'Reserved'
      AND stay_date >= CURRENT_DATE
    GROUP BY booking_type
    ORDER BY total_revenue DESC;
    """

    return {
        "metric": "ota_dependency",
        "assumption": "OTA is identified using market_code = OTA or source names such as Booking.com/Expedia. Future reserved stays only.",
        "data": fetch_all(query),
    }


def get_cancellations_by_month():
    query = """
    SELECT
        TO_CHAR(DATE_TRUNC('month', stay_date), 'YYYY-MM') AS stay_month,
        COUNT(DISTINCT reservation_id) AS cancelled_reservations,
        SUM(number_of_spaces) AS cancelled_room_nights,
        ROUND(SUM(daily_total_revenue_before_tax), 2) AS cancelled_total_revenue
    FROM reservations_hackathon
    WHERE reservation_status = 'Cancelled'
    GROUP BY DATE_TRUNC('month', stay_date)
    ORDER BY DATE_TRUNC('month', stay_date);
    """

    return {
        "metric": "cancellations_by_month",
        "assumption": "Uses stay_date month to show the business impact of cancelled reservations.",
        "data": fetch_all(query),
    }


def get_room_type_adr():
    query = """
    SELECT
        r.space_type,
        rt.display_name,
        rt.room_class,
        COUNT(DISTINCT r.reservation_id) AS reservations,
        SUM(r.number_of_spaces) AS room_nights,
        ROUND(SUM(r.daily_room_revenue_before_tax), 2) AS room_revenue,
        ROUND(AVG(r.adr_room), 2) AS adr
    FROM reservations_hackathon r
    LEFT JOIN room_type_lookup rt
        ON r.space_type = rt.space_type
    WHERE r.reservation_status = 'Reserved'
      AND r.stay_date >= CURRENT_DATE
    GROUP BY r.space_type, rt.display_name, rt.room_class
    ORDER BY adr DESC;
    """

    return {
        "metric": "room_type_adr",
        "assumption": "ADR uses the reservation-level adr_room field averaged by room type. Cancelled reservations are excluded.",
        "data": fetch_all(query),
    }


def get_group_business_summary():
    query = """
    SELECT
        CASE
            WHEN is_block = TRUE
              OR market_code IN ('CNI', 'CGR', 'SMERF')
            THEN 'Group / Block'
            ELSE 'Transient'
        END AS business_type,
        COUNT(DISTINCT reservation_id) AS reservations,
        SUM(number_of_spaces) AS room_nights,
        ROUND(SUM(daily_total_revenue_before_tax), 2) AS total_revenue,
        ROUND(
            100.0 * SUM(daily_total_revenue_before_tax)
            / NULLIF(SUM(SUM(daily_total_revenue_before_tax)) OVER (), 0),
            2
        ) AS revenue_share_pct
    FROM reservations_hackathon
    WHERE reservation_status = 'Reserved'
      AND stay_date >= CURRENT_DATE
    GROUP BY business_type
    ORDER BY total_revenue DESC;
    """

    return {
        "metric": "group_business_summary",
        "assumption": "Group business is identified using is_block=true or group-style market codes CNI, CGR, and SMERF.",
        "data": fetch_all(query),
    }


def get_pickup_last_7_days():
    query = """
    SELECT
        TO_CHAR(DATE_TRUNC('month', stay_date), 'YYYY-MM') AS stay_month,
        COUNT(DISTINCT reservation_id) AS new_reservations,
        SUM(number_of_spaces) AS picked_up_room_nights,
        ROUND(SUM(daily_total_revenue_before_tax), 2) AS picked_up_total_revenue
    FROM reservations_hackathon
    WHERE reservation_status = 'Reserved'
      AND stay_date >= CURRENT_DATE
      AND create_datetime >= NOW() - INTERVAL '7 days'
    GROUP BY DATE_TRUNC('month', stay_date)
    ORDER BY DATE_TRUNC('month', stay_date);
    """

    return {
        "metric": "pickup_last_7_days",
        "assumption": "Uses create_datetime to measure new reservations created in the last 7 days for future stay dates.",
        "data": fetch_all(query),
    }


def get_market_mix():
    query = """
    SELECT
        r.market_code,
        m.market_name,
        m.macro_group,
        COUNT(DISTINCT r.reservation_id) AS reservations,
        SUM(r.number_of_spaces) AS room_nights,
        ROUND(SUM(r.daily_total_revenue_before_tax), 2) AS total_revenue,
        ROUND(
            100.0 * SUM(r.daily_total_revenue_before_tax)
            / NULLIF(SUM(SUM(r.daily_total_revenue_before_tax)) OVER (), 0),
            2
        ) AS revenue_share_pct
    FROM reservations_hackathon r
    LEFT JOIN market_code_lookup m
        ON r.market_code = m.market_code
    WHERE r.reservation_status = 'Reserved'
      AND r.stay_date >= CURRENT_DATE
    GROUP BY r.market_code, m.market_name, m.macro_group
    ORDER BY total_revenue DESC;
    """

    return {
        "metric": "market_mix",
        "assumption": "Uses future reserved stay dates only and groups business by market code.",
        "data": fetch_all(query),
    }