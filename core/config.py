"""全局路径与常量。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
ASSETS_DIR = ROOT / "assets"
PHYSICS_IMAGE_DIR = ASSETS_DIR / "physics_images"
CLASS_MEMORY_DIR = ASSETS_DIR / "class_memories"

DATA_FILES = {
    "settings": "settings.json",
    "curriculum": "curriculum.json",
    "classes": "classes.json",
    "timeline": "timeline.json",
    "images": "physics_images.json",
    "events": "events.json",
    "questions": "questions.json",
}

TOPICS = ["力学", "电磁学", "热学", "光学", "近代物理", "天文学", "科学史", "实验", "课堂记忆"]

WEEKDAY_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
