import json
import os
from abc import ABC, abstractmethod
from typing import Any

from src.aeroplane import Aeroplane


class BaseSaver(ABC):
    """Абстрактный класс-коннектор к хранилищу информации о самолетах."""

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавляет самолет в хранилище."""

    @abstractmethod
    def add_aeroplanes(self, aeroplanes: list[Aeroplane]) -> None:
        """Добавляет несколько самолетов в хранилище."""

    @abstractmethod
    def get_aeroplanes(self, **criteria: Any) -> list[Aeroplane]:
        """Возвращает самолеты из хранилища, подходящие под критерии."""

    @abstractmethod
    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Удаляет самолет из хранилища."""

    @abstractmethod
    def clear(self) -> None:
        """Удаляет информацию обо всех самолетах."""

    def close(self) -> None:
        """Заглушка: закрытие соединения. Для файлов не нужно, пригодится для подключения к БД."""


class JSONSaver(BaseSaver):
    """Класс для сохранения информации о самолетах в JSON-файл."""

    def __init__(self, filename: str = os.path.join("data", "aeroplanes.json")) -> None:
        self.__filename = filename

    @property
    def filename(self) -> str:
        return self.__filename

    @staticmethod
    def __key(aeroplane: dict[str, Any]) -> tuple[str, ...]:
        if aeroplane.get("icao24"):
            return (aeroplane["icao24"],)
        return aeroplane.get("callsign", ""), aeroplane.get("country", "")

    def __read(self) -> list[dict[str, Any]]:
        try:
            with open(self.__filename, encoding="utf-8") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        return data if isinstance(data, list) else []

    def __write(self, data: list[dict[str, Any]]) -> None:
        directory = os.path.dirname(self.__filename)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(self.__filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        self.add_aeroplanes([aeroplane])

    def add_aeroplanes(self, aeroplanes: list[Aeroplane]) -> None:
        data = self.__read()
        existing = {self.__key(item) for item in data}
        for aeroplane in aeroplanes:
            if not isinstance(aeroplane, Aeroplane):
                raise TypeError("Сохранять можно только объекты Aeroplane")
            item = aeroplane.to_dict()
            if self.__key(item) not in existing:
                data.append(item)
                existing.add(self.__key(item))
        self.__write(data)

    def get_aeroplanes(self, **criteria: Any) -> list[Aeroplane]:
        """Критерии: country, callsign (без учета регистра), min_altitude, max_altitude."""
        result = []
        for aeroplane in Aeroplane.cast_to_object_list(self.__read()):
            if "country" in criteria and aeroplane.country.lower() != str(criteria["country"]).lower():
                continue
            if "callsign" in criteria and aeroplane.callsign.lower() != str(criteria["callsign"]).lower():
                continue
            if "min_altitude" in criteria and aeroplane.altitude < criteria["min_altitude"]:
                continue
            if "max_altitude" in criteria and aeroplane.altitude > criteria["max_altitude"]:
                continue
            result.append(aeroplane)
        return result

    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        key = self.__key(aeroplane.to_dict())
        self.__write([item for item in self.__read() if self.__key(item) != key])

    def clear(self) -> None:
        self.__write([])
