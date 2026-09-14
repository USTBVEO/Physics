"""物理 AI 助教：原聊天功能完整迁移 + 当前教学进度上下文。"""
import json
from pathlib import Path

import streamlit as st

from core import ai, repo, school_year
from ui.style import inject_base

inject_base()

providers = ai.available_providers()
with st.sidebar:
    st.title("物理 AI 助教")
    if not providers:
        st.error("尚未配置 API Key。请在 .streamlit/secrets.toml 或 Streamlit Cloud Secrets 中配置 deepseek_api_key / openai_api_key。")
        provider = None
    else:
        provider = st.selectbox("模型", providers)
    st.markdown("---")

    export_json = json.dumps(st.session_state.get("messages", []), ensure_ascii=False, indent=2)
    st.download_button("导出聊天记录 JSON", data=export_json, file_name="chat_history.json",
                       mime="application/json", help="下载当前会话的聊天记录为 JSON 文件")
    uploaded = st.file_uploader("导入聊天记录 JSON", type=["json"])
    if uploaded and st.button("加载记录"):
        try:
            content = uploaded.read().decode("utf-8")
            d = json.loads(content)
            if isinstance(d, list) and all(isinstance(x, dict) and "role" in x and "content" in x for x in d):
                st.session_state.messages = d
                st.success("导入成功，聊天记录已加载。")
                st.rerun()
            else:
                st.warning("JSON 格式不正确：应为包含 role 与 content 字段的对象列表。")
        except Exception as e:
            st.error(f"导入失败：{e}")

st.markdown(
    """
    <div style="margin:.4rem 0 1rem">
      <div style="font-size:.8rem;letter-spacing:.3em;color:rgba(232,236,242,.45)">PHYSICS AI ASSISTANT</div>
      <h2 style="margin:.3rem 0 0">物理 AI 助教</h2>
      <p style="color:rgba(232,236,242,.6)">AI 知道本节课的进度，会结合当前课程回答你的问题。</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_html" not in st.session_state:
    st.session_state.last_html = None

client = model = None
if provider:
    client, model = ai.get_client(provider)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("你好，有什么物理问题想问的吗？"):
    if client is None:
        st.warning("教师尚未配置 API Key，暂时无法使用。")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    data = repo.all_data()
    settings = data["settings"]
    system_prompt = ai.build_system_prompt(
        data, school_year.teaching_week(settings, school_year.today()),
        school_year.grade_name(settings, school_year.today()))

    with st.chat_message("assistant"):
        try:
            def stream_generator():
                yield from ai.stream_reply(client, model,
                                           [{"role": "system", "content": system_prompt}]
                                           + st.session_state.messages)

            response = st.write_stream(stream_generator)
            st.session_state.messages.append({"role": "assistant", "content": response})

            html_blocks = ai.extract_html_from_text(response)
            st.session_state.last_html = html_blocks[0] if html_blocks else None
            st.rerun()
        except Exception as e:
            import openai
            if isinstance(e, openai.APIConnectionError):
                st.error(f"API 连接错误: {e.__cause__}")
            elif isinstance(e, openai.RateLimitError):
                st.error("API 请求过于频繁，请稍后再试。")
            elif isinstance(e, openai.APIStatusError):
                st.error(f"API 状态错误: {e.status_code} - {e.response}")
            else:
                st.error(f"发生未知错误: {e}")

if st.session_state.get("last_html"):
    st.markdown("---")
    st.subheader("HTML 预览")
    st.components.v1.html(st.session_state.last_html, height=600, scrolling=True)

    st.download_button("下载为 index.html", data=st.session_state.last_html,
                       file_name="index.html", mime="text/html")

    server_address = None
    try:
        server_address = st.get_option("server.address")
    except Exception:
        pass
    is_local = server_address in ("localhost", "127.0.0.1")
    if is_local and st.button("在浏览器中打开 index.html"):
        file_path = Path.cwd() / "index.html"
        file_path.write_text(st.session_state.last_html, encoding="utf-8")
        import webbrowser
        webbrowser.open(file_path.resolve().as_uri())
