"""「杨威的物理课堂」入口：全局配置 + 页面路由。"""
import streamlit as st

from ui.style import inject_base

st.set_page_config(
    page_title="杨威的物理课堂",
    page_icon="⚛",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_base()

pages = [
    st.Page("ui/display_home.py", title="课堂大屏", icon="🖥", default=True),
    st.Page("ui/display_curriculum.py", title="课程地图", icon="🧭"),
    st.Page("ui/display_timeline.py", title="物理记忆", icon="🕰"),
    st.Page("ui/display_gallery.py", title="物理图鉴", icon="🖼"),
    st.Page("ui/assistant.py", title="物理 AI 助教", icon="🤖"),
    st.Page("ui/display_review.py", title="三年回顾", icon="⏳"),
    st.Page("ui/admin.py", title="教师后台", icon="🔐"),
]
pg = st.navigation(pages)
pg.run()
