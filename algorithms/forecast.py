# ============================================
# SMART WASTE AI FORECASTING
# ============================================


def calculate_fill_rate(
    current_fill,
    previous_fill,
    time_difference_minutes
):
    """
    Calculate how quickly the dustbin is filling.

    Returns:
        Fill rate in percentage per hour.
    """

    if time_difference_minutes <= 0:
        return 0.0

    fill_change = current_fill - previous_fill

    time_difference_hours = (
        time_difference_minutes / 60
    )

    fill_rate = (
        fill_change / time_difference_hours
    )

    return round(fill_rate, 2)


def estimate_time_to_overflow(
    current_fill,
    fill_rate,
    overflow_threshold=80
):
    """
    Estimate time required to reach
    the overflow threshold.

    Returns:
        Estimated hours or None.
    """

    if current_fill >= overflow_threshold:
        return 0.0

    if fill_rate <= 0:
        return None

    remaining_fill = (
        overflow_threshold - current_fill
    )

    estimated_hours = (
        remaining_fill / fill_rate
    )

    return round(estimated_hours, 2)


def forecast_fill_level(
    current_fill,
    fill_rate,
    future_hours=2
):
    """
    Estimate the fill level after
    a specified number of hours.
    """

    predicted_fill = (
        current_fill +
        (fill_rate * future_hours)
    )

    # Keep fill level between 0 and 100
    predicted_fill = max(
        0,
        min(100, predicted_fill)
    )

    return round(predicted_fill, 2)

def calculate_average_fill_rate(readings):
    """
    Calculate average fill rate using historical readings.
    readings format: [(fill_level, timestamp), ...]
    """

    if len(readings) < 2:
        return 0.0

    rates = []

    # Readings are newest first
    for i in range(len(readings) - 1):
        current_fill, current_time = readings[i]
        previous_fill, previous_time = readings[i + 1]

        time_difference_hours = (
            current_time - previous_time
        ).total_seconds() / 3600

        if time_difference_hours > 0:
            fill_change = float(current_fill) - float(previous_fill)
            rate = fill_change / time_difference_hours

            rates.append(rate)

    if not rates:
        return 0.0

    average_rate = sum(rates) / len(rates)

    return round(average_rate, 2)