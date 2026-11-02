from src.aeroplane import Aeroplane


def filter_aeroplanes(aeroplanes: list[Aeroplane], countries: list[str]) -> list[Aeroplane]:
    """Оставляет самолеты, зарегистрированные в указанных странах (без учета регистра).

    Если список стран пуст, возвращаются все самолеты.
    """
    names = {country.strip().lower() for country in countries if country.strip()}
    if not names:
        return list(aeroplanes)
    return [aeroplane for aeroplane in aeroplanes if aeroplane.country.lower() in names]


def parse_altitude_range(altitude_range: str) -> tuple[float, float]:
    """Разбирает строку вида '1000 - 5000' в кортеж (min, max)."""
    parts = altitude_range.split("-")
    if len(parts) != 2:
        raise ValueError("Диапазон высот должен иметь формат 'мин - макс', например: 1000 - 5000")
    try:
        low, high = float(parts[0]), float(parts[1])
    except ValueError as error:
        raise ValueError("Границы диапазона высот должны быть числами") from error
    if low > high:
        raise ValueError("Нижняя граница диапазона не может быть больше верхней")
    return low, high


def get_aeroplanes_by_altitude(aeroplanes: list[Aeroplane], altitude_range: str) -> list[Aeroplane]:
    """Оставляет самолеты в диапазоне высот. Пустая строка - без фильтрации."""
    if not altitude_range.strip():
        return list(aeroplanes)
    low, high = parse_altitude_range(altitude_range)
    return [aeroplane for aeroplane in aeroplanes if low <= aeroplane.altitude <= high]


def sort_aeroplanes(aeroplanes: list[Aeroplane], by: str = "altitude") -> list[Aeroplane]:
    """Сортирует самолеты по убыванию высоты ('altitude') или скорости ('velocity')."""
    if by == "altitude":
        return sorted(aeroplanes, reverse=True)
    if by == "velocity":
        return sorted(aeroplanes, key=lambda aeroplane: aeroplane.velocity, reverse=True)
    raise ValueError("Сортировать можно только по 'altitude' или 'velocity'")


def get_top_aeroplanes(aeroplanes: list[Aeroplane], top_n: int) -> list[Aeroplane]:
    """Возвращает первые N самолетов."""
    if not isinstance(top_n, int) or isinstance(top_n, bool) or top_n <= 0:
        raise ValueError("N должно быть положительным целым числом")
    return aeroplanes[:top_n]


def print_aeroplanes(aeroplanes: list[Aeroplane]) -> None:
    """Выводит самолеты в консоль в читаемом виде."""
    if not aeroplanes:
        print("Самолеты не найдены.")
        return
    for number, aeroplane in enumerate(aeroplanes, start=1):
        print(f"{number:>3}. {aeroplane}")
    print(f"Всего: {len(aeroplanes)}")
