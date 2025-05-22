import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List
from config import settings
from loguru import logger
import random


def _validate_code(code: str) -> bool:
    return isinstance(code, str) and code.isdigit() and len(code) == 8



class CodeManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_manager()
        return cls._instance

    def _init_manager(self):
        self._json_path = Path(__file__).parent / 'data.json'

    def add_code(self, new_code: str) -> bool:
        if not _validate_code(new_code):
            logger.error(f"Invalid code format: {new_code}")
            raise ValueError("Code must be 8-digit string")

        try:
            codes = self._load_codes()
            codes.append(new_code)
            self._save_codes(codes)
            logger.info(f"Code added: {new_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to add code: {e}")
            raise

    def generate_code(self) -> str:
        new_code = str(random.randint(10_000_000, 99_999_999))
        self.add_code(new_code)
        return new_code

    def is_valid_code(self, code: str) -> bool:
        return code in self.get_all_codes()

    def get_all_codes(self) -> List[str]:
        return self._load_codes()

    def _load_codes(self) -> List[str]:
        try:
            if self._json_path.exists():
                with open(self._json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to load codes: {e}")
            return []

    def _save_codes(self, codes: List[str]) -> bool:
        temp_file = self._json_path.with_suffix('.tmp')
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(codes, f, indent=4, ensure_ascii=False)
            temp_file.replace(self._json_path)
            return True
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            logger.error(f"Failed to save codes: {e}")
            raise

class CodeManagerFactory:
    @staticmethod
    def create_manager() -> CodeManager:
        return CodeManager()