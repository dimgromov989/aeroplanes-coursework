import pytest

from src.aeroplane import Aeroplane
from src.savers import JSONSaver


@pytest.fixture
def state_vectors():
    # Формат вектора состояния opensky-network: icao24, callsign, origin_country, time_position, last_contact,
    # longitude, latitude, baro_altitude, on_ground, velocity, true_track, vertical_rate, sensors,
    # geo_altitude, squawk, spi, position_source
    tail = [90.0, 0, None]
    return [
        ["4b1815", "SWR736  ", "Switzerland", 1, 1, 8.55, 47.45, 10972.8, False, 230.5, *tail, 11000.0, "1", False, 0],
        ["3c6444", "DLH9LF  ", "Germany", 1, 1, 9.0, 48.0, None, False, 180.0, *tail, 5000.0, "1", False, 0],
        ["a1b2c3", "", "United States", 1, 1, 9.0, 48.0, None, True, None, *tail, None, "1", False, 0],
        ["bad", "BAD1", None, 1, 1, 9.0, 48.0, 100.0, False, 10.0, *tail, 100.0, "1", False, 0],
    ]


@pytest.fixture
def aeroplanes():
    return [
        Aeroplane("UAL1621", "United States", 268.79, 10203.18, "a00001"),
        Aeroplane("IBE123", "Spain", 200.0, 8000.0, "340001"),
        Aeroplane("DLH456", "Germany", 250.0, 11000.0, "3c0001"),
        Aeroplane("VLG789", "Spain", 150.5, 3000.0, "340002"),
    ]


@pytest.fixture
def saver(tmp_path):
    return JSONSaver(str(tmp_path / "data" / "aeroplanes.json"))
