from typing import Any


class Aeroplane:
    """Класс для работы с информацией о самолете."""

    __slots__ = ("__icao24", "__callsign", "__country", "__velocity", "__altitude", "__on_ground")

    def __init__(
        self,
        callsign: str,
        country: str,
        velocity: float | None,
        altitude: float | None,
        icao24: str = "",
        on_ground: bool = False,
    ) -> None:
        self.__callsign: str = self.__validate_callsign(callsign)
        self.__country: str = self.__validate_country(country)
        self.__velocity: float = self.__validate_velocity(velocity)
        self.__altitude: float = self.__validate_altitude(altitude)
        self.__icao24: str = str(icao24).strip() if icao24 else ""
        self.__on_ground: bool = bool(on_ground)

    # --- валидация ---

    @staticmethod
    def __validate_callsign(callsign: Any) -> str:
        if callsign is None:
            return "Нет позывного"
        if not isinstance(callsign, str):
            raise TypeError("Позывной должен быть строкой")
        return callsign.strip() or "Нет позывного"

    @staticmethod
    def __validate_country(country: Any) -> str:
        if not isinstance(country, str):
            raise TypeError("Страна регистрации должна быть строкой")
        if not country.strip():
            raise ValueError("Страна регистрации не может быть пустой")
        return country.strip()

    @staticmethod
    def __validate_number(value: Any, name: str) -> float:
        if value is None:
            return 0.0
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} должна быть числом")
        return float(value)

    @classmethod
    def __validate_velocity(cls, velocity: Any) -> float:
        value = cls.__validate_number(velocity, "Скорость")
        if value < 0:
            raise ValueError("Скорость не может быть отрицательной")
        return value

    @classmethod
    def __validate_altitude(cls, altitude: Any) -> float:
        return cls.__validate_number(altitude, "Высота")

    # --- свойства (только чтение) ---

    @property
    def icao24(self) -> str:
        return self.__icao24

    @property
    def callsign(self) -> str:
        return self.__callsign

    @property
    def country(self) -> str:
        return self.__country

    @property
    def velocity(self) -> float:
        return self.__velocity

    @property
    def altitude(self) -> float:
        return self.__altitude

    @property
    def on_ground(self) -> bool:
        return self.__on_ground

    # --- сравнение по высоте (операторы) ---

    @staticmethod
    def __check_other(other: Any) -> None:
        if not isinstance(other, Aeroplane):
            raise TypeError("Сравнивать можно только самолеты между собой")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.__altitude == other.altitude

    def __lt__(self, other: "Aeroplane") -> bool:
        self.__check_other(other)
        return self.__altitude < other.altitude

    def __le__(self, other: "Aeroplane") -> bool:
        self.__check_other(other)
        return self.__altitude <= other.altitude

    def __gt__(self, other: "Aeroplane") -> bool:
        self.__check_other(other)
        return self.__altitude > other.altitude

    def __ge__(self, other: "Aeroplane") -> bool:
        self.__check_other(other)
        return self.__altitude >= other.altitude

    __hash__ = None  # type: ignore[assignment]

    # --- сравнение по скорости и высоте (методы) ---

    def is_faster(self, other: "Aeroplane") -> bool:
        """Летит ли самолет быстрее другого."""
        self.__check_other(other)
        return self.__velocity > other.velocity

    def is_slower(self, other: "Aeroplane") -> bool:
        """Летит ли самолет медленнее другого."""
        self.__check_other(other)
        return self.__velocity < other.velocity

    def is_higher(self, other: "Aeroplane") -> bool:
        """Летит ли самолет выше другого."""
        self.__check_other(other)
        return self.__altitude > other.altitude

    def is_lower(self, other: "Aeroplane") -> bool:
        """Летит ли самолет ниже другого."""
        self.__check_other(other)
        return self.__altitude < other.altitude

    # --- преобразования ---

    def to_dict(self) -> dict[str, Any]:
        return {
            "icao24": self.__icao24,
            "callsign": self.__callsign,
            "country": self.__country,
            "velocity": self.__velocity,
            "altitude": self.__altitude,
            "on_ground": self.__on_ground,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Aeroplane":
        return cls(
            callsign=data.get("callsign"),  # type: ignore[arg-type]
            country=data.get("country"),  # type: ignore[arg-type]
            velocity=data.get("velocity"),
            altitude=data.get("altitude"),
            icao24=data.get("icao24", ""),
            on_ground=data.get("on_ground", False),
        )

    @classmethod
    def from_state(cls, state: list[Any]) -> "Aeroplane":
        """Создает самолет из вектора состояния opensky-network.

        Индексы: 0 - icao24, 1 - позывной, 2 - страна регистрации, 7 - барометрическая высота,
        8 - на земле, 9 - скорость, 13 - геометрическая высота.
        """
        altitude = state[7] if state[7] is not None else state[13]
        return cls(
            callsign=state[1],
            country=state[2],
            velocity=state[9],
            altitude=altitude,
            icao24=state[0],
            on_ground=state[8],
        )

    @classmethod
    def cast_to_object_list(cls, data: list[Any]) -> list["Aeroplane"]:
        """Преобразует список состояний (или словарей) в список объектов. Некорректные записи пропускаются."""
        aeroplanes = []
        for item in data or []:
            try:
                if isinstance(item, dict):
                    aeroplanes.append(cls.from_dict(item))
                else:
                    aeroplanes.append(cls.from_state(item))
            except (TypeError, ValueError, IndexError):
                continue
        return aeroplanes

    def __repr__(self) -> str:
        return (
            f"Aeroplane({self.__callsign!r}, {self.__country!r}, {self.__velocity}, "
            f"{self.__altitude}, icao24={self.__icao24!r}, on_ground={self.__on_ground})"
        )

    def __str__(self) -> str:
        status = "на земле" if self.__on_ground else "в воздухе"
        return (
            f"{self.__callsign:<10} | {self.__country:<20} | "
            f"скорость: {self.__velocity:7.2f} м/с | высота: {self.__altitude:9.2f} м | {status}"
        )
