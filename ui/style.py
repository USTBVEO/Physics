"""视觉层：统一的 CSS 注入。深蓝黑 / 低饱和 / 单强调色 #5FB4C9。"""
import streamlit as st

ACCENT = "#5FB4C9"
BG = "#0B0F17"
CARD = "#101624"
TEXT = "#E8ECF2"

BASE_CSS = f"""
<style>
.stApp {{
    background: {BG};
    color: {TEXT};
    font-family: -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei",
                 "Noto Sans SC", sans-serif;
}}
#MainMenu, footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{
    background: transparent; visibility: hidden; height: 0;
}}
.block-container {{ padding: 1.2rem 2.6rem 2.2rem; max-width: 1780px; }}
h1, h2, h3, h4 {{ color: {TEXT}; font-weight: 600; letter-spacing: .02em; }}
a {{ color: {ACCENT}; }}
[data-testid="stSidebar"] {{ background: #0E1420; }}
[data-testid="stSidebar"] * {{ color: rgba(232,236,242,.75); }}
[data-testid="stPageLink-NavLink"] {{
    color: rgba(232,236,242,.38); font-size: .82rem; text-decoration: none;
}}
[data-testid="stPageLink-NavLink"]:hover {{ color: {ACCENT}; }}
.stButton>button, .stDownloadButton>button {{
    border-radius: 8px; border: 1px solid rgba(255,255,255,.14);
    background: rgba(255,255,255,.04); color: {TEXT};
}}
.stButton>button:hover, .stDownloadButton>button:hover {{
    border-color: {ACCENT}; color: {ACCENT};
}}
input, textarea, [data-baseweb="select"] > div {{
    background: rgba(255,255,255,.04) !important;
}}
::-webkit-scrollbar {{ width: 8px; height: 8px; }}
::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,.12); border-radius: 99px; }}
[data-testid="stImage"] img {{ border-radius: 10px; }}
</style>
"""

DISPLAY_CSS = f"""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {{ display: none; }}
.stApp {{ overflow: hidden; }}
.block-container {{ padding: .5rem 3rem .6rem; max-width: 1900px; }}

/* 一屏展示：约束图片与长文本 */
[data-testid="stImage"] img {{
    max-height: 8vh; width: auto !important; max-width: 100%;
    object-fit: contain; display: block; margin: 0 auto;
}}
.pw-imgdesc {{
    display: -webkit-box; -webkit-line-clamp: 2;
    -webkit-box-orient: vertical; overflow: hidden;
}}
.pw-question .txt {{
    display: -webkit-box; -webkit-line-clamp: 2;
    -webkit-box-orient: vertical; overflow: hidden;
}}

.pw-topbar {{
    display: flex; align-items: flex-end; gap: 2.4vw;
    border-bottom: 1px solid rgba(255,255,255,.09);
    padding: .15vh .2rem .5vh; margin-bottom: .7vh;
}}
.pw-brand {{ font-size: 3.1vh; font-weight: 700; letter-spacing: .05em; line-height: 1.1; }}
.pw-brand small {{
    display: block; font-size: 1.05vh; letter-spacing: .55em;
    color: {ACCENT}; font-weight: 500; margin-top: .4vh;
}}
.pw-spacer {{ flex: 1; }}
.pw-top-item {{ font-size: 2vh; white-space: nowrap; }}
.pw-top-item label {{
    display: block; font-size: 1.05vh; letter-spacing: .3em;
    color: rgba(232,236,242,.45); margin-bottom: .3vh;
}}
.pw-top-item .accent {{ color: {ACCENT}; font-weight: 700; }}

.pw-card {{
    background: {CARD}; border: 1px solid rgba(255,255,255,.07);
    border-radius: 14px; padding: 1vh 1.4vw; height: 100%;
    display: flex; flex-direction: column;
}}
.pw-class {{
    font-size: 1.5vh; letter-spacing: .25em; color: rgba(232,236,242,.55);
}}
.pw-theme {{
    font-size: 2.2vh; font-weight: 700; margin: .1vh 0 .4vh; line-height: 1.2;
    padding-bottom: .3vh; border-bottom: 1px solid rgba(255,255,255,.06);
}}
.pw-timeline {{ display: flex; flex-direction: column; gap: .15vh; }}
.pw-lesson {{
    padding-left: .8vw; border-left: 2px solid rgba(255,255,255,.08);
}}
.pw-lesson-head {{
    display: flex; align-items: baseline; gap: .6vw; margin-bottom: .15vh;
}}
.pw-lesson-day {{
    font-size: 1.35vh; font-weight: 600; color: {ACCENT}; letter-spacing: .08em;
}}
.pw-lesson-no {{
    font-size: 1.05vh; color: rgba(232,236,242,.35); letter-spacing: .05em;
}}
.pw-lesson-content {{
    font-size: 1.35vh; color: rgba(232,236,242,.85); line-height: 1.2; margin-bottom: .05vh;
}}
.pw-lesson-task {{
    font-size: 1.15vh; color: rgba(95,180,201,.65); line-height: 1.2;
}}
.pw-note {{
    font-size: 1.05vh; color: rgba(232,236,242,.35); margin-top: .3vh;
    line-height: 1.2; display: -webkit-box; -webkit-line-clamp: 2;
    -webkit-box-orient: vertical; overflow: hidden;
}}

.pw-stats {{
    display: flex; gap: 3.6vw; align-items: baseline;
    border-top: 1px solid rgba(255,255,255,.09); border-bottom: 1px solid rgba(255,255,255,.09);
    padding: .4vh .2rem; margin: .5vh 0 0;
}}
.pw-stat b {{
    font-size: 2.7vh; font-weight: 700; color: {ACCENT};
    font-variant-numeric: tabular-nums;
}}
.pw-stat span {{
    display: block; font-size: 1.15vh; color: rgba(232,236,242,.5);
    letter-spacing: .25em; margin-top: .15vh;
}}

.pw-question {{
    display: flex; align-items: center; gap: 1.6vw;
    background: linear-gradient(90deg, rgba(95,180,201,.10), transparent 75%);
    border-left: 3px solid {ACCENT}; border-radius: 0 12px 12px 0;
    padding: .5vh 1.5vw; margin-top: .5vh;
}}
.pw-question .tag {{
    font-size: 1.25vh; letter-spacing: .4em; color: {ACCENT};
    white-space: nowrap; font-weight: 600;
}}
.pw-question .txt {{ font-size: 2.15vh; line-height: 1.45; }}

.pw-imgtitle {{ font-size: 2.4vh; font-weight: 650; margin: .4vh 0; }}
.pw-imgmeta {{ font-size: 1.3vh; color: rgba(232,236,242,.45); letter-spacing: .14em; }}
.pw-imgdesc {{ font-size: 1.7vh; color: rgba(232,236,242,.78); line-height: 1.65; margin-top: 1vh; }}
.pw-weeklabel {{ font-size: 1.25vh; letter-spacing: .4em; color: {ACCENT}; font-weight: 600; }}

.pw-footer {{
    display: flex; gap: 1.6vw; margin-top: .3vh; align-items: center;
}}
</style>
"""


def inject_base():
    st.markdown(BASE_CSS, unsafe_allow_html=True)


def inject_display():
    st.markdown(DISPLAY_CSS, unsafe_allow_html=True)
