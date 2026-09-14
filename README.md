# 杨威的物理课堂

高中物理课堂主页与三年成长档案：课堂大屏、课程地图、物理记忆时间线、物理图鉴、AI 助教、教师后台。

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 配置密钥（不要提交到 GitHub）

复制以下内容为 `.streamlit/secrets.toml`（本地）或在 Streamlit Cloud 的 App Settings → Secrets 中填写：

```toml
admin_password = "你的教师后台密码"
deepseek_api_key = "sk-..."   # 与 openai_api_key 至少配置一个
openai_api_key = "sk-..."

[github]
token = "github_pat_..."      # Fine-grained Token，仅授予本仓库 Contents 读写权限
repo = "USTBVEO/Physics"
branch = "main"
```

- 配置 `[github]` 后，教师后台的每次保存会以 commit 形式写回仓库（云端自动重新部署，约 1 分钟生效）；
  不配置则仅写入本地文件（适合本机自托管）。
- API Key 一律走 secrets，代码中不出现任何密钥。

## 数据结构

内容全部存放在 `data/*.json`（班级进度、课程地图、时间线、物理图片、事件、问题池、设置），
媒体文件在 `assets/` 下按年份归档。程序负责展示，内容独立存储，更换前端框架后数据仍可直接复用。
