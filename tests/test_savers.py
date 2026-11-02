import json

import pytest

from src.aeroplane import Aeroplane
from src.savers import BaseSaver, JSONSaver


def callsigns(planes):
    return [plane.callsign for plane in planes]


def test_base_saver_is_abstract():
    with pytest.raises(TypeError):
        BaseSaver()
    assert issubclass(JSONSaver, BaseSaver)


def test_default_filename():
    assert JSONSaver().filename.endswith("aeroplanes.json")


def test_add_and_get(saver, aeroplanes):
    saver.add_aeroplane(aeroplanes[0])
    saver.add_aeroplanes(aeroplanes)
    saver.add_aeroplane(aeroplanes[0])  # дубликат не добавляется
    assert callsigns(saver.get_aeroplanes()) == ["UAL1621", "IBE123", "DLH456", "VLG789"]
    with open(saver.filename, encoding="utf-8") as file:
        data = json.load(file)
    assert data[0] == aeroplanes[0].to_dict()


def test_add_without_icao24(saver):
    saver.add_aeroplanes([Aeroplane("A", "Spain", 1, 1), Aeroplane("A", "Spain", 2, 2), Aeroplane("A", "Italy", 1, 1)])
    assert len(saver.get_aeroplanes()) == 2


def test_add_wrong_type(saver):
    with pytest.raises(TypeError):
        saver.add_aeroplane({"callsign": "A"})


def test_get_by_criteria(saver, aeroplanes):
    saver.add_aeroplanes(aeroplanes)
    assert callsigns(saver.get_aeroplanes(country="spain")) == ["IBE123", "VLG789"]
    assert callsigns(saver.get_aeroplanes(callsign="dlh456")) == ["DLH456"]
    assert callsigns(saver.get_aeroplanes(min_altitude=8000, max_altitude=10500)) == ["UAL1621", "IBE123"]
    assert saver.get_aeroplanes(country="France") == []


def test_delete(saver, aeroplanes):
    saver.add_aeroplanes(aeroplanes)
    saver.delete_aeroplane(aeroplanes[1])
    assert callsigns(saver.get_aeroplanes()) == ["UAL1621", "DLH456", "VLG789"]
    saver.delete_aeroplane(Aeroplane("NONE", "Spain", 1, 1))
    assert len(saver.get_aeroplanes()) == 3


def test_clear_and_close(saver, aeroplanes):
    saver.add_aeroplanes(aeroplanes)
    saver.clear()
    assert saver.get_aeroplanes() == []
    assert saver.close() is None


def test_broken_or_missing_file(saver, tmp_path):
    assert saver.get_aeroplanes() == []
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    assert JSONSaver(str(broken)).get_aeroplanes() == []
    broken.write_text('{"a": 1}', encoding="utf-8")
    assert JSONSaver(str(broken)).get_aeroplanes() == []


def test_file_in_current_dir(tmp_path, monkeypatch, aeroplanes):
    monkeypatch.chdir(tmp_path)
    saver = JSONSaver("planes.json")
    saver.add_aeroplane(aeroplanes[0])
    assert len(saver.get_aeroplanes()) == 1
