"""
Season Service - India cropping seasons (Kharif / Rabi / Zaid).

    Kharif = June - October
    Rabi   = November - March
    Zaid   = April - May
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple


class SeasonService:
    # month ranges (inclusive) for each Indian cropping season.
    SEASON_MONTHS: dict = {
        "Kharif": (6, 10),   # June - October
        "Rabi": (11, 3),     # November - March (wraps year boundary)
        "Zaid": (4, 5),      # April - May
    }

    SEASON_WINDOWS: dict = {
        "Kharif": "June - October (sown with onset of southwest monsoon)",
        "Rabi": "November - March (sown after monsoon, winter season)",
        "Zaid": "April - May (summer / short-duration crops)",
    }

    @staticmethod
    def get_current_season(month: Optional[int] = None) -> str:
        """Return the season name for the given month (defaults to today)."""
        if month is None:
            month = datetime.now().month

        for season, (start, end) in SeasonService.SEASON_MONTHS.items():
            if start <= end:
                if start <= month <= end:
                    return season
            else:
                # season wraps the year (e.g. Rabi Nov..Mar)
                if month >= start or month <= end:
                    return season
        # Defensive fallback (never expected).
        return "Kharif"

    @staticmethod
    def get_season_window(season: Optional[str] = None) -> str:
        if season is None:
            season = SeasonService.get_current_season()
        return SeasonService.SEASON_WINDOWS.get(season, "")

    @staticmethod
    def month_range(season: str) -> Tuple[int, int]:
        return SeasonService.SEASON_MONTHS.get(season, (6, 10))


# Module-level singleton.
season_service = SeasonService()