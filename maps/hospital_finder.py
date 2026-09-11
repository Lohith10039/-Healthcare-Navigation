from math import asin, cos, radians, sin, sqrt
from typing import Any


# Demo data: verify operating hours and accessibility with the hospital.
HOSPITALS = [
    {
        "name": "Manipal Hospital, Old Airport Road",
        "address": "HAL Old Airport Road, Bengaluru",
        "latitude": 12.9592,
        "longitude": 77.6487,
        "emergency_available": True,
        "wheelchair_accessible": True,
    },
    {
        "name": "Apollo Hospitals, Bannerghatta Road",
        "address": "Bannerghatta Road, Bengaluru",
        "latitude": 12.8917,
        "longitude": 77.5987,
        "emergency_available": True,
        "wheelchair_accessible": True,
    },
    {
        "name": "Fortis Hospital, Bannerghatta Road",
        "address": "Bannerghatta Road, Bengaluru",
        "latitude": 12.8934,
        "longitude": 77.5972,
        "emergency_available": True,
        "wheelchair_accessible": True,
    },
    {
        "name": "Aster CMI Hospital",
        "address": "Hebbal, Bengaluru",
        "latitude": 13.0601,
        "longitude": 77.5990,
        "emergency_available": True,
        "wheelchair_accessible": True,
    },
    {
        "name": "Narayana Health City",
        "address": "Bommasandra, Bengaluru",
        "latitude": 12.8163,
        "longitude": 77.6915,
        "emergency_available": True,
        "wheelchair_accessible": True,
    },
]


def calculate_distance_km(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float,
) -> float:
    """Return straight-line distance between two points in kilometres."""
    earth_radius_km = 6371.0

    lat_diff = radians(latitude_2 - latitude_1)
    lon_diff = radians(longitude_2 - longitude_1)

    a = (
        sin(lat_diff / 2) ** 2
        + cos(radians(latitude_1))
        * cos(radians(latitude_2))
        * sin(lon_diff / 2) ** 2
    )

    return earth_radius_km * 2 * asin(sqrt(a))


def get_route_link(
    user_lat: float,
    user_lng: float,
    hospital_lat: float,
    hospital_lng: float,
) -> str:
    """Return a Google Maps directions link."""
    return (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={user_lat},{user_lng}"
        f"&destination={hospital_lat},{hospital_lng}"
        "&travelmode=driving"
    )


def find_nearby_hospitals(
    user_lat: float,
    user_lng: float,
    limit: int = 3,
    emergency_only: bool = True,
) -> list[dict[str, Any]]:
    """Return nearest hospitals with route and accessibility information."""
    results = []

    for hospital in HOSPITALS:
        if emergency_only and not hospital["emergency_available"]:
            continue

        distance_km = calculate_distance_km(
            user_lat,
            user_lng,
            hospital["latitude"],
            hospital["longitude"],
        )

        results.append(
            {
                **hospital,
                "distance_km": round(distance_km, 2),
                "route_url": get_route_link(
                    user_lat,
                    user_lng,
                    hospital["latitude"],
                    hospital["longitude"],
                ),
                "accessibility_note": (
                    "Wheelchair-friendly entrance listed. "
                    "Please confirm ramps, lifts, and curb access locally."
                    if hospital["wheelchair_accessible"]
                    else "Accessibility information unavailable; please call ahead."
                ),
            }
        )

    return sorted(results, key=lambda item: item["distance_km"])[:limit]


if __name__ == "__main__":
    # Example: Bengaluru city centre
    hospitals = find_nearby_hospitals(12.9716, 77.5946)

    for number, hospital in enumerate(hospitals, start=1):
        print(
            f"{number}. {hospital['name']} — {hospital['distance_km']} km\n"
            f"   Route: {hospital['route_url']}\n"
            f"   Accessibility: {hospital['accessibility_note']}\n"
        )
