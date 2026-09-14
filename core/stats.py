"""物理年轮统计：全部由数据推导，不手工维护。"""
from __future__ import annotations

from core.models import section_index


def compute(data: dict) -> dict:
    classes = data.get("classes", {}).get("classes", [])
    curriculum = data.get("curriculum", {})
    timeline = data.get("timeline", {}).get("timeline", [])
    images = data.get("images", {}).get("images", [])
    events = data.get("events", {}).get("events", [])
    questions = data.get("questions", {}).get("questions", [])

    sidx = section_index(curriculum)
    concepts: set[str] = set()
    for c in classes:
        # 从 lessons 的 content 统计本周涉及的主题
        for item in c.get("lessons", []):
            t = item.get("content", "")
            if t:
                concepts.add(t)
        # 向后兼容旧字段
        for item in c.get("weekly_plan", []):
            if item.get("status") in ("done", "current"):
                t = item.get("title", "")
                if t:
                    concepts.add(t)
        for sid in c.get("done", []):
            for cp in sidx.get(sid, {}).get("core_concepts", []) or [sidx.get(sid, {}).get("name", "")]:
                if cp:
                    concepts.add(cp)

    return {
        "lessons": sum(int(c.get("lesson_count", 0)) for c in classes),
        "concepts": len(concepts),
        "experiments": sum(1 for n in timeline if n.get("experiment")),
        "images": len(images),
        "questions": sum(1 for q in questions if q.get("used_on")),
        "memories": len(events),
    }
