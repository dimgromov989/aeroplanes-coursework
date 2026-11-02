from unittest.mock import Mock, patch

import pytest
import requests

from src.api import AeroplanesAPI, APIError, BaseAPI

NOMINATIM_RESPONSE = [{"boundingbox": ["35.17", "43.99", "-18.39", "4.59"], "display_name": "España"}]


def make_response(json_data=None, status_code=200, json_error=False):
    response = Mock(status_code=status_code)
    if json_error:
        response.json.side_effect = ValueError("bad json")
    else:
        response.json.return_value = json_data
    return response


def test_base_api_is_abstract():
    with pytest.raises(TypeError):
        BaseAPI()
    assert issubclass(AeroplanesAPI, BaseAPI)


@patch("src.api.requests.get")
def test_get_country_bbox(mock_get):
    mock_get.return_value = make_response(NOMINATIM_RESPONSE)
    assert AeroplanesAPI().get_country_bbox(" Spain ") == (35.17, 43.99, -18.39, 4.59)
    args, kwargs = mock_get.call_args
    assert args[0] == AeroplanesAPI.NOMINATIM_URL
    assert kwargs["params"]["country"] == "Spain"
    assert "User-Agent" in kwargs["headers"]


@pytest.mark.parametrize("country", ["", "   ", None])
def test_get_country_bbox_empty_name(country):
    with pytest.raises(ValueError):
        AeroplanesAPI().get_country_bbox(country)


@patch("src.api.requests.get")
def test_get_country_bbox_not_found(mock_get):
    mock_get.return_value = make_response([])
    with pytest.raises(APIError, match="не найдена"):
        AeroplanesAPI().get_country_bbox("Narnia")


@patch("src.api.requests.get")
def test_get_country_bbox_bad_format(mock_get):
    mock_get.return_value = make_response([{"no_bbox": True}])
    with pytest.raises(APIError):
        AeroplanesAPI().get_country_bbox("Spain")


@patch("src.api.requests.get")
def test_get_aeroplanes(mock_get):
    states = [["4b1815", "SWR736", "Switzerland"]]
    mock_get.side_effect = [make_response(NOMINATIM_RESPONSE), make_response({"time": 1, "states": states})]
    assert AeroplanesAPI().get_aeroplanes("Spain") == states
    args, kwargs = mock_get.call_args
    assert args[0] == AeroplanesAPI.OPENSKY_URL
    assert kwargs["params"] == {"lamin": 35.17, "lamax": 43.99, "lomin": -18.39, "lomax": 4.59}


@patch("src.api.requests.get")
def test_get_aeroplanes_no_states(mock_get):
    mock_get.side_effect = [make_response(NOMINATIM_RESPONSE), make_response({"time": 1, "states": None})]
    assert AeroplanesAPI().get_aeroplanes("Spain") == []


@patch("src.api.requests.get")
def test_get_aeroplanes_bad_response(mock_get):
    mock_get.side_effect = [make_response(NOMINATIM_RESPONSE), make_response(["unexpected"])]
    with pytest.raises(APIError):
        AeroplanesAPI().get_aeroplanes("Spain")


@patch("src.api.requests.get")
def test_connect_errors(mock_get):
    api = AeroplanesAPI()
    mock_get.side_effect = requests.ConnectionError("no network")
    with pytest.raises(APIError, match="Не удалось подключиться"):
        api.get_country_bbox("Spain")

    mock_get.side_effect = None
    mock_get.return_value = make_response(status_code=429)
    with pytest.raises(APIError, match="429"):
        api.get_country_bbox("Spain")

    mock_get.return_value = make_response(json_error=True)
    with pytest.raises(APIError, match="JSON"):
        api.get_country_bbox("Spain")
