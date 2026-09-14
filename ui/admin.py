"""教师后台：密码门 + 全部内容编辑。所有保存经 store 层持久化。"""
import hashlib
import io
import time
import uuid
from datetime import date

import streamlit as st

from core import repo, school_year
from core.config import TOPICS
from core.models import ClassProgress, PhysicsImage
from core.store import secret
from ui.style import inject_base, ACCENT

inject_base()

# ---------------- 密码门 ----------------
if not st.session_state.get("is_teacher"):
    st.markdown("## 教师后台")
    st.caption("输入管理员密码进入。密码在 .streamlit/secrets.toml 或 Streamlit Cloud Secrets 中配置（admin_password）。")
    pw = st.text_input("管理员密码", type="password")
    if st.button("解锁", type="primary"):
        admin_pw = secret("admin_password")
        if admin_pw and pw and hashlib.sha256(pw.encode()).hexdigest() == hashlib.sha256(str(admin_pw).encode()).hexdigest():
            st.session_state.is_teacher = True
            st.rerun()
        else:
            st.error("密码错误或未配置 admin_password。")
    st.stop()

# ---------------- 已解锁 ----------------
st.markdown(
    f"""
    <div style="display:flex;align-items:baseline;gap:1rem;margin:.4rem 0 .6rem">
      <h2 style="margin:0">教师后台</h2>
      <span style="font-size:.8rem;color:{ACCENT}">写入方式：{repo.store_name()}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

data = repo.all_data()
settings = data["settings"]
today = school_year.today()
week = school_year.teaching_week(settings, today)
cur_sem, _ = school_year.semester_for(settings, today)
semester_id = cur_sem["id"] if cur_sem else ""

st.caption(f"今天 {school_year.today_label(today)} · 第 {week if week else '—'} 教学周 · {semester_id or '假期'}")

if st.button("退出教师模式"):
    st.session_state.is_teacher = False
    st.rerun()


def persist(key: str, payload: dict, label: str):
    ok, detail = repo.save(key, payload, label)
    if ok:
        st.success(f"已保存：{label} · {detail}")
    else:
        st.error(f"保存失败：{detail}")


def compress_image(raw: bytes, max_side: int = 1800, quality: int = 82) -> tuple[bytes, str]:
    """>350KB 的图片压成 JPEG；小图原样保留。返回 (bytes, ext)。"""
    if len(raw) <= 350_000:
        return raw, "bin"
    from PIL import Image
    img = Image.open(io.BytesIO(raw))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if max(img.size) > max_side:
        img.thumbnail((max_side, max_side))
    out = io.BytesIO()
    img.save(out, "JPEG", quality=quality, optimize=True)
    return out.getvalue(), "jpg"


def safe_name(name: str) -> str:
    """生成安全的文件名：仅保留 ASCII 字母数字和 ._-，其余替换为 _。"""
    keep = "".join(
        ch if (ord(ch) < 128 and (ch.isalnum() or ch in "._-")) else "_"
        for ch in name
    )
    return keep[-60:] or "file"


tab_cls, tab_img, tab_photo, tab_event, tab_q, tab_tl, tab_cfg = st.tabs(
    ["班级进度", "本周物理一图", "课堂照片", "事件", "今日问题", "时间线", "考试与设置"])

# ================= 班级进度 =================
with tab_cls:
    classes = data["classes"].get("classes", [])
    names = [c["name"] for c in classes]
    if not names:
        st.warning("无班级数据。")
        st.stop()
    sel_name = st.selectbox("选择班级", names)
    idx = names.index(sel_name)
    c = classes[idx]
    cp = ClassProgress.from_dict(c)

    b1, b2 = st.columns(2)
    if b1.button("课后 +1 课时", type="primary"):
        cp.lesson_count += 1
        classes[idx] = cp.to_dict()
        persist("classes", {"classes": classes}, f"{cp.name} 课时 +1（第 {cp.lesson_count} 节）")

    chapters = {}
    for g in data["curriculum"].get("grades", []):
        for ch in g.get("chapters", []):
            chapters[ch["id"]] = ch

    def chapter_of(sid: str):
        for ch in chapters.values():
            if any(s["id"] == sid for s in ch["sections"]):
                return ch
        return None

    cur_chapter = next((ch for sid in reversed(cp.done) if (ch := chapter_of(sid))), None)
    chapter_names = {ch["name"]: ch for ch in chapters.values()}
    default_ch = cur_chapter["name"] if cur_chapter else next(iter(chapter_names), None)
    sel_ch_name = st.selectbox("编辑章节（选择要勾选完成情况的那一章）", list(chapter_names),
                               index=list(chapter_names).index(default_ch) if default_ch in chapter_names else 0)
    sel_ch = chapter_names[sel_ch_name]

    with st.form("cls_form"):
        cp.week_theme = st.text_input("本周教学主题", cp.week_theme)
        cp.today = st.text_input("今天 / 下一节课", cp.today)
        cp.next_lesson = st.text_input("再下一课", cp.next_lesson)
        cp.week_experiment = st.text_input("本周实验 / 活动", cp.week_experiment)
        cp.note = st.text_input("备注", cp.note)
        cp.progress = st.slider("章节进度", 0.0, 1.0, float(cp.progress), 0.05)
        cp.lesson_count = st.number_input("累计课时", 0, 9999, cp.lesson_count)
        sec_names = [s["name"] for s in sel_ch["sections"]]
        name_to_id = {s["name"]: s["id"] for s in sel_ch["sections"]}
        current_in_ch = [name_to_id[sid] for sid in cp.done if sid in name_to_id.values()]
        done_sel = st.multiselect("本章已完成小节", sec_names,
                                  default=[next(k for k, v in name_to_id.items() if v == sid)
                                           for sid in current_in_ch])
        submitted = st.form_submit_button("保存班级进度")
        if submitted:
            kept = [sid for sid in cp.done if sid not in list(name_to_id.values())]
            cp.done = kept + [name_to_id[n] for n in done_sel]
            classes[idx] = cp.to_dict()
            persist("classes", {"classes": classes}, f"{cp.name} 进度更新")

# ================= 本周物理一图 =================
with tab_img:
    with st.form("img_form"):
        up = st.file_uploader("上传图片（>350KB 自动压缩）", type=["jpg", "jpeg", "png", "webp"])
        url = st.text_input("或填外链 URL（已上传文件则优先）")
        title = st.text_input("图片标题")
        topic = st.selectbox("物理主题", TOPICS)
        chapter = st.selectbox("对应章节（可选）", [""] + [ch["name"] for ch in chapters.values()])
        tags_in = st.text_input("标签（逗号分隔）", "科学史")
        desc = st.text_area("简短介绍（展示在大屏上）")
        note = st.text_area("老师备注（仅图鉴详情显示）")
        set_featured = st.checkbox("设为本周展示图片", value=True)
        if st.form_submit_button("保存本周物理一图") and title:
            chapter_id = next((cid for cid, ch in chapters.items() if ch["name"] == chapter), "")
            img_id = f"img-{today.year}w{week or 0:02d}-{uuid.uuid4().hex[:4]}"
            rel = ""
            if up is not None:
                raw, _ = compress_image(up.getvalue())
                rel = f"assets/physics_images/{today.year}/{int(time.time())}_{safe_name(up.name)}"
                ok, detail = repo.save_binary(rel, raw, f"上传物理图片 {title}")
                if not ok:
                    st.error(f"图片上传失败：{detail}")
                    st.stop()
            images_list = data["images"].get("images", [])
            images_list.append(PhysicsImage(
                id=img_id, title=title, file=rel, url=url if not rel else "",
                description=desc, topic=topic, chapter_id=chapter_id,
                tags=[t.strip() for t in tags_in.split(",") if t.strip()],
                semester=semester_id, week=week or 0,
                first_shown=today.isoformat(), teacher_note=note).to_dict())
            persist("images", {"images": images_list}, f"新增物理图片「{title}」")
            if set_featured:
                settings["featured_image_id"] = img_id
                persist("settings", settings, f"本周展示图片 → {title}")

# ================= 课堂照片 =================
with tab_photo:
    nodes = data["timeline"].get("timeline", [])
    node_labels = {f"{n.get('date', '')} W{n.get('week', '?')} {n.get('title', '')}": n for n in nodes}
    cur_mon = today.isoformat()
    default_lbl = next((l for l in node_labels if l.startswith(cur_mon)),
                       next(iter(node_labels), None))
    sel_lbl = st.selectbox("归入哪一周", list(node_labels),
                           index=list(node_labels).index(default_lbl) if default_lbl else 0)
    ups = st.file_uploader("上传课堂照片（可多选）", type=["jpg", "jpeg", "png", "webp"],
                           accept_multiple_files=True)
    if ups and st.button("保存课堂照片", type="primary") and sel_lbl:
        node = node_labels[sel_lbl]
        saved = 0
        for up in ups:
            raw, _ = compress_image(up.getvalue(), max_side=1400, quality=78)
            rel = f"assets/class_memories/{today.year}/{int(time.time())}_{safe_name(up.name)}"
            ok, detail = repo.save_binary(rel, raw, f"上传课堂照片 → {sel_lbl}")
            if ok:
                node.setdefault("photos", []).append(rel)
                saved += 1
            else:
                st.error(f"{up.name} 上传失败：{detail}")
        if saved:
            persist("timeline", {"timeline": nodes}, f"添加 {saved} 张课堂照片")

# ================= 事件 =================
with tab_event:
    with st.form("ev_form"):
        ev_date = st.date_input("日期", today)
        ev_type = st.selectbox("类型", ["第一次", "考试", "竞赛", "公开课", "趣事", "学生作品", "学期", "学年", "其他"])
        ev_title = st.text_input("标题")
        ev_desc = st.text_area("描述")
        ev_note = st.text_input("老师一句话")
        if st.form_submit_button("记录事件") and ev_title:
            events_list = data["events"].get("events", [])
            events_list.append({
                "id": f"ev-{uuid.uuid4().hex[:8]}", "date": ev_date.isoformat(),
                "type": ev_type, "title": ev_title, "description": ev_desc,
                "class_ids": [c["id"] for c in data["classes"].get("classes", [])],
                "photos": [], "teacher_note": ev_note})
            persist("events", {"events": events_list}, f"事件「{ev_title}」")
    st.markdown("**已记录事件**")
    for e in sorted(data["events"].get("events", []), key=lambda x: x.get("date", ""), reverse=True):
        st.markdown(f"- `{e.get('date')}` **{e['title']}**（{e.get('type')}）{e.get('description', '')}")

# ================= 今日问题 =================
with tab_q:
    questions = data["questions"].get("questions", [])
    st.markdown("设为「今日物理问题」，首页立即展示。")
    q_labels = [f"{q['text']}（{'用过 ' + q['used_on'] if q.get('used_on') else '未用'}）" for q in questions]
    sel_q = st.selectbox("选择问题", q_labels)
    if st.button("设为今日问题", type="primary"):
        q = questions[q_labels.index(sel_q)]
        settings["today_question_id"] = q["id"]
        if not q.get("used_on"):
            q["used_on"] = today.isoformat()
        persist("settings", settings, f"今日问题 → {q['text'][:20]}")
        persist("questions", {"questions": questions}, "更新问题使用记录")
    with st.form("q_form"):
        new_q = st.text_input("新增问题")
        if st.form_submit_button("添加到问题池") and new_q:
            questions.append({"id": f"q-{uuid.uuid4().hex[:6]}", "text": new_q, "used_on": ""})
            persist("questions", {"questions": questions}, "新增今日问题池")

# ================= 时间线 =================
with tab_tl:
    nodes = data["timeline"].get("timeline", [])
    labels = [f"{n.get('date', '')} W{n.get('week', '?')} {n.get('title', '')}" for n in nodes]
    cur_lbl = next((f"{n.get('date', '')} W{n.get('week', '?')} {n.get('title', '')}"
                    for n in nodes if n.get("week") == week), None)
    sel_tl = st.selectbox("选择周节点", labels,
                          index=labels.index(cur_lbl) if cur_lbl else 0)
    node = nodes[labels.index(sel_tl)]
    with st.form("tl_form"):
        node["title"] = st.text_input("本周标题", node.get("title", ""))
        node["experiment"] = st.text_input("本周实验", node.get("experiment", ""))
        node["teacher_quote"] = st.text_input("老师的一句话", node.get("teacher_quote", ""))
        if st.form_submit_button("保存周节点"):
            persist("timeline", {"timeline": nodes}, f"更新时间线 {sel_tl}")

# ================= 考试与设置 =================
with tab_cfg:
    st.markdown("**考试日期（驱动首页倒计时）**")
    exams = settings.get("exams", [])
    for i, e in enumerate(exams):
        ec1, ec2, ec3 = st.columns([3, 2, 1])
        e["name"] = ec1.text_input("名称", e.get("name", ""), key=f"ex-n{i}")
        e["date"] = ec2.text_input("日期 YYYY-MM-DD", e.get("date", ""), key=f"ex-d{i}")
        if ec3.button("删除", key=f"ex-x{i}"):
            exams.pop(i)
            persist("settings", settings, f"删除考试 {e.get('name')}")
            st.rerun()
    if st.button("保存考试日期"):
        persist("settings", settings, "更新考试日期")
    with st.form("exam_add"):
        en = st.text_input("新考试名称")
        ed = st.date_input("新考试日期", today)
        if st.form_submit_button("添加考试") and en:
            exams.append({"name": en, "date": ed.isoformat()})
            persist("settings", settings, f"新增考试 {en}")

    st.markdown("---")
    st.markdown("**学期与站点**")
    with st.form("sem_form"):
        site = settings.get("site", {})
        site["title"] = st.text_input("站点标题", site.get("title", ""))
        site["grade_start_year"] = st.number_input("高一入学年份", 2000, 2100,
                                                   int(site.get("grade_start_year", today.year)))
        settings["holiday_weeks"] = [x.strip() for x in st.text_input(
            "放假周（各周周一日期，逗号分隔）",
            ", ".join(settings.get("holiday_weeks", []))).split(",") if x.strip()]
        for i, s in enumerate(settings.get("semesters", [])):
            st.markdown(f"学期 {i + 1}")
            sc1, sc2, sc3 = st.columns(3)
            s["name"] = sc1.text_input("名称", s.get("name", ""), key=f"sm-n{i}")
            s["start"] = sc2.text_input("开始", s.get("start", ""), key=f"sm-s{i}")
            s["end"] = sc3.text_input("结束", s.get("end", ""), key=f"sm-e{i}")
        if st.form_submit_button("保存设置"):
            settings["site"] = site
            persist("settings", settings, "更新学期与站点设置")
