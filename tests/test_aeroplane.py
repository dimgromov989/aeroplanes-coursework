import pytest

from src.aeroplane import Aeroplane


def test_init_and_properties():
    plane = Aeroplane(" UAL1621 ", "United States", 268.79, 10203, "a00001", False)
    assert plane.callsign == "UAL1621"
    assert plane.country == "United States"
    assert plane.velocity == 268.79
    assert plane.altitude == 10203.0
    assert isinstance(plane.altitude, float)
    assert plane.icao24 == "a00001"
    assert plane.on_ground is False


def test_defaults_for_missing_values():
    plane = Aeroplane(None, "Spain", None, None)
    assert plane.callsign == "Нет позывного"
    assert plane.velocity == 0.0
    assert plane.altitude == 0.0
    assert plane.icao24 == ""
    assert Aeroplane("   ", "Spain", 1, 1).callsign == "Нет позывного"


@pytest.mark.parametrize(
    "args, error",
    [
        ((123, "Spain", 1, 1), TypeError),
        (("A", None, 1, 1), TypeError),
        (("A", "  ", 1, 1), ValueError),
        (("A", "Spain", "fast", 1), TypeError),
        (("A", "Spain", True, 1), TypeError),
        (("A", "Spain", -5, 1), ValueError),
        (("A", "Spain", 1, "high"), TypeError),
    ],
)
def test_validation(args, error):
    with pytest.raises(error):
        Aeroplane(*args)


def test_attributes_are_encapsulated():
    plane = Aeroplane("A", "Spain", 1, 1)
    with pytest.raises(AttributeError):
        plane.altitude = 5
    with pytest.raises(AttributeError):
        plane.new_attr = 5


def test_compare_by_altitude():
    low = Aeroplane("LOW", "Spain", 300, 1000)
    high = Aeroplane("HIGH", "Spain", 100, 9000)
    same = Aeroplane("SAME", "Spain", 50, 1000)
    assert low < high and high > low
    assert low <= same and low >= same and low == same
    assert low != high
    assert high.is_higher(low) and low.is_lower(high)
    assert not low.is_higher(same)


def test_compare_by_velocity():
    slow = Aeroplane("SLOW", "Spain", 100, 9000)
    fast = Aeroplane("FAST", "Spain", 300, 1000)
    assert fast.is_faster(slow) and slow.is_slower(fast)
    assert not slow.is_faster(fast)


def test_compare_with_other_type():
    plane = Aeroplane("A", "Spain", 1, 1)
    assert plane != 1
    operations = (plane.__lt__, plane.__le__, plane.__gt__, plane.__ge__,
                  plane.is_faster, plane.is_slower, plane.is_higher, plane.is_lower)
    for operation in operations:
        with pytest.raises(TypeError):
            operation(1)


def test_dict_roundtrip():
    plane = Aeroplane("A", "Spain", 1.5, 2.5, "abc", True)
    data = plane.to_dict()
    assert data == {"icao24": "abc", "callsign": "A", "country": "Spain", "velocity": 1.5,
                    "altitude": 2.5, "on_ground": True}
    assert Aeroplane.from_dict(data).to_dict() == data


def test_from_state_uses_geo_altitude_as_fallback(state_vectors):
    plane = Aeroplane.from_state(state_vectors[1])
    assert plane.callsign == "DLH9LF"
    assert plane.altitude == 5000.0
    assert Aeroplane.from_state(state_vectors[0]).altitude == 10972.8


def test_cast_to_object_list_skips_invalid(state_vectors):
    planes = Aeroplane.cast_to_object_list(state_vectors + [[1, 2], {"country": ""}])
    assert [plane.icao24 for plane in planes] == ["4b1815", "3c6444", "a1b2c3"]
    assert planes[2].on_ground is True
    assert Aeroplane.cast_to_object_list(None) == []
    assert len(Aeroplane.cast_to_object_list([{"callsign": "A", "country": "Spain"}])) == 1


def test_str_and_repr():
    plane = Aeroplane("UAL1621", "United States", 268.79, 10203.18)
    text = str(plane)
    assert "UAL1621" in text and "United States" in text and "268.79" in text and "в воздухе" in text
    assert "на земле" in str(Aeroplane("A", "Spain", 0, 0, on_ground=True))
    assert repr(plane).startswith("Aeroplane('UAL1621'")
