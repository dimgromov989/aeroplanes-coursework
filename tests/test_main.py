from unittest.mock import Mock

import pytest

import main
from src.api import APIError


def run(monkeypatch, inputs, api=None, saver=None):
    answers = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _="": next(answers))
    main.user_interaction(api or Mock(), saver)


@pytest.fixture
def api(state_vectors):
    mock = Mock()
    mock.get_aeroplanes.return_value = state_vectors
    return mock


def test_load_and_show(monkeypatch, capsys, api, saver):
    run(monkeypatch, ["1", "Spain", "6", "0"], api, saver)
    out = capsys.readouterr().out
    api.get_aeroplanes.assert_called_once_with("Spain")
    assert "Найдено самолетов над страной 'Spain': 3" in out
    assert "SWR736" in out and "DLH9LF" in out
    assert "До свидания!" in out
    assert len(saver.get_aeroplanes()) == 3


def test_load_error(monkeypatch, capsys, saver):
    api = Mock()
    api.get_aeroplanes.side_effect = APIError("Страна 'Narnia' не найдена")
    run(monkeypatch, ["1", "Narnia", "0"], api, saver)
    assert "Ошибка: Страна 'Narnia' не найдена" in capsys.readouterr().out


def test_top_by_altitude_and_velocity(monkeypatch, capsys, saver, aeroplanes):
    saver.add_aeroplanes(aeroplanes)
    run(monkeypatch, ["2", "2", "0"], saver=saver)
    out = capsys.readouterr().out
    assert "1. DLH456" in out and "2. UAL1621" in out and "IBE123" not in out

    run(monkeypatch, ["3", "1", "0"], saver=saver)
    out = capsys.readouterr().out
    assert "1. UAL1621" in out and "DLH456" not in out


@pytest.mark.parametrize("value", ["abc", "0", "-3"])
def test_top_invalid_n(monkeypatch, capsys, saver, aeroplanes, value):
    saver.add_aeroplanes(aeroplanes)
    run(monkeypatch, ["2", value, "0"], saver=saver)
    assert "Ошибка:" in capsys.readouterr().out


def test_by_country(monkeypatch, capsys, saver, aeroplanes):
    saver.add_aeroplanes(aeroplanes)
    run(monkeypatch, ["4", "spain, Germany", "0"], saver=saver)
    out = capsys.readouterr().out
    assert "DLH456" in out and "IBE123" in out and "VLG789" in out and "UAL1621" not in out


def test_by_altitude(monkeypatch, capsys, saver, aeroplanes):
    saver.add_aeroplanes(aeroplanes)
    run(monkeypatch, ["5", "7000 - 10500", "5", "oops", "0"], saver=saver)
    out = capsys.readouterr().out
    assert "1. UAL1621" in out and "2. IBE123" in out and "VLG789" not in out
    assert "Ошибка:" in out


def test_delete_and_clear(monkeypatch, capsys, saver, aeroplanes):
    saver.add_aeroplanes(aeroplanes)
    run(monkeypatch, ["7", "ibe123", "7", "NOPE", "0"], saver=saver)
    out = capsys.readouterr().out
    assert "Удалено самолетов: 1" in out and "не найден" in out
    assert len(saver.get_aeroplanes()) == 3

    run(monkeypatch, ["8", "0"], saver=saver)
    assert "Файл очищен." in capsys.readouterr().out
    assert saver.get_aeroplanes() == []


def test_unknown_command(monkeypatch, capsys, saver):
    run(monkeypatch, ["42", "0"], saver=saver)
    assert "Неизвестная команда" in capsys.readouterr().out


def test_default_dependencies(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("builtins.input", lambda _="": "0")
    main.user_interaction()
    assert "До свидания!" in capsys.readouterr().out
