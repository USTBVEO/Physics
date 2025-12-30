import streamlit as st
import openai

# --- UI 设置 ---
st.set_page_config(page_title="Trae AI Chat", page_icon="🤖")
st.title("🤖 杨威的物理课堂机器人")

# --- 侧边栏 ---
with st.sidebar:
    st.title("设置")
    
    # API Key 输入
    api_key = st.text_input("输入你的 API Key", type="password", help="从 OpenAI 或 DeepSeek 官网获取", value="sk-bb20c47e022b4d299a4077932081b872")
    
    # 模型选择
    model_options = ["gpt-4o", "deepseek-chat"]
    selected_model = st.selectbox("选择模型", model_options, index=1)
    
    st.markdown("---")
    st.markdown("不知道如何获取 API Key？")
    st.page_link("https://platform.openai.com/api-keys", label="OpenAI API Key", icon="🔑")
    st.page_link("https://platform.deepseek.com/api_keys", label="DeepSeek API Key", icon="🔑")

# --- API Client 初始化 ---
def get_openai_client(api_key, model):
    if not api_key:
        return None
    
    base_url = None
    # 为 DeepSeek 模型设置特定的 base_url
    if model == "deepseek-chat":
        base_url = "https://api.deepseek.com/v1"
    
    try:
        return openai.OpenAI(api_key=api_key, base_url=base_url)
    except Exception as e:
        st.error(f"创建 API Client 失败: {e}")
        return None

client = get_openai_client(api_key, selected_model)

# --- 聊天记录管理 ---
# 初始化聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 聊天输入和响应 ---
if prompt := st.chat_input("你好，有什么可以帮你的吗？"):
    # 检查 API Key 是否已输入
    if not client:
        st.warning("请输入你的 API Key。")
        st.stop()

    # 将用户消息添加到聊天记录并显示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 显示助手的响应
    with st.chat_message("assistant"):
        try:
            # 定义流式响应生成器
            def stream_generator():
                stream = client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                )
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content

            # 使用 st.write_stream 来优雅地处理流式输出
            response = st.write_stream(stream_generator)
            
            # 将完整的助手响应添加到聊天记录
            st.session_state.messages.append({"role": "assistant", "content": response})

        except openai.APIConnectionError as e:
            st.error(f"API 连接错误: {e.__cause__}")
        except openai.RateLimitError:
            st.error("API 请求过于频繁，请稍后再试。")
        except openai.APIStatusError as e:
            st.error(f"API 状态错误: {e.status_code} - {e.response}")
        except Exception as e:
            st.error(f"发生未知错误: {e}")