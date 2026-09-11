from maps.hospital_finder import find_nearby_hospitals, get_route_link


def test_find_nearby_hospitals_returns_three_results():
    hospitals = find_nearby_hospitals(12.9716, 77.5946)

    assert len(hospitals) == 3
    assert all("name" in hospital for hospital in hospitals)
    assert all("distance_km" in hospital for hospital in hospitals)
    assert all("route_url" in hospital for hospital in hospitals)


def test_hospitals_are_sorted_by_distance():
    hospitals = find_nearby_hospitals(12.9716, 77.5946)

    distances = [hospital["distance_km"] for hospital in hospitals]
    assert distances == sorted(distances)


def test_route_link_is_google_maps_url():
    route_url = get_route_link(12.9716, 77.5946, 12.9592, 77.6487)

    assert route_url.startswith("https://www.google.com/maps/dir/")
    assert "origin=12.9716,77.5946" in route_url
    assert "destination=12.9592,77.6487" in route_url
