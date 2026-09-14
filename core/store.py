"""存储适配层。

读取：始终读部署环境内的 data/、assets/ 文件（云端=仓库 checkout，本地=磁盘）。
写入：LocalStore 直接写本地文件；GitHubStore 通过 GitHub Contents API 提交 commit
     （同时写本地文件，让当前实例立即生效；云端随后自动重新部署同步）。
"""
from __future__ import annotations

import base64
import json

import streamlit as st

from core.config import DATA_DIR, ROOT


def secret(name: str, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


class LocalStore:
    name = "本地文件"

    def read_bytes(self, rel_path: str) -> bytes | None:
        p = ROOT / rel_path
        return p.read_bytes() if p.exists() else None

    def _write_local(self, rel_path: str, content: bytes):
        p = ROOT / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)

    def save_json(self, rel_path: str, data: dict, commit_msg: str) -> tuple[bool, str]:
        self._write_local(rel_path, json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
        return True, "已写入本地文件"

    def save_binary(self, rel_path: str, content: bytes, commit_msg: str) -> tuple[bool, str]:
        self._write_local(rel_path, content)
        return True, "已写入本地文件"


class GitHubStore(LocalStore):
    name = "GitHub 仓库"

    def __init__(self, token: str, repo: str, branch: str = "main"):
        self.token, self.repo, self.branch = token, repo, branch

    def _api_url(self, rel_path: str) -> str:
        return f"https://api.github.com/repos/{self.repo}/contents/{rel_path}"

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json"}

    def _put(self, rel_path: str, content: bytes, commit_msg: str) -> tuple[bool, str]:
        import requests
        try:
            r = requests.get(self._api_url(rel_path), headers=self._headers(),
                             params={"ref": self.branch}, timeout=15)
            sha = r.json().get("sha") if r.status_code == 200 else None
            payload = {"message": commit_msg, "branch": self.branch,
                       "content": base64.b64encode(content).decode()}
            if sha:
                payload["sha"] = sha
            r = requests.put(self._api_url(rel_path), headers=self._headers(),
                             json=payload, timeout=30)
            if r.status_code in (200, 201):
                return True, "已提交到 GitHub（云端约 1 分钟后自动同步）"
            return False, f"GitHub API {r.status_code}: {r.json().get('message', r.text[:200])}"
        except Exception as e:
            return False, f"GitHub 提交失败：{e}"

    def save_json(self, rel_path: str, data: dict, commit_msg: str) -> tuple[bool, str]:
        content = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        ok, msg = self._put(rel_path, content, commit_msg)
        if ok:
            self._write_local(rel_path, content)  # 当前实例乐观更新
        return ok, msg

    def save_binary(self, rel_path: str, content: bytes, commit_msg: str) -> tuple[bool, str]:
        ok, msg = self._put(rel_path, content, commit_msg)
        if ok:
            self._write_local(rel_path, content)
        return ok, msg


def get_store() -> LocalStore | GitHubStore:
    gh = secret("github") or {}
    token, repo = gh.get("token"), gh.get("repo")
    if token and repo:
        return GitHubStore(token, repo, gh.get("branch", "main"))
    return LocalStore()
