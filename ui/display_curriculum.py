"""课程地图：三年学习路径 + 各班完成状态。"""
import streamlit as st

from core import repo, school_year
from core.models import ordered_section_ids
from ui.style import inject_base, ACCENT

inject_base()

data = repo.all_data()
settings = data["settings"]
classes = sorted(data["classes"].get("classes", []), key=lambda x: x.get("order", 0))
today = school_year.today()

if not classes:
    st.warning("暂无班级数据。")
    st.stop()

names = [c["name"] for c in classes]
sel = st.radio("选择班级", names, horizontal=True)
cls = next(c for c in classes if c["name"] == sel)
done = set(cls.get("done", []))

order = ordered_section_ids(data["curriculum"])
next_id = next((sid for sid in order if sid not in done), None)

st.markdown(
    f"""
    <div style="margin:1.2rem 0 0">
      <div style="font-size:.8rem;letter-spacing:.3em;color:rgba(232,236,242,.45)">
        {school_year.semester_grade_label(settings, today)} · 学习路径</div>
      <h2 style="margin:.3rem 0 0">{sel} · 我们现在在这里</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

for grade in data["curriculum"].get("grades", []):
    st.markdown(f"### {grade['grade']} · {grade['textbook']}")
    for ch in grade.get("chapters", []):
        rows = []
        ch_done = 0
        for s in ch.get("sections", []):
            sid, name = s["id"], s["name"]
            if sid in done:
                ch_done += 1
                rows.append(f"<span style='color:rgba(232,236,242,.4)'>✓ {name}</span>")
            elif sid == next_id:
                rows.append(
                    f"<span style='color:{ACCENT};font-weight:600'>→ {name}"
                    f"　<span style='font-size:.75rem;letter-spacing:.2em'>我们在这里</span></span>")
            else:
                rows.append(f"<span style='color:rgba(232,236,242,.75)'>○ {name}</span>")
        n = len(ch.get("sections", []))
        head = (f"<div style='display:flex;align-items:baseline;gap:.8rem;margin:1.1rem 0 .4rem'>"
                f"<span style='font-size:1.05rem;font-weight:600'>{ch['name']}</span>"
                f"<span style='font-size:.75rem;color:rgba(232,236,242,.4)'>{ch_done}/{n}</span></div>")
        body = "<div style='display:flex;flex-direction:column;gap:.35rem;font-size:.95rem'>" + \
            "".join(f"<div>{r}</div>" for r in rows) + "</div>"
        st.markdown(head + body, unsafe_allow_html=True)

st.caption("✓ 已完成　→ 当前进行到　○ 待学习（进度来自教师后台每周更新）")
