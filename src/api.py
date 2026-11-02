from abc import ABC, abstractmethod
from typing import Any

import requests


class APIError(Exception):
    """Ошибка при обращении к внешнему API."""


class BaseAPI(ABC):
    """Абстрактный класс для работы с API сервисов с самолетами."""

    @abstractmethod
    def _connect(self, url: str, params: dict[str, Any]) -> Any:
        """Подключается к API и возвращает распарсенный JSON-ответ."""

    @abstractmethod
    def get_country_bbox(self, country: str) -> tuple[float, float, float, float]:
        """Возвращает границы страны: (юг, север, запад, восток)."""

    @abstractmethod
    def get_aeroplanes(self, country: str) -> list[list[Any]]:
        """Возвращает список самолетов в воздушном пространстве страны."""


class AeroplanesAPI(BaseAPI):
    """Класс для работы с API nominatim.openstreetmap.org и opensky-network.org."""

    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    OPENSKY_URL = "https://opensky-network.org/api/states/all"
    HEADERS = {"User-Agent": "aeroplanes-coursework/1.0 (educational project)"}

    def __init__(self, timeout: int = 30) -> None:
        self.__timeout = timeout

    def _connect(self, url: str, params: dict[str, Any]) -> Any:
        try:
            response = requests.get(url, params=params, headers=self.HEADERS, timeout=self.__timeout)
        except requests.RequestException as error:
            raise APIError(f"Не удалось подключиться к {url}: {error}") from error

        if response.status_code != 200:
            raise APIError(f"Сервис {url} вернул ошибку {response.status_code}")

        try:
            return response.json()
        except ValueError as error:
            raise APIError(f"Сервис {url} вернул некорректный JSON") from error

    def get_country_bbox(self, country: str) -> tuple[float, float, float, float]:
        if not isinstance(country, str) or not country.strip():
            raise ValueError("Название страны не может быть пустым")

        data = self._connect(self.NOMINATIM_URL, {"country": country.strip(), "format": "json", "limit": 1})
        if not data:
            raise APIError(f"Страна '{country}' не найдена")

        try:
            south, north, west, east = (float(coord) for coord in data[0]["boundingbox"])
        except (KeyError, IndexError, TypeError, ValueError) as error:
            raise APIError("Не удалось получить координаты страны из ответа nominatim") from error
        return south, north, west, east

    def get_aeroplanes(self, country: str) -> list[list[Any]]:
        south, north, west, east = self.get_country_bbox(country)
        params = {"lamin": south, "lamax": north, "lomin": west, "lomax": east}
        data = self._connect(self.OPENSKY_URL, params)

        if not isinstance(data, dict):
            raise APIError("Некорректный ответ от opensky-network")
        return data.get("states") or []
