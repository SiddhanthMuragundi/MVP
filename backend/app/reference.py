"""Reference geo/domain data shared across seeding, filtering and display."""
from __future__ import annotations

# City -> Indian state / UT. Covers every city used in the seed pools and metros, so a
# client's state can be derived from their city without storing a separate column.
CITY_STATE = {
    "Delhi": "Delhi",
    "Noida": "Uttar Pradesh",
    "Gurugram": "Haryana",
    "Jaipur": "Rajasthan",
    "Lucknow": "Uttar Pradesh",
    "Indore": "Madhya Pradesh",
    "Bhopal": "Madhya Pradesh",
    "Chennai": "Tamil Nadu",
    "Coimbatore": "Tamil Nadu",
    "Madurai": "Tamil Nadu",
    "Hyderabad": "Telangana",
    "Vijayawada": "Andhra Pradesh",
    "Visakhapatnam": "Andhra Pradesh",
    "Bengaluru": "Karnataka",
    "Mysuru": "Karnataka",
    "Mangaluru": "Karnataka",
    "Kochi": "Kerala",
    "Thiruvananthapuram": "Kerala",
    "Kozhikode": "Kerala",
    "Mumbai": "Maharashtra",
    "Pune": "Maharashtra",
    "Nagpur": "Maharashtra",
    "Nashik": "Maharashtra",
    "Kolkata": "West Bengal",
    "Howrah": "West Bengal",
    "Durgapur": "West Bengal",
    "Ahmedabad": "Gujarat",
    "Surat": "Gujarat",
    "Vadodara": "Gujarat",
    "Rajkot": "Gujarat",
    "Chandigarh": "Chandigarh",
    "Amritsar": "Punjab",
    "Ludhiana": "Punjab",
    "Jalandhar": "Punjab",
    "Goa": "Goa",
}

# Sorted unique states for filter dropdowns.
STATES = sorted(set(CITY_STATE.values()))

# Religions present in the studio (for filter dropdowns).
RELIGIONS = ["Hindu", "Muslim", "Christian", "Sikh", "Jain"]


def state_for(city: str | None) -> str | None:
    return CITY_STATE.get(city or "")


def cities_for_state(state: str) -> list[str]:
    return [city for city, st in CITY_STATE.items() if st == state]
