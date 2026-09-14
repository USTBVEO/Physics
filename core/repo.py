"""数据读写门面：UI 层只调用这里，不直接碰文件。"""
from __future__ import annotations

import json

import streamlit as st

from core.config import DATA_DIR, DATA_FILES
from core.store import get_store

_DEFAULTS: dict[str, dict] = {
    "settings": {}, "curriculum": {}, "classes": {}, "timeline": {},
    "images": {}, "events": {}, "questions": {},
}


@st.cache_data(ttl=5)
def _cached_read(rel_path: str) -> dict:
    p = DATA_DIR / rel_path
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load(key: str) -> dict:
    return _cached_read(DATA_FILES[key])


def all_data() -> dict[str, dict]:
    return {k: load(k) for k in DATA_FILES}


def save(key: str, data: dict, label: str) -> tuple[bool, str]:
    from datetime import date
    msg = f"后台: {label} ({date.today().isoformat()})"
    ok, detail = get_store().save_json(DATA_FILES[key], data, msg)
    _cached_read.clear()
    return ok, detail


def save_binary(rel_path: str, content: bytes, label: str) -> tuple[bool, str]:
    from datetime import date
    msg = f"后台: {label} ({date.today().isoformat()})"
    ok, detail = get_store().save_binary(rel_path, content, msg)
    _cached_read.clear()
    return ok, detail


def store_name() -> str:
    return get_store().name
