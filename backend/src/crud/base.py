# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
import json
from src.core.config import get_settings
from typing import TypeVar, Generic, Type

T = TypeVar("T")


class BaseCRUD(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model
        self.data_file = get_settings().DATA_FILE
        self._load_data()

    def _load_data(self):
        try:
            with open(self.data_file, "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {"conversations": [], "messages": []}
            self._save_data()

    def _save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.data, f, default=str)  # Handle datetime
