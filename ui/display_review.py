"""三年回顾：高三最后一课的全屏回顾模式（数据结构已就绪，逐年自动生长）。"""
import streamlit as st

from core import repo
from core.config import ROOT
from core.models import section_index
from core.repo import resolve_image_src
from ui.style import inject_base, ACCENT

inject_base()

data = repo.all_data()
nodes = sorted(data["timeline"].get("timeline", []),
               key=lambda n: (n.get("date", ""), n.get("week", 0)))
sidx = section_index(data["curriculum"])
images = data["images"].get("images", [])

st.markdown(
    """
    <div style="margin:.6rem 0 1rem">
      <div style="font-size:.8rem;letter-spacing:.3em;color:rgba(232,236,242,.45)">THREE-YEAR REVIEW</div>
      <h2 style="margin:.3rem 0 0">三年物理回顾</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

if not nodes:
    st.info("三年回顾会随时间线自动生长。第一节课的照片、章节与故事，都将在这里被记住。")
    st.stop()

if "review_idx" not in st.session_state:
    st.session_state.review_idx = 0
st.session_state.review_idx = max(0, min(st.session_state.review_idx, len(nodes) - 1))

node = nodes[st.session_state.review_idx]
chapter_names = " · ".join(
    sidx.get(cid, {}).get("chapter_name", cid) for cid in node.get("chapter_ids", []))
img = next((i for i in images
            if i.get("semester") == node.get("semester") and i.get("week") == node.get("week")), None)

progress = f"{st.session_state.review_idx + 1} / {len(nodes)}"
st.caption(f"一起走过的第 {progress} 周")

mc1, mc2 = st.columns([2, 1.2])
with mc1:
    st.markdown(f"### {node.get('date', '')} · {node.get('title', '')}")
    if chapter_names:
        st.caption(f"章节：{chapter_names}")
    if node.get("experiment"):
        st.markdown(f"**实验：** {node['experiment']}")
    if node.get("teacher_quote"):
        st.markdown(f"> {node['teacher_quote']}")
    photos = node.get("photos", [])
    if photos:
        pcols = st.columns(min(len(photos), 3))
        for pc, p in zip(pcols, photos):
            with pc:
                try:
                    st.image(ROOT / p if not p.startswith("http") else p,
                              width="stretch")
                except Exception:
                    pass
with mc2:
    if img:
        src = resolve_image_src(img)
        if src:
            try:
                st.image(src, width="stretch")
                st.caption(f"当周图片：{img['title']}")
            except Exception:
                pass

b1, b2, _ = st.columns([1, 1, 4])
if b1.button("← 上一周", disabled=st.session_state.review_idx <= 0):
    st.session_state.review_idx -= 1
    st.rerun()
if b2.button("下一周 →", disabled=st.session_state.review_idx >= len(nodes) - 1):
    st.session_state.review_idx += 1
    st.rerun()
