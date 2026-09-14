"""学年/学期/教学周等日期计算，全部为纯函数。"""
from __future__ import annotations

from datetime import date, timedelta

from core.config import WEEKDAY_CN


def parse_d(s: str) -> date:
    return date.fromisoformat(s)


def today() -> date:
    """以 Asia/Shanghai 为准的「今天」，避免云端 UTC 日期偏差。"""
    from datetime import datetime
    from zoneinfo import ZoneInfo
    return datetime.now(ZoneInfo("Asia/Shanghai")).date()


def week_monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def semester_for(settings: dict, today: date) -> tuple[dict | None, bool]:
    """返回 (当前学期, 是否假期)。假期指今天不在任何学期区间内。"""
    sems = settings.get("semesters", [])
    for s in sems:
        if parse_d(s["start"]) <= today <= parse_d(s["end"]):
            return s, False
    past = [s for s in sems if parse_d(s["start"]) <= today]
    return (max(past, key=lambda s: s["start"]) if past else None), True


def teaching_week(settings: dict, today: date) -> int | None:
    """教学周序号；假期或学年前返回 None。自动扣除 holiday_weeks。"""
    sem, on_vacation = semester_for(settings, today)
    if sem is None or on_vacation:
        return None
    first = parse_d(sem.get("first_teaching_monday") or sem["start"])
    first = week_monday(first)
    naive = (week_monday(today) - first).days // 7 + 1
    if naive < 1:
        return None
    holidays = [week_monday(parse_d(x)) for x in settings.get("holiday_weeks", [])]
    skipped = sum(1 for h in holidays if h < week_monday(today))
    return max(naive - skipped, 1)


def next_exam(settings: dict, today: date) -> tuple[str, int] | None:
    """(考试名, 剩余天数)；没有未来的考试返回 None。"""
    exams = sorted(settings.get("exams", []), key=lambda e: e["date"])
    for e in exams:
        d = parse_d(e["date"])
        if d >= today:
            return e["name"], (d - today).days
    return None


def grade_name(settings: dict, today: date) -> str:
    gs = int(settings.get("site", {}).get("grade_start_year", today.year))
    # 学年从 9 月起算：2026 年 9 月入学，则 2026.9–2027.8 为高一
    n = today.year - gs if today.month >= 9 else today.year - gs - 1
    return {0: "高一", 1: "高二", 2: "高三"}.get(max(n, 0), "高三")


def semester_label(settings: dict, today: date) -> str:
    sem, on_vacation = semester_for(settings, today)
    grade = grade_name(settings, today)
    if sem is None:
        return f"{grade} · 未知学期"
    return f"{sem.get('name', '')}"


def semester_grade_label(settings: dict, today: date) -> str:
    """如：2026–2027 学年 · 高一上学期"""
    sem, _ = semester_for(settings, today)
    gs = int(settings.get("site", {}).get("grade_start_year", today.year))
    return f"{gs}–{gs + 1} 学年 · {semester_label(settings, today)}"


def today_label(today: date) -> str:
    return f"{today.year}.{today.month:02d}.{today.day:02d} {WEEKDAY_CN[today.weekday()]}"


def memories_for_today(timeline_nodes: list[dict], today: date, window: int = 3) -> list[tuple[dict, int]]:
    """历史同日期回忆：[(节点, 距今天数)]。"""
    out: list[tuple[dict, int]] = []
    for n in timeline_nodes:
        d = n.get("date")
        if not d:
            continue
        try:
            nd = parse_d(d)
        except ValueError:
            continue
        if nd.year >= today.year:
            continue
        delta = (today - nd).days
        # 同月日窗口匹配
        try:
            same_day_this_year = date(today.year, nd.month, nd.day)
        except ValueError:
            continue
        if abs((same_day_this_year - today).days) <= window:
            out.append((n, delta))
    return out
