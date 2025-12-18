from typing import Dict, Any

from abc import ABC, abstractmethod

class ParamMapper(ABC):
    @classmethod
    @abstractmethod
    def map_parameters(cls, user_params: Dict[str, Any]):
        pass

    @classmethod
    def map_param(cls, key: str, mapper: Dict[str, Any]):
        return mapper[key]

    @classmethod
    def _map_date(cls, key: str, year: int):
        if key.startswith("from"):
            return [f"{year}-01-01"]
        return [f"{year}-12-31"]

    @classmethod
    def _map_list(cls, value: list):
        return [item.strip() for item in value if item and item.strip()]

    @classmethod
    def _map_str(cls, value: str):
        return [item.strip() for item in value.split(',') if item and item.strip()]

    @classmethod
    def _map_filter(cls, map_key: str, filter_value: Any):
        if map_key.endswith("date"):
            filters = cls._map_date(map_key, int(filter_value))

        # Обрабатываем список (например, collaboration_countries)
        elif isinstance(filter_value, list):
            # Фильтруем пустые значения
            filters = cls._map_list(filter_value)
            # Если список пустой, возвращаем пустую строку
            if not filters:
                return None

        # Обрабатываем строку (стандартный случай)
        elif isinstance(filter_value, str):
            # Фильтруем пустые значения
            filters = cls._map_str(filter_value)
            # Если список пустой, возвращаем пустую строку
            if not filters:
                return None

        # Обрабатываем другие типы (числа и т.д.)
        else:
            # Проверяем, что значение не None
            if filter_value is None:
                return None
            filters = [str(filter_value)]

        return f"{map_key}:{'|'.join(filters)}"