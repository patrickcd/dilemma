from datetime import datetime, timedelta, timezone


class DateMethods:

    def date_is_past(self, items: list) -> bool:
        """Handle 'is past' date comparison"""
        date_obj = self._ensure_datetime(items[0])
        now = datetime.now(date_obj.tzinfo if date_obj.tzinfo else timezone.utc)
        return date_obj < now

    def date_is_future(self, items: list) -> bool:
        """Handle 'is future' date comparison"""
        date_obj = self._ensure_datetime(items[0])
        now = datetime.now(date_obj.tzinfo if date_obj.tzinfo else timezone.utc)
        return date_obj > now

    def date_is_today(self, items: list) -> bool:
        """Handle 'is today' date comparison"""
        date_obj = self._ensure_datetime(items[0])
        now = datetime.now(date_obj.tzinfo if date_obj.tzinfo else timezone.utc)
        return date_obj.date() == now.date()

    def date_within(self, items: list) -> bool:
        """Check if date is within a specified time period from now"""
        date_obj = self._ensure_datetime(items[0])
        quantity = int(items[1]) if hasattr(items[1], 'value') else items[1]
        unit = items[2].value if hasattr(items[2], 'value') else items[2]

        now = datetime.now(date_obj.tzinfo if date_obj.tzinfo else timezone.utc)
        delta = self._create_timedelta(quantity, unit)

        return abs(date_obj - now) <= delta

    def date_older_than(self, items: list) -> bool:
        """Check if date is older than a specified time period from now"""
        date_obj = self._ensure_datetime(items[0])
        quantity = int(items[1]) if hasattr(items[1], 'value') else items[1]
        unit = items[2].value if hasattr(items[2], 'value') else items[2]

        now = datetime.now(date_obj.tzinfo if date_obj.tzinfo else timezone.utc)
        delta = self._create_timedelta(quantity, unit)

        return (now - date_obj) > delta

    def date_before(self, items: list) -> bool:
        """Check if one date is before another"""
        date1 = self._ensure_datetime(items[0])
        date2 = self._ensure_datetime(items[1])
        return date1 < date2

    def date_after(self, items: list) -> bool:
        """Check if one date is after another"""
        date1 = self._ensure_datetime(items[0])
        date2 = self._ensure_datetime(items[1])
        return date1 > date2

    def date_same_day(self, items: list) -> bool:
        """Check if two dates are on the same calendar day"""
        date1 = self._ensure_datetime(items[0])
        date2 = self._ensure_datetime(items[1])
        return date1.date() == date2.date()

    # Unit methods
    def minute_unit(self, _) -> str:
        return "minute"

    def hour_unit(self, _) -> str:
        return "hour"

    def day_unit(self, _) -> str:
        return "day"

    def week_unit(self, _) -> str:
        return "week"

    def month_unit(self, _) -> str:
        return "month"

    def year_unit(self, _) -> str:
        return "year"

    # Helper methods
    def _ensure_datetime(self, value) -> datetime:
        """Convert value to datetime if it's not already"""
        if isinstance(value, datetime):
            return value
        elif isinstance(value, str):
            # Try different formats
            for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z"]:
                try:
                    dt = datetime.strptime(value, fmt)
                    # Make naive datetimes timezone-aware with UTC
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt
                except ValueError:
                    continue
            raise ValueError(f"Could not parse date string: {value}")
        elif isinstance(value, (int, float)):
            # Assume Unix timestamp
            return datetime.fromtimestamp(value, timezone.utc)
        else:
            raise TypeError(f"Cannot convert {type(value)} to datetime")

    def _create_timedelta(self, quantity, unit) -> timedelta:
        """Create a timedelta object based on quantity and unit"""
        # Now unit should be a simple string from one of our unit methods
        print(f"DEBUG - Unit received: {unit} (type: {type(unit)})")

        if unit == "minute":
            return timedelta(minutes=quantity)
        elif unit == "hour":
            return timedelta(hours=quantity)
        elif unit == "day":
            return timedelta(days=quantity)
        elif unit == "week":
            return timedelta(weeks=quantity)
        elif unit == "month":
            # Approximate month as 30 days
            return timedelta(days=30 * quantity)
        elif unit == "year":
            # Approximate year as 365 days
            return timedelta(days=365 * quantity)
        else:
            raise ValueError(f"Unsupported time unit: {unit}")