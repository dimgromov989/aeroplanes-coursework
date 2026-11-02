import pytest

from src.utils import (
    filter_aeroplanes,
    get_aeroplanes_by_altitude,
    get_top_aeroplanes,
    parse_altitude_range,
    print_aeroplanes,
    sort_aeroplanes,
)


def callsigns(planes):
    return [plane.callsign for plane in planes]


def test_filter_aeroplanes(aeroplanes):
    assert callsigns(filter_aeroplanes(aeroplanes, ["spain", " Germany "])) == ["IBE123", "DLH456", "VLG789"]
    assert filter_aeroplanes(aeroplanes, ["France"]) == []
    assert len(filter_aeroplanes(aeroplanes, [])) == 4
    assert len(filter_aeroplanes(aeroplanes, ["", "  "])) == 4


@pytest.mark.parametrize("text, expected", [("1000 - 5000", (1000.0, 5000.0)), ("0-10.5", (0.0, 10.5))])
def test_parse_altitude_range(text, expected):
    assert parse_altitude_range(text) == expected


@pytest.mark.parametrize("text", ["1000", "a - b", "5000 - 1000", "1-2-3"])
def test_parse_altitude_range_errors(text):
    with pytest.raises(ValueError):
        parse_altitude_range(text)


def test_get_aeroplanes_by_altitude(aeroplanes):
    assert callsigns(get_aeroplanes_by_altitude(aeroplanes, "3000 - 8000")) == ["IBE123", "VLG789"]
    assert len(get_aeroplanes_by_altitude(aeroplanes, "  ")) == 4
    with pytest.raises(ValueError):
        get_aeroplanes_by_altitude(aeroplanes, "abc")


def test_sort_aeroplanes_desc(aeroplanes):
    assert callsigns(sort_aeroplanes(aeroplanes)) == ["DLH456", "UAL1621", "IBE123", "VLG789"]
    assert callsigns(sort_aeroplanes(aeroplanes, "velocity")) == ["UAL1621", "DLH456", "IBE123", "VLG789"]
    with pytest.raises(ValueError):
        sort_aeroplanes(aeroplanes, "name")


def test_get_top_aeroplanes(aeroplanes):
    assert callsigns(get_top_aeroplanes(sort_aeroplanes(aeroplanes), 2)) == ["DLH456", "UAL1621"]
    assert len(get_top_aeroplanes(aeroplanes, 100)) == 4


@pytest.mark.parametrize("n", [0, -1, "2", 1.5, True])
def test_get_top_aeroplanes_invalid(aeroplanes, n):
    with pytest.raises(ValueError):
        get_top_aeroplanes(aeroplanes, n)


def test_print_aeroplanes(aeroplanes, capsys):
    print_aeroplanes(aeroplanes[:2])
    out = capsys.readouterr().out
    assert "1. UAL1621" in out and "2. IBE123" in out and "Всего: 2" in out
    print_aeroplanes([])
    assert "Самолеты не найдены" in capsys.readouterr().out
