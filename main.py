from src.aeroplane import Aeroplane
from src.api import AeroplanesAPI, APIError, BaseAPI
from src.savers import BaseSaver, JSONSaver
from src.utils import (
    filter_aeroplanes,
    get_aeroplanes_by_altitude,
    get_top_aeroplanes,
    print_aeroplanes,
    sort_aeroplanes,
)

MENU = """
Выберите действие:
1 - Загрузить самолеты над страной (opensky-network.org)
2 - Топ N самолетов по высоте полета
3 - Топ N самолетов по скорости
4 - Самолеты по стране регистрации
5 - Самолеты в диапазоне высот
6 - Показать все сохраненные самолеты
7 - Удалить самолет по позывному
8 - Очистить файл
0 - Выход"""


def load_aeroplanes(api: BaseAPI, saver: BaseSaver) -> None:
    country = input("Введите название страны (например, Spain): ").strip()
    try:
        aeroplanes = Aeroplane.cast_to_object_list(api.get_aeroplanes(country))
    except (APIError, ValueError) as error:
        print(f"Ошибка: {error}")
        return
    saver.clear()
    saver.add_aeroplanes(aeroplanes)
    print(f"Найдено самолетов над страной '{country}': {len(aeroplanes)}. Данные сохранены.")


def ask_top_n() -> int:
    value = input("Введите количество самолетов для вывода в топ N: ").strip()
    try:
        return int(value)
    except ValueError:
        raise ValueError("N должно быть целым числом")


def show_top(saver: BaseSaver, by: str) -> None:
    try:
        top_n = ask_top_n()
        top = get_top_aeroplanes(sort_aeroplanes(saver.get_aeroplanes(), by), top_n)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return
    print_aeroplanes(top)


def show_by_country(saver: BaseSaver) -> None:
    countries = input("Введите страны регистрации через запятую (например, Spain, Germany): ").split(",")
    print_aeroplanes(sort_aeroplanes(filter_aeroplanes(saver.get_aeroplanes(), countries)))


def show_by_altitude(saver: BaseSaver) -> None:
    altitude_range = input("Введите диапазон высот в метрах (например, 1000 - 5000): ")
    try:
        aeroplanes = get_aeroplanes_by_altitude(saver.get_aeroplanes(), altitude_range)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return
    print_aeroplanes(sort_aeroplanes(aeroplanes))


def delete_by_callsign(saver: BaseSaver) -> None:
    callsign = input("Введите позывной самолета: ").strip()
    found = saver.get_aeroplanes(callsign=callsign)
    if not found:
        print(f"Самолет с позывным '{callsign}' не найден.")
        return
    for aeroplane in found:
        saver.delete_aeroplane(aeroplane)
    print(f"Удалено самолетов: {len(found)}")


def user_interaction(api: BaseAPI | None = None, saver: BaseSaver | None = None) -> None:
    """Взаимодействие с пользователем через консоль."""
    api = api or AeroplanesAPI()
    saver = saver or JSONSaver()

    actions = {
        "1": lambda: load_aeroplanes(api, saver),
        "2": lambda: show_top(saver, "altitude"),
        "3": lambda: show_top(saver, "velocity"),
        "4": lambda: show_by_country(saver),
        "5": lambda: show_by_altitude(saver),
        "6": lambda: print_aeroplanes(sort_aeroplanes(saver.get_aeroplanes())),
        "7": lambda: delete_by_callsign(saver),
        "8": lambda: (saver.clear(), print("Файл очищен.")),
    }

    print("Программа для поиска самолетов в воздушном пространстве стран")
    while True:
        print(MENU)
        choice = input("Ваш выбор: ").strip()
        if choice == "0":
            print("До свидания!")
            break
        action = actions.get(choice)
        if action is None:
            print("Неизвестная команда, попробуйте еще раз.")
            continue
        action()
    saver.close()


if __name__ == "__main__":
    user_interaction()
