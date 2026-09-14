"""AI 助教核心：客户端构建、流式响应、HTML 提取、课程上下文注入。"""
from __future__ import annotations

import re

import streamlit as st

PROVIDERS = {
    "DeepSeek": {"model": "deepseek-chat", "base_url": "https://api.deepseek.com/v1",
                 "secret": "deepseek_api_key"},
    "OpenAI": {"model": "gpt-4o", "base_url": None, "secret": "openai_api_key"},
}


def _secret(name: str):
    try:
        return st.secrets.get(name)
    except Exception:
        return None


def available_providers() -> list[str]:
    return [name for name, cfg in PROVIDERS.items() if _secret(cfg["secret"])]


def get_client(provider: str):
    """返回 (OpenAI client, model)；未配置时返回 (None, None)。"""
    if provider not in PROVIDERS:
        return None, None
    cfg = PROVIDERS[provider]
    key = _secret(cfg["secret"])
    if not key:
        return None, None
    import openai
    return openai.OpenAI(api_key=key, base_url=cfg["base_url"]), cfg["model"]


def stream_reply(client, model: str, messages: list[dict]):
    """流式生成器：逐段 yield 文本增量。"""
    stream = client.chat.completions.create(
        model=model, messages=messages, stream=True)
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content


def build_system_prompt(data: dict, week: int | None, grade: str) -> str:
    """把当前教学进度注入为系统提示词，让 AI 知道课讲到哪。"""
    lines = [
        "你是杨威老师的高中物理 AI 助教，服务于一所高中的物理课堂。",
        "回答要求：符合高中生认知水平；多用生活实例和比喻；公式用 LaTeX；",
        "先给直觉理解，再给严谨推导；鼓励学生自己思考，不直接替学生完成作业。",
    ]
    if week:
        lines.append(f"现在是{grade}第 {week} 教学周。")
    classes = data.get("classes", {}).get("classes", [])
    if classes:
        lines.append("三个班当前教学进度：")
        for c in classes:
            lines.append(
                f"- {c.get('name')}：本周主题「{c.get('week_theme', '')}」，"
                f"今天课程「{c.get('today', '')}」，本周实验「{c.get('week_experiment', '')}」")
    return "\n".join(lines)


def extract_html_from_text(text: str) -> list[str]:
    """从 AI 回复中提取 HTML（```html``` 代码块 / <html> / <body> 片段）。"""
    blocks: list[str] = []
    if not text:
        return blocks
    for m in re.finditer(r"```(?:html|HTML)\s*([\s\S]*?)```", text, flags=re.MULTILINE):
        blocks.append(m.group(1).strip())
    if not blocks:
        for m in re.finditer(r"(<\s*html[\s\S]*?</\s*html\s*>)", text, flags=re.IGNORECASE):
            blocks.append(m.group(1).strip())
    if not blocks:
        for m in re.finditer(r"(<\s*body[\s\S]*?</\s*body\s*>)", text, flags=re.IGNORECASE):
            body = m.group(1).strip()
            blocks.append(f"<!DOCTYPE html>\n<html>\n{body}\n</html>")
    return blocks
