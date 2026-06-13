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
        COALESCE(mgh.macro_group, m.macro_group, 'Unknown') AS macro_group,
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
    LEFT JOIN macro_group_history mgh
        ON r.market_code = mgh.market_code
       AND r.stay_date >= mgh.effective_from
       AND (
            mgh.effective_to IS NULL
            OR r.stay_date < mgh.effective_to
       )
    WHERE r.reservation_status = 'Reserved'
      AND r.stay_date >= CURRENT_DATE
    GROUP BY
        r.market_code,
        m.market_name,
        COALESCE(mgh.macro_group, m.macro_group, 'Unknown')
    ORDER BY total_revenue DESC;
    """

    return {
        "metric": "market_mix",
        "assumption": "Uses future reserved stay dates. Macro group is selected using macro_group_history by stay_date, falling back to market_code_lookup.",
        "data": fetch_all(query),
    }

def get_financial_status_summary():
    query = """
    SELECT
        COALESCE(financial_status, 'Unknown') AS financial_status,
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
    GROUP BY COALESCE(financial_status, 'Unknown')
    ORDER BY total_revenue DESC;
    """

    return {
        "metric": "financial_status_summary",
        "assumption": "Uses future reserved stays and groups revenue by financial_status, such as Posted or Provisional.",
        "data": fetch_all(query),
    }


def get_rate_plan_performance():
    query = """
    SELECT
        r.rate_plan_code,
        COALESCE(rp.rate_plan_name, r.rate_plan_code) AS rate_plan_name,
        COALESCE(
            rp.rate_plan_group,
            CASE
                WHEN r.rate_plan_code ILIKE '%%GROUP%%' THEN 'Group'
                WHEN r.rate_plan_code ILIKE '%%CORP%%' THEN 'Corporate'
                WHEN r.rate_plan_code ILIKE '%%BOOK%%' THEN 'OTA'
                WHEN r.rate_plan_code ILIKE '%%EXP%%' THEN 'OTA'
                WHEN r.rate_plan_code ILIKE '%%BAR%%' THEN 'Retail'
                WHEN r.rate_plan_code ILIKE '%%PROM%%' THEN 'Promotion'
                WHEN r.rate_plan_code ILIKE '%%FIT%%' THEN 'Retail'
                WHEN r.rate_plan_code ILIKE '%%DLY%%' THEN 'Retail'
                WHEN r.rate_plan_code ILIKE '%%OCH%%' THEN 'Direct'
                ELSE 'Unknown'
            END
        ) AS rate_plan_group,
        COUNT(DISTINCT r.reservation_id) AS reservations,
        SUM(r.number_of_spaces) AS room_nights,
        ROUND(SUM(r.daily_room_revenue_before_tax), 2) AS room_revenue,
        ROUND(SUM(r.daily_total_revenue_before_tax), 2) AS total_revenue,
        ROUND(
            SUM(r.daily_room_revenue_before_tax)
            / NULLIF(SUM(r.number_of_spaces), 0),
            2
        ) AS adr
    FROM reservations_hackathon r
    LEFT JOIN rate_plan_lookup rp
        ON r.rate_plan_code = rp.rate_plan_code
    WHERE r.reservation_status = 'Reserved'
      AND r.stay_date >= CURRENT_DATE
    GROUP BY
        r.rate_plan_code,
        rp.rate_plan_name,
        rp.rate_plan_group,
        CASE
            WHEN r.rate_plan_code ILIKE '%%GROUP%%' THEN 'Group'
            WHEN r.rate_plan_code ILIKE '%%CORP%%' THEN 'Corporate'
            WHEN r.rate_plan_code ILIKE '%%BOOK%%' THEN 'OTA'
            WHEN r.rate_plan_code ILIKE '%%EXP%%' THEN 'OTA'
            WHEN r.rate_plan_code ILIKE '%%BAR%%' THEN 'Retail'
            WHEN r.rate_plan_code ILIKE '%%PROM%%' THEN 'Promotion'
            WHEN r.rate_plan_code ILIKE '%%FIT%%' THEN 'Retail'
            WHEN r.rate_plan_code ILIKE '%%DLY%%' THEN 'Retail'
            WHEN r.rate_plan_code ILIKE '%%OCH%%' THEN 'Direct'
            ELSE 'Unknown'
        END
    ORDER BY total_revenue DESC;
    """

    return {
        "metric": "rate_plan_performance",
        "assumption": "Uses future reserved stays. Joins to rate_plan_lookup, then derives fallback group from rate_plan_code when lookup metadata is missing.",
        "data": fetch_all(query),
    }


def get_dataset_verification_latest():
    query = """
    SELECT
        dataset_revision,
        total_stay_rows,
        total_reservations,
        posted_otb_total_revenue,
        posted_otb_room_revenue,
        reservation_stay_status_sha256,
        scraped_at
    FROM dataset_verification
    ORDER BY scraped_at DESC
    LIMIT 1;
    """

    return {
        "metric": "dataset_verification_latest",
        "assumption": "Shows the latest captured verification metadata from the data portal, if ETL has stored it.",
        "data": fetch_all(query),
    }