"""首页：课堂大屏（16:9，一屏展示）。"""
import streamlit as st

from core import repo, school_year, stats
from core.config import WEEKDAY_CN
from ui.style import inject_base, inject_display

inject_base()
inject_display()

data = repo.all_data()
settings = data["settings"]
today = school_year.today()
week = school_year.teaching_week(settings, today)
exam = school_year.next_exam(settings, today)
grade = school_year.grade_name(settings, today)
counts = stats.compute(data)

# ---------- 顶栏 ----------
grade_label = school_year.semester_grade_label(settings, today)
week_html = f"WEEK {week}" if week else "假期中"
exam_html = (f"距{exam[0]} <span class='accent'>{exam[1]}</span> 天" if exam and exam[1] > 0
             else (f"{exam[0]} 加油" if exam else ""))
st.markdown(
    f"""
    <div class="pw-topbar">
        <div class="pw-brand">{settings.get('site', {}).get('title', '杨威的物理课堂')}
            <small>{settings.get('site', {}).get('subtitle', 'PHYSICS')}</small>
        </div>
        <div class="pw-spacer"></div>
        <div class="pw-top-item"><label>SEMESTER</label>{grade_label} · {grade}</div>
        <div class="pw-top-item"><label>WEEK</label><span class="accent">{week_html}</span></div>
        <div class="pw-top-item"><label>DATE</label>{school_year.today_label(today)}</div>
        <div class="pw-top-item"><label>COMING</label>{exam_html}</div>
        <div class="pw-top-item"><label>LESSONS</label>累计第 <span class="accent">{counts['lessons']}</span> 节物理课</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- 三班本周学习安排 ----------
cols = st.columns(3, gap="large")
for col, c in zip(cols, sorted(data["classes"].get("classes", []), key=lambda x: x.get("order", 0))):
    lessons = c.get("lessons", [])
    lessons_html = ""
    for ln in lessons:
        lessons_html += (
            f"<div class='pw-lesson'>"
            f"<div class='pw-lesson-head'>"
            f"<span class='pw-lesson-day'>{ln.get('day', '')}</span>"
            f"<span class='pw-lesson-no'>第{ln.get('lesson', '')}节</span>"
            f"</div>"
            f"<div class='pw-lesson-content'>{ln.get('content', '')}</div>"
            f"<div class='pw-lesson-task'>指南 → {ln.get('task', '')}</div>"
            f"</div>"
        )
    parts = [
        f"<div class='pw-class'>{c['name']}</div>",
        f"<div class='pw-theme'>{c.get('week_theme', '—')}</div>",
        f"<div class='pw-timeline'>{lessons_html or '—'}</div>",
    ]
    if c.get("note"):
        parts.append(f"<div class='pw-note'>{c['note']}</div>")
    with col:
        st.markdown(f"<div class='pw-card'>{''.join(parts)}</div>", unsafe_allow_html=True)

# ---------- 本周物理一图 ----------
st.markdown("<div style='height:.8vh'></div>", unsafe_allow_html=True)
img_col, txt_col = st.columns([1.15, 1], gap="large")
images = data["images"].get("images", [])
featured = next((i for i in images if i["id"] == settings.get("featured_image_id")), None)
if featured is None and images:
    featured = images[-1]

with img_col:
    if featured:
        src = featured.get("file") or featured.get("url")
        if src:
            try:
                st.image(src, width="stretch")
            except Exception:
                st.markdown("<div class='pw-imgmeta'>图片加载失败或待上传</div>",
                            unsafe_allow_html=True)

with txt_col:
    if featured:
        tags = " · ".join(featured.get("tags", []))
        st.markdown(
            f"""
            <div class="pw-weeklabel">PHYSICS IMAGE OF THE WEEK · 第 {featured.get('week', '—')} 周</div>
            <div class="pw-imgtitle">{featured['title']}</div>
            <div class="pw-imgmeta">{featured.get('topic', '')} {('· ' + tags) if tags else ''}
                ｜首次展示 {featured.get('first_shown', '—')}</div>
            <div class="pw-imgdesc">{featured.get('description', '')}</div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<div class='pw-weeklabel'>PHYSICS IMAGE OF THE WEEK</div>"
                    "<div class='pw-imgmeta'>本周图片待教师在后台上传</div>",
                    unsafe_allow_html=True)

# ---------- 物理年轮 ----------
stats_items = [
    ("LESSONS", counts["lessons"], "节物理课"),
    ("CONCEPTS", counts["concepts"], "个核心概念"),
    ("EXPERIMENTS", counts["experiments"], "次实验"),
    ("IMAGES", counts["images"], "张物理图片"),
    ("QUESTIONS", counts["questions"], "个课堂问题"),
    ("MEMORIES", counts["memories"], "条课堂记忆"),
]
st.markdown(
    "<div class='pw-stats'>" +
    "".join(f"<div class='pw-stat'><b>{v}</b><span>{label}</span></div>" for _, v, label in stats_items) +
    "</div>",
    unsafe_allow_html=True,
)

# ---------- 今日物理问题 ----------
questions = data["questions"].get("questions", [])
qid = settings.get("today_question_id")
q = next((x for x in questions if x["id"] == qid), None)
if q is None:
    q = next((x for x in questions if not x.get("used_on")), questions[0] if questions else None)
if q:
    st.markdown(
        f"""
        <div class="pw-question">
            <span class="tag">今日物理 · 想一个问题</span>
            <span class="txt">{q['text']}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------- 底部导航（低存在感） ----------
def _link(path: str, label: str):
    try:
        st.page_link(path, label=label)
    except KeyError:
        pass  # 脱离导航单独运行时（如测试环境）无页面注册表


st.markdown("<div class='pw-footer'></div>", unsafe_allow_html=True)
fcols = st.columns([1, 1, 1, 1, 1, 8])
with fcols[0]:
    _link("ui/display_curriculum.py", "课程地图")
with fcols[1]:
    _link("ui/display_timeline.py", "物理记忆")
with fcols[2]:
    _link("ui/display_gallery.py", "物理图鉴")
with fcols[3]:
    _link("ui/assistant.py", "AI 助教")
with fcols[4]:
    _link("ui/admin.py", "教师入口")
