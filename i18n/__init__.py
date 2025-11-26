# i18n/__init__.py
import json
import os
from pathlib import Path

I18N_DIR = Path(__file__).parent
_current_lang = "zh"
_translations = {}

def get_available_languages():
    """自动扫描 i18n 目录，找出所有 .json 翻译文件（如 zh.json, en.json）"""
    lang_files = I18N_DIR.glob("*.json")
    langs = []
    for f in lang_files:
        name = f.stem  # 去掉 .json
        if name != "messages":  # 排除模板文件
            langs.append(name)
    return sorted(langs)

def _load_language(lang: str):
    lang_file = I18N_DIR / f"{lang}.json"
    if lang_file.exists():
        with open(lang_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def set_language(lang: str):
    global _current_lang, _translations
    _current_lang = lang
    _translations = _load_language(lang)

def get_language() -> str:
    return _current_lang

def tr(text: str) -> str:
    if _current_lang == "zh" and not _translations:
        return text
    return _translations.get(text, text)