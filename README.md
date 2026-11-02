# Самолеты в воздушном пространстве стран

Консольная программа, которая получает координаты страны через API
[nominatim.openstreetmap.org](https://nominatim.openstreetmap.org/), затем загружает информацию о самолетах
в этом прямоугольнике (`boundingbox`) через API [opensky-network.org](https://opensky-network.org/),
сохраняет данные в JSON-файл и позволяет фильтровать и сортировать их.

## Установка и запуск

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS
pip install -r requirements.txt
python main.py
```

## Возможности

1. Загрузить самолеты над страной (название страны вводит пользователь, например `Spain`)
2. Топ N самолетов по высоте полета (сортировка по убыванию)
3. Топ N самолетов по скорости (сортировка по убыванию)
4. Самолеты по стране регистрации (можно указать несколько стран через запятую)
5. Самолеты в диапазоне высот (формат `1000 - 5000`)
6. Показать все сохраненные самолеты
7. Удалить самолет по позывному
8. Очистить файл

Данные сохраняются в `data/aeroplanes.json`.

## Структура проекта

```
├── main.py              # функция user_interaction - взаимодействие с пользователем
├── src/
│   ├── api.py           # BaseAPI (ABC) и AeroplanesAPI - работа с nominatim и opensky
│   ├── aeroplane.py     # Aeroplane - самолет: валидация, инкапсуляция, сравнение
│   ├── savers.py        # BaseSaver (ABC) и JSONSaver - хранение в JSON-файле
│   └── utils.py         # фильтрация, сортировка, топ N, вывод
├── tests/               # тесты pytest
└── data/aeroplanes.json # пример выходных данных
```

## Классы

- **`BaseAPI`** — абстрактный класс (`ABC`) с абстрактными методами `_connect`, `get_country_bbox`, `get_aeroplanes`.
- **`AeroplanesAPI(BaseAPI)`** — получает `boundingbox` страны из nominatim и состояния самолетов из opensky.
  Ошибки сети, HTTP-статусы и некорректные ответы оборачиваются в `APIError`.
- **`Aeroplane`** — атрибуты: `icao24: str`, `callsign: str`, `country: str`, `velocity: float`, `altitude: float`,
  `on_ground: bool`. Атрибуты приватные (`__slots__`, доступ только на чтение через `property`), значения
  валидируются в конструкторе. Сравнение по высоте — операторами `<`, `<=`, `>`, `>=`, `==`, а также методами
  `is_higher` / `is_lower`; по скорости — методами `is_faster` / `is_slower`.
  `Aeroplane.cast_to_object_list` преобразует ответ opensky в список объектов, пропуская некорректные записи.
- **`BaseSaver`** — абстрактный класс-коннектор с методами `add_aeroplane`, `add_aeroplanes`, `get_aeroplanes`
  (по критериям), `delete_aeroplane`, `clear`; метод `close` — заглушка для будущего подключения к БД.
- **`JSONSaver(BaseSaver)`** — хранение в JSON-файле, без дубликатов, поиск по критериям
  `country`, `callsign`, `min_altitude`, `max_altitude`.

## Пример использования

```python
from src.aeroplane import Aeroplane
from src.api import AeroplanesAPI
from src.savers import JSONSaver
from src.utils import get_top_aeroplanes, print_aeroplanes, sort_aeroplanes

api = AeroplanesAPI()
aeroplanes = Aeroplane.cast_to_object_list(api.get_aeroplanes("Spain"))

aeroplane = Aeroplane("UAL1621", "United States", 268.79, 10203.18)

json_saver = JSONSaver()
json_saver.add_aeroplane(aeroplane)
json_saver.delete_aeroplane(aeroplane)

print_aeroplanes(get_top_aeroplanes(sort_aeroplanes(aeroplanes), 5))
```

## Тесты

```bash
pytest --cov=src --cov=main --cov-report=term-missing
```

Покрытие — 99%.
