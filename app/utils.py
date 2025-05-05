import json
import os
from pathlib import Path


def get_json_path():
    return Path(__file__).parent.parent /'data.json'


def add_to_json(new_code: str):
    filename = get_json_path()

    if not (isinstance(new_code, str) and new_code.isdigit() and len(new_code) == 8):
        raise ValueError("Код должен быть 8-значной строкой из цифр")

    try:
        if filename.exists():
            with open(filename, 'r', encoding='utf-8') as f:
                codes = json.load(f)
        else:
            codes = []
    except json.JSONDecodeError:
        codes = []

    codes.append(new_code)

    temp_file = filename.with_suffix('.tmp')
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(codes, f, indent=4, ensure_ascii=False)

        temp_file.replace(filename)
        return True

    except Exception as e:
        if temp_file.exists():
            temp_file.unlink()
        raise


def get_last_code():
    filename = get_json_path()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            codes = json.load(f)
            return codes[-1] if codes else None
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def get_all_codes():
    filename = get_json_path()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []