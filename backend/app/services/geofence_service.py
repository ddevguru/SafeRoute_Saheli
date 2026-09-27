"""
SafeRoute Saheli — Automated Geo-Fence Safe Zone Guard & Battery Optimization Service
Manages user-defined safe havens (Home, Hostel, College Campus, Workplace).
Provides:
- Real-time circular geo-fence entry/exit detection via Haversine distance
- Curfew breach detection (late-night departure alerts to guardians)
- Autonomous power-saving battery management:
  - Inside Safe Zone: Throttle GPS to 120s (power saver)
  - Outside / In Transit: 25s regular tracking
  - Curfew Breach / High Alert: 10s tracking
"""

import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from backend.app.database import db
from backend.app.models.routing import SafeZone
from backend.app.models.guardian import GuardianUser, Guardian


class GeoFenceService:
    """Geo-fence monitoring and dynamic battery-saving scheduler"""

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Computes geodesic distance in meters between two lat/lon coordinates"""
        r = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r * c

    @classmethod
    def is_curfew_active(cls, start_hour: Optional[int], end_hour: Optional[int], current_hour: int) -> bool:
        """
        Determines whether the given hour falls inside the curfew window.
        Handles midnight rollover (e.g. 22:00 to 05:00).
        """
        if start_hour is None or end_hour is None:
            return False

        if start_hour > end_hour:
            # Over midnight window (e.g. 22:00 to 05:00)
            return current_hour >= start_hour or current_hour < end_hour
        else:
            # Same day window (e.g. 01:00 to 05:00)
            return start_hour <= current_hour < end_hour

    @classmethod
    def evaluate_position(
        cls,
        user_id: str,
        latitude: float,
        longitude: float,
        battery_percent: int = 100,
        current_dt: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Evaluates a user's current GPS position against all their registered Safe Zones.
        Returns safe zone status, power-saving recommendations, and curfew alerts.
        """
        now = current_dt or datetime.now(timezone.utc)
        current_hour = now.hour

        safe_zones = SafeZone.query.filter_by(user_id=user_id, is_active=True).all()

        active_zone = None
        min_distance = float('inf')
        nearest_zone = None

        for zone in safe_zones:
            dist = cls.haversine_distance(latitude, longitude, float(zone.latitude), float(zone.longitude))
            if dist < min_distance:
                min_distance = dist
                nearest_zone = zone

            if dist <= zone.radius_meters:
                active_zone = zone
                break

        is_inside_safe_zone = (active_zone is not None)

        # Curfew breach evaluation:
        # If user has a safe zone with curfew hours, and current time is in curfew,
        # but user is OUTSIDE all safe zones -> Curfew Breach!
        curfew_breached = False
        curfew_details = None

        if not is_inside_safe_zone and safe_zones:
            for zone in safe_zones:
                if zone.curfew_start_hour is not None and zone.curfew_end_hour is not None:
                    if cls.is_curfew_active(zone.curfew_start_hour, zone.curfew_end_hour, current_hour):
                        curfew_breached = True
                        curfew_details = {
                            "zone_name": zone.name,
                            "curfew_window": f"{zone.curfew_start_hour:02d}:00 - {zone.curfew_end_hour:02d}:00",
                            "current_hour": current_hour
                        }
                        break

        # Dynamic Battery Saving Calculations:
        # Inside Safe Zone: throttle GPS down to 120s (or 300s if critically low battery)
        # Outside Safe Zone: 25s normal
        # Curfew Breach: 10s high alert
        if is_inside_safe_zone:
            if battery_percent <= 15:
                recommended_gps_interval_ms = 300000  # 5 min sleep
                power_mode = "ULTRA_POWER_SAVING"
            else:
                recommended_gps_interval_ms = 120000  # 2 min
                power_mode = "SAFE_HAVEN_POWER_SAVING"
        elif curfew_breached:
            recommended_gps_interval_ms = 10000   # 10s high vigilance
            power_mode = "HIGH_ALERT_TRACKING"
        else:
            recommended_gps_interval_ms = 25000   # 25s normal transit
            power_mode = "STANDARD_TRANSIT"

        return {
            "status": "INSIDE_SAFE_ZONE" if is_inside_safe_zone else "OUTSIDE_SAFE_ZONE",
            "is_inside_safe_zone": is_inside_safe_zone,
            "active_safe_zone": active_zone.to_dict() if active_zone else None,
            "distance_to_nearest_zone_meters": round(min_distance, 1) if min_distance != float('inf') else None,
            "nearest_zone_name": nearest_zone.name if nearest_zone else None,
            "curfew_breached": curfew_breached,
            "curfew_details": curfew_details,
            "recommended_gps_interval_ms": recommended_gps_interval_ms,
            "battery_power_mode": power_mode,
            "battery_percent": battery_percent,
            "evaluated_at": now.isoformat()
        }
