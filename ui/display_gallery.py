"""物理图鉴：长期积累的物理图片库，按主题/标签筛选，大图浏览。"""
import streamlit as st

from core import repo
from core.repo import resolve_image_src
from ui.style import inject_base

inject_base()

data = repo.all_data()
images = data["images"].get("images", [])

st.markdown(
    """
    <div style="margin:.6rem 0 1rem">
      <div style="font-size:.8rem;letter-spacing:.3em;color:rgba(232,236,242,.45)">PHYSICS GALLERY</div>
      <h2 style="margin:.3rem 0 0">物理图鉴</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

if not images:
    st.caption("图鉴还没有内容。教师在后台上传「本周物理一图」后，会自动归档到这里。")
    st.stop()

topics = sorted({i.get("topic", "") for i in images if i.get("topic")})
tags = sorted({t for i in images for t in i.get("tags", [])})

c1, c2 = st.columns(2)
topic = c1.selectbox("按主题", ["全部"] + topics)
sel_tags = c2.multiselect("按标签", tags)

filtered = [
    i for i in images
    if (topic == "全部" or i.get("topic") == topic)
    and (not sel_tags or set(sel_tags) <= set(i.get("tags", [])))
]


@st.dialog("物理图鉴 · 大图", width="large")
def show_large(img: dict):
    src = resolve_image_src(img)
    if src:
        try:
            st.image(src, width="stretch")
        except Exception:
            st.warning("图片加载失败。")
    tags_txt = " · ".join(img.get("tags", []))
    st.markdown(f"**{img['title']}**")
    st.caption(f"{img.get('topic', '')} ｜ {tags_txt} ｜ 首次展示 {img.get('first_shown', '—')}")
    st.write(img.get("description", ""))
    if img.get("teacher_note"):
        st.info(f"老师备注：{img['teacher_note']}", icon="💡")


ncols = 3
for row_start in range(0, len(filtered), ncols):
    cols = st.columns(ncols, gap="medium")
    for col, img in zip(cols, filtered[row_start:row_start + ncols]):
        with col:
            src = resolve_image_src(img)
            if src:
                try:
                    st.image(src, width="stretch")
                except Exception:
                    st.warning("图片加载失败")
            st.markdown(f"**{img['title']}**")
            st.caption(f"{img.get('topic', '')} · WEEK {img.get('week', '—')}")
            st.button("查看大图", key=f"view-{img['id']}",
                      on_click=show_large, args=(img,))
