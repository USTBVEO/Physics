"""物理记忆：三年时间线 + 历史回忆。"""
import streamlit as st

from core import repo, school_year
from core.models import section_index
from ui.style import inject_base, ACCENT

inject_base()

data = repo.all_data()
nodes = sorted(data["timeline"].get("timeline", []), key=lambda n: (n.get("date", ""), n.get("week", 0)),
               reverse=True)
sidx = section_index(data["curriculum"])
today = school_year.today()

# ---------- 历史回忆 ----------
memories = school_year.memories_for_today(data["timeline"].get("timeline", []), today)
if memories:
    for node, delta in memories[:2]:
        st.info(f"{delta} 天前的今天，我们正在学习「{node.get('title', '')}」。", icon="⏳")

st.markdown(
    """
    <div style="margin:.6rem 0 1rem">
      <div style="font-size:.8rem;letter-spacing:.3em;color:rgba(232,236,242,.45)">PHYSICS MEMORIES</div>
      <h2 style="margin:.3rem 0 0">物理记忆 · 时间线</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

images = data["images"].get("images", [])
events = {e["id"]: e for e in data["events"].get("events", [])}

if not nodes:
    st.caption("时间线还没有内容，等待第一周的课程记录。")
    st.stop()

for node in nodes:
    chapter_names = " · ".join(
        sidx.get(cid, {}).get("chapter_name", cid) for cid in node.get("chapter_ids", []))
    linked = [events[eid] for eid in node.get("events", []) if eid in events]
    img = next((i for i in images
                if i.get("semester") == node.get("semester") and i.get("week") == node.get("week")), None)

    with st.container(border=True):
        head_l, head_r = st.columns([3, 1])
        with head_l:
            st.markdown(
                f"<div style='font-size:.75rem;letter-spacing:.3em;color:{ACCENT}'>"
                f"{node.get('date', '')} · WEEK {node.get('week', '—')}</div>"
                f"<div style='font-size:1.35rem;font-weight:650;margin-top:.2rem'>"
                f"{node.get('title', '')}</div>",
                unsafe_allow_html=True)
        if img:
            with head_r:
                src = img.get("file") or img.get("url")
                if src:
                    try:
                        st.image(src, width="stretch")
                    except Exception:
                        pass
        if chapter_names:
            st.caption(f"章节：{chapter_names}")
        if node.get("experiment"):
            st.markdown(f"**本周实验：** {node['experiment']}")
        if node.get("teacher_quote"):
            st.markdown(f"> {node['teacher_quote']}")
        for e in linked:
            st.markdown(f"**事件：** {e['title']}（{e.get('date', '')}）— {e.get('description', '')}")
        photos = node.get("photos", [])
        if photos:
            pcols = st.columns(min(len(photos), 4))
            for pc, p in zip(pcols, photos):
                with pc:
                    try:
                        st.image(p, width="stretch")
                    except Exception:
                        pass
