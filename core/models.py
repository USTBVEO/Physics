"""数据模型：与 data/*.json 一一对应，只做薄封装。"""
from __future__ import annotations

import dataclasses as _dc
from dataclasses import dataclass, field, asdict


def _from_dict(cls, d: dict):
    allowed = {f.name for f in _dc.fields(cls)}
    return cls(**{k: v for k, v in d.items() if k in allowed})


@dataclass
class ClassProgress:
    id: str
    name: str
    order: int = 0
    week_theme: str = ""
    lesson_count: int = 0
    note: str = ""
    lessons: list[dict] = field(default_factory=list)  # [{lesson, day, content, task}]
    # 向后兼容旧字段
    class_days: list[str] = field(default_factory=list)
    today: str = ""
    weekly_plan: list[dict] = field(default_factory=list)
    weekly_tasks: list[dict] = field(default_factory=list)
    done: list[str] = field(default_factory=list)
    next_lesson: str = ""
    experiment: str = ""
    week_experiment: str = ""
    progress: float = 0.0

    @classmethod
    def from_dict(cls, d: dict) -> "ClassProgress":
        return _from_dict(cls, d)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PhysicsImage:
    id: str
    title: str
    file: str = ""            # 仓库内相对路径，如 assets/physics_images/2026/w03.jpg
    url: str = ""             # 外链（file 优先）
    description: str = ""
    topic: str = ""
    chapter_id: str = ""
    tags: list[str] = field(default_factory=list)
    semester: str = ""
    week: int = 0
    first_shown: str = ""     # 首次展示日期 YYYY-MM-DD
    teacher_note: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "PhysicsImage":
        return _from_dict(cls, d)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TimelineNode:
    id: str                   # 如 w2026s1-03
    semester: str
    week: int
    date: str = ""            # 该周周一日期
    title: str = ""
    chapter_ids: list[str] = field(default_factory=list)
    experiment: str = ""
    events: list[str] = field(default_factory=list)   # 关联 event id
    photos: list[str] = field(default_factory=list)   # 课堂照片路径
    teacher_quote: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "TimelineNode":
        return _from_dict(cls, d)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EventRecord:
    id: str
    date: str
    type: str = "其他"        # 第一次/考试/竞赛/公开课/趣事/学生作品/学期/学年/其他
    title: str = ""
    description: str = ""
    class_ids: list[str] = field(default_factory=list)
    photos: list[str] = field(default_factory=list)
    teacher_note: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "EventRecord":
        return _from_dict(cls, d)

    def to_dict(self) -> dict:
        return asdict(self)


def section_index(curriculum: dict) -> dict[str, dict]:
    """小节 id -> {name, chapter_id, chapter_name, grade, core_concepts} 的全局索引。"""
    idx: dict[str, dict] = {}
    for grade in curriculum.get("grades", []):
        for ch in grade.get("chapters", []):
            for s in ch.get("sections", []):
                idx[s["id"]] = {
                    **s,
                    "chapter_id": ch["id"],
                    "chapter_name": ch["name"],
                    "grade": grade.get("grade"),
                    "textbook": grade.get("textbook"),
                }
    return idx


def ordered_section_ids(curriculum: dict) -> list[str]:
    """按课程顺序展平的小节 id 列表。"""
    out: list[str] = []
    for grade in curriculum.get("grades", []):
        for ch in grade.get("chapters", []):
            out += [s["id"] for s in ch.get("sections", [])]
    return out
