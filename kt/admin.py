"""後台：老師登入後自行新增、修改、刪除網站內容。"""
import csv
import io
import re
import secrets
import time
import uuid
from datetime import date, datetime, timedelta
from functools import wraps
from pathlib import Path

from flask import (Blueprint, abort, current_app, flash, g, jsonify, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from . import content as C
from . import today_str
from .db import execute, get_db, get_settings, log_action, now_str, query, set_setting
from .icons import ICON_CHOICES
from .sanitize import clean_html

bp = Blueprint("admin", __name__)

IMAGE_EXT = {"jpg", "jpeg", "png", "gif", "webp"}
FILE_EXT = IMAGE_EXT | {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv", "zip"}
PER_PAGE = 30

# ------------------------------------------------------------------
# 內容類型設定：每種內容的欄位、列表欄目及權限
# ------------------------------------------------------------------
PUB = ("published", "公開顯示", "checkbox", {"default": 1, "help": "取消勾選即暫時隱藏，不會刪除。"})


def F(name, label, type_="text", **opt):
    return (name, label, type_, opt)


RESOURCES = {
    "posts": {
        "label": "消息及故事", "singular": "消息／故事", "icon": "news", "role": "editor",
        "fields": [
            F("type", "類別", "select", choices=C.POST_TYPES, required=True, filter=True),
            F("title", "標題", required=True, help="簡短清晰，建議 30 字以內。"),
            F("date", "日期", "date", required=True),
            F("tag", "標籤", "select", choices=C.POST_TAGS, filter=True),
            F("summary", "摘要", "textarea", help="顯示於首頁及列表卡片，建議 50 字以內。"),
            F("image", "封面相片", "image", help="建議橫向相片（16:10）。未上載則顯示色塊。"),
            F("body", "內文", "richtext"),
            F("featured", "首頁精選", "checkbox", help="勾選後於首頁「成果與故事」展示（適用於校園故事、活動及喜訊）。"),
            F(*PUB[:3], **PUB[3]),
        ],
        "list": ["date", "type", "title", "tag", "featured", "published"],
        "search": ["title", "summary"], "order": "date DESC, id DESC",
        "preview": lambda r: url_for("public.news_detail", post_id=r["id"]),
    },
    "awards": {
        "label": "學生成就", "singular": "獎項", "icon": "trophy", "role": "editor",
        "fields": [
            F("school_year", "學年", "schoolyear", required=True, filter=True),
            F("date", "得獎日期", "date", required=True, help="必須在所選學年內（九月一日至翌年八月卅一日）。"),
            F("category", "範疇", "select", choices=C.AWARD_CATEGORIES, required=True, filter=True),
            F("competition", "比賽名稱", required=True),
            F("result", "獎項", required=True, help="例：冠軍、金獎、優異獎"),
            F("students", "得獎學生", "textarea", help="建議只寫班別及姓氏，例：5A 陳同學。"),
            F("story", "成果故事", "textarea", help="一兩句描述學生的努力過程。精選成果建議填寫。"),
            F("featured", "精選成果", "checkbox", help="於首頁展示（建議不多於 3 項）。"),
            F(*PUB[:3], **PUB[3]),
        ],
        "list": ["school_year", "date", "category", "competition", "result", "featured", "published"],
        "search": ["competition", "students", "result"], "order": "date DESC, id DESC",
        "preview": lambda r: "/stories#awards",
    },
    "events": {
        "label": "校曆", "singular": "校曆事項", "icon": "calendar", "role": "editor",
        "fields": [
            F("date", "日期", "date", required=True),
            F("end_date", "結束日期", "date", help="單日活動請留空。"),
            F("title", "事項", required=True),
            F("note", "備註"),
            F("kind", "類別", "select", choices=C.EVENT_KINDS, required=True, filter=True),
            F(*PUB[:3], **PUB[3]),
        ],
        "list": ["date", "end_date", "title", "kind", "published"],
        "search": ["title", "note"], "order": "date DESC",
        "preview": lambda r: "/calendar",
    },
    "documents": {
        "label": "通告及文件", "singular": "文件", "icon": "file", "role": "editor",
        "fields": [
            F("category", "類別", "select", choices=C.DOC_CATEGORIES, required=True, filter=True),
            F("title", "文件名稱", required=True),
            F("date", "發出日期", "date", required=True),
            F("file", "上載檔案", "file", help="PDF、Word、Excel、PowerPoint 或圖片，上限 25MB。"),
            F("url", "或外部連結", "url", help="如文件存放於其他網站（例如教育局），可填寫連結。"),
            F(*PUB[:3], **PUB[3]),
        ],
        "list": ["date", "category", "title", "file", "published"],
        "search": ["title"], "order": "date DESC, id DESC",
        "preview": lambda r: {"plan": "/info#reports", "p1": "/parents#p1"}.get(r["category"], "/info#notices"),
    },
    "faqs": {
        "label": "常見問題", "singular": "問題", "icon": "chat", "role": "editor",
        "fields": [
            F("grp", "分類", "select", choices=C.FAQ_GROUPS, required=True, filter=True),
            F("question", "問題", required=True),
            F("answer", "答案", "richtext", required=True),
            F("sort", "排序", "number", help="數字越小越前。"),
            F(*PUB[:3], **PUB[3]),
        ],
        "list": ["grp", "question", "sort", "published"],
        "search": ["question"], "order": "sort, id",
        "preview": lambda r: "/parents#faq",
    },
    "voices": {
        "label": "家長及學生心聲", "singular": "心聲", "icon": "users", "role": "editor",
        "fields": [
            F("role", "身份", "select", choices=C.VOICE_ROLES, required=True, filter=True),
            F("name", "稱呼", required=True, help="例：陳太（二年級家長）。請先取得當事人同意。"),
            F("quote", "內容", "textarea", required=True),
            F("sort", "排序", "number"),
            F(*PUB[:3], **PUB[3]),
        ],
        "list": ["role", "name", "quote", "sort", "published"],
        "search": ["name", "quote"], "order": "sort, id",
        "preview": lambda r: "/",
    },
    "highlights": {
        "label": "首頁：學校特色", "singular": "特色", "icon": "star", "role": "editor",
        "fields": [
            F("title", "標題", required=True),
            F("text", "簡介", "textarea", required=True),
            F("icon", "圖示", "icon"),
            F("color", "顏色", "select", choices=C.HIGHLIGHT_COLORS),
            F("link", "連結", "url", help="例：/development#ai"),
            F("sort", "排序", "number"),
            F(*PUB[:3], **PUB[3]),
        ],
        "list": ["title", "color", "link", "sort", "published"],
        "search": ["title", "text"], "order": "sort, id",
        "preview": lambda r: "/#why",
    },
    "sections": {
        "label": "內頁內容", "singular": "內頁區塊", "icon": "layers", "role": "editor",
        "fields": [
            F("page_id", "所屬頁面", "page", required=True, filter=True),
            F("title", "區塊標題", required=True, help="同時顯示於主選單的下拉清單。"),
            F("anchor", "網址代號", required=True, help="只可用英文小寫、數字及「-」，例：p1-admission。用於連結 /頁面#代號。"),
            F("icon", "圖示", "icon"),
            F("body", "內容", "richtext"),
            F("widget", "附加動態內容", "select", choices=C.WIDGETS,
              help="在文字下方自動列出相關內容，例如學生成就、常見問題、文件。"),
            F("sort", "排序", "number", help="數字越小越前。"),
            F("visible", "顯示", "checkbox", default=1),
        ],
        "list": ["page_id", "sort", "title", "anchor", "widget", "visible"],
        "search": ["title", "body"], "order": "page_id, sort, id",
        "preview": lambda r: f"/{_page_slug(r['page_id'])}#{r['anchor']}",
    },
    "pages": {
        "label": "主選單頁面", "singular": "頁面", "icon": "home", "role": "admin", "no_create": True, "no_delete": True,
        "fields": [
            F("title", "頁面名稱", required=True),
            F("title_en", "英文名稱"),
            F("intro", "頁面簡介", "textarea"),
            F("style", "頁首顏色", "select", choices=C.PAGE_STYLES),
            F("sort", "選單排序", "number"),
            F("in_nav", "顯示於主選單", "checkbox", default=1),
        ],
        "list": ["sort", "title", "slug", "in_nav"],
        "search": ["title"], "order": "sort, id",
        "preview": lambda r: f"/{r['slug']}",
    },
    "users": {
        "label": "帳戶管理", "singular": "帳戶", "icon": "lock", "role": "admin",
        "fields": [
            F("username", "登入名稱", required=True, help="英文或數字。"),
            F("display_name", "顯示名稱", required=True, help="例：陳老師"),
            F("role", "權限", "select", choices={"editor": "編輯（更新內容）", "admin": "管理員（另可管理帳戶及網站設定）"}, required=True),
            F("password", "密碼", "password", help="最少 8 個字元。修改帳戶時留空即不更改。"),
            F("active", "啟用", "checkbox", default=1),
        ],
        "list": ["username", "display_name", "role", "last_login", "active"],
        "search": ["username", "display_name"], "order": "id",
    },
}

NAV_GROUPS = [
    ("日常更新", ["posts", "awards", "events", "documents"]),
    ("頁面內容", ["sections", "faqs", "voices", "highlights"]),
    ("網站管理", ["pages", "users"]),
]

SETTINGS_GROUPS = [
    ("學校資料", [
        ("school_name", "學校名稱", "text"), ("school_name_en", "英文名稱", "text"), ("school_short", "簡稱", "text"),
        ("sponsor", "辦學團體", "text"), ("address", "地址", "text"), ("address_en", "英文地址", "text"),
        ("phone", "電話", "text"), ("fax", "傳真", "text"), ("email", "電郵", "text"),
        ("office_hours", "校務處辦公時間", "text"), ("map_query", "地圖搜尋字詞", "text"), ("philosophy", "教育理念", "text"),
    ]),
    ("首頁橫幅", [
        ("hero_tag", "小標籤", "text"), ("hero_title", "主標題（第一行）", "text"), ("hero_title_hl", "主標題（第二行，橙色）", "text"),
        ("hero_lead", "簡介", "textarea"), ("hero_video_url", "校園短片（YouTube 嵌入網址）", "text"),
        ("hero_video_caption", "短片說明", "text"), ("hero_badge_num", "徽章數字", "text"), ("hero_badge_text", "徽章文字", "text"),
    ]),
    ("校長的話", [
        ("principal_name", "校長姓名", "text"), ("principal_title", "職銜", "text"),
        ("principal_quote", "引言", "textarea"), ("principal_body", "首頁簡介", "textarea"),
        ("principal_video_url", "校長短片（YouTube 嵌入網址）", "text"),
    ]),
    ("三年發展計劃", [
        ("plan_years", "計劃年期", "text"), ("plan_stage", "目前階段（1、2 或 3）", "text"),
        ("plan_ai_title", "關注事項一", "text"), ("plan_ai_points", "關注事項一重點（每行一項）", "textarea"),
        ("plan_char_title", "關注事項二", "text"), ("plan_char_points", "關注事項二重點（每行一項）", "textarea"),
        ("roadmap_1_title", "第一年標題", "text"), ("roadmap_1_text", "第一年內容", "textarea"),
        ("roadmap_2_title", "第二年標題", "text"), ("roadmap_2_text", "第二年內容", "textarea"),
        ("roadmap_3_title", "第三年標題", "text"), ("roadmap_3_text", "第三年內容", "textarea"),
    ]),
    ("數字一覽", [(f"stat_{i}_{k}", f"數字 {i}：{'數值' if k == 'n' else '說明'}", "text") for i in range(1, 5) for k in "nl"]),
    ("網站設定", [
        ("show_proto_note", "顯示頂部提示列（1 = 顯示，0 = 隱藏）", "text"), ("proto_note", "提示列文字", "text"),
        ("footer_note", "頁尾附註", "text"),
    ]),
]


def _page_slug(page_id):
    r = query("SELECT slug FROM pages WHERE id=?", (page_id,), one=True)
    return r["slug"] if r else ""


# ------------------------------------------------------------------
# 登入、權限及 CSRF
# ------------------------------------------------------------------
_failed = {}  # ip -> [count, first_ts]


def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


@bp.app_context_processor
def inject_admin():
    return {"csrf_token": csrf_token, "RES": RESOURCES, "NAV_GROUPS": NAV_GROUPS, "user": g.get("user")}


@bp.before_request
def load_user():
    g.user = None
    uid = session.get("uid")
    if uid:
        u = query("SELECT * FROM users WHERE id=? AND active=1", (uid,), one=True)
        if u:
            g.user = u
        else:
            session.clear()
    if request.method == "POST":
        token = request.form.get("_csrf") or request.headers.get("X-CSRF-Token")
        if not token or not secrets.compare_digest(token, session.get("csrf", "")):
            abort(400, "表單已逾時，請重新整理頁面後再試。")
    if request.endpoint not in ("admin.login",) and g.user is None:
        return redirect(url_for("admin.login", next=request.full_path if request.method == "GET" else None))


def require_role(role):
    if role == "admin" and g.user["role"] != "admin":
        abort(403)


def admin_only(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        require_role("admin")
        return fn(*a, **kw)
    return wrapper


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("admin.dashboard"))
    error = None
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
    rec = _failed.get(ip)
    if rec and rec[0] >= 5 and time.time() - rec[1] < 300:
        error = "登入失敗次數過多，請五分鐘後再試。"
    elif request.method == "POST":
        u = query("SELECT * FROM users WHERE username=? AND active=1",
                  (request.form.get("username", "").strip(),), one=True)
        if u and check_password_hash(u["password_hash"], request.form.get("password", "")):
            _failed.pop(ip, None)
            session.clear()
            session.permanent = True
            session["uid"] = u["id"]
            csrf_token()
            execute("UPDATE users SET last_login=? WHERE id=?", (now_str(), u["id"]))
            nxt = request.args.get("next") or ""
            if not nxt.startswith("/admin") or nxt.startswith("//"):
                nxt = url_for("admin.dashboard")
            return redirect(nxt)
        if not rec or time.time() - rec[1] >= 300:
            _failed[ip] = [1, time.time()]
        else:
            rec[0] += 1
        error = "登入名稱或密碼不正確。"
    return render_template("admin/login.html", error=error)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("已登出。", "ok")
    return redirect(url_for("admin.login"))


@bp.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        cur, new, new2 = (request.form.get(k, "") for k in ("current", "new", "new2"))
        if not check_password_hash(g.user["password_hash"], cur):
            flash("現有密碼不正確。", "error")
        elif len(new) < 8:
            flash("新密碼最少 8 個字元。", "error")
        elif new != new2:
            flash("兩次輸入的新密碼不一致。", "error")
        else:
            execute("UPDATE users SET password_hash=? WHERE id=?", (generate_password_hash(new), g.user["id"]))
            log_action(g.user["username"], "更改密碼", "帳戶")
            flash("密碼已更改。", "ok")
            return redirect(url_for("admin.dashboard"))
    return render_template("admin/account.html")


# ------------------------------------------------------------------
# 主控台及資料檢查
# ------------------------------------------------------------------
@bp.route("/")
def dashboard():
    counts = {k: query(f"SELECT COUNT(*) n FROM {k}", one=True)["n"] for k in RESOURCES}
    recent = query("SELECT * FROM audit_log ORDER BY id DESC LIMIT 12")
    issues = data_issues()
    return render_template("admin/dashboard.html", counts=counts, recent=recent,
                           issue_count=sum(len(v["items"]) for v in issues if v["level"] != "info"))


def data_issues():
    """對應改版建議第一階段：核對日期、比賽年份、重複資料、待填寫內容及失效連結。"""
    today = today_str()
    soon = (date.fromisoformat(today) + timedelta(days=30)).isoformat()
    issues = []

    def add(title, level, items, help_=""):
        issues.append({"title": title, "level": level, "items": items, "help": help_})

    bad = []
    for a in query("SELECT * FROM awards"):
        start, end = C.school_year_range(a["school_year"])
        if not (start <= a["date"] <= end):
            bad.append(("awards", a["id"], f"{a['competition']}（學年 {a['school_year']}，日期 {a['date']}）"))
    add("獎項日期與學年不符", "error", bad, "例如比賽年份誤輸入為 2036。請核對學年及日期。")

    fut = [("awards", a["id"], f"{a['competition']}（{a['date']}）")
           for a in query("SELECT * FROM awards WHERE date > ?", (soon,))]
    fut += [("posts", p["id"], f"{p['title']}（{p['date']}）")
            for p in query("SELECT * FROM posts WHERE date > ?", (soon,))]
    add("日期在未來（超過 30 日）", "error", fut, "消息及獎項通常不應是未來日期，請核對是否輸入錯誤。")

    ev = [("events", e["id"], f"{e['title']}（{e['date']} 至 {e['end_date']}）")
          for e in query("SELECT * FROM events WHERE end_date != '' AND end_date < date")]
    add("校曆結束日期早於開始日期", "error", ev)

    dup = [("posts", r["id"], f"{r['title']}（{r['n']} 項重複）") for r in query(
        "SELECT MIN(id) id, title, COUNT(*) n FROM posts GROUP BY type, title HAVING n > 1")]
    dup += [("awards", r["id"], f"{r['competition']} {r['result']}（{r['n']} 項重複）") for r in query(
        "SELECT MIN(id) id, competition, result, COUNT(*) n FROM awards "
        "GROUP BY school_year, competition, result, students HAVING n > 1")]
    add("可能重複的資料", "warn", dup)

    docs = [("documents", d["id"], d["title"]) for d in query(
        "SELECT * FROM documents WHERE published=1 AND file='' AND url=''")]
    add("已公開但未上載檔案的文件", "warn", docs, "前台會顯示「即將上載」。")

    todo = []
    for k, v in get_settings().items():
        if "請於後台填寫" in v or "請核實" in v:
            todo.append(("settings", 0, f"網站設定：{_setting_label(k)}"))
    for s in query("SELECT s.id, s.title, p.title pt FROM sections s JOIN pages p ON p.id=s.page_id "
                   "WHERE s.body LIKE '%請於後台%' OR s.body LIKE '%（年份）%' OR s.body LIKE '%請按%更新%' "
                   "OR s.body LIKE '%請上載%'"):
        todo.append(("sections", s["id"], f"{s['pt']} › {s['title']}"))
    for f in query("SELECT id, question FROM faqs WHERE answer LIKE '%請於後台%'"):
        todo.append(("faqs", f["id"], f["question"]))
    add("待填寫或待核實的內容", "warn", todo)

    demo = [(t, r["id"], r["label"]) for t, sql in (
        ("posts", "SELECT id, title label FROM posts WHERE body LIKE '%示範%' OR summary LIKE '%請核實%'"),
        ("voices", "SELECT id, name label FROM voices WHERE quote LIKE '%示範%'"),
    ) for r in query(sql)]
    add("示範內容（正式發佈前請替換或刪除）", "warn", demo)

    anchors = {(p["slug"], s["anchor"]) for p in query("SELECT * FROM pages")
               for s in query("SELECT anchor FROM sections WHERE page_id=? AND visible=1", (p["id"],))}
    slugs = {p["slug"] for p in query("SELECT slug FROM pages")} | {"", "calendar", "news"}
    broken = []
    link_re = re.compile(r'href="/([a-z0-9-]*)(?:#([a-z0-9-]+))?"')
    sources = [("sections", r["id"], r["title"], r["body"]) for r in query("SELECT id, title, body FROM sections")]
    sources += [("highlights", r["id"], r["title"], f'href="{r["link"]}"') for r in query("SELECT id, title, link FROM highlights")]
    sources += [("posts", r["id"], r["title"], r["body"]) for r in query("SELECT id, title, body FROM posts")]
    for t, rid, title, html in sources:
        for slug, anchor in link_re.findall(html or ""):
            if slug not in slugs or (anchor and slug not in ("", "calendar", "news") and (slug, anchor) not in anchors):
                broken.append((t, rid, f"{title} → /{slug}{'#' + anchor if anchor else ''}"))
    add("網站內部失效連結", "error", broken)

    noimg = [("posts", p["id"], p["title"]) for p in query(
        "SELECT * FROM posts WHERE published=1 AND image='' AND type IN ('news','joy','activity','story','work') "
        "ORDER BY date DESC LIMIT 20")]
    add("未有封面相片的消息（建議補上）", "info", noimg)
    return issues


def _setting_label(key):
    for _, items in SETTINGS_GROUPS:
        for k, label, _t in items:
            if k == key:
                return label
    return key


@bp.route("/check")
def check():
    return render_template("admin/check.html", issues=data_issues())


@bp.route("/log")
@admin_only
def log():
    return render_template("admin/log.html", rows=query("SELECT * FROM audit_log ORDER BY id DESC LIMIT 300"))


# ------------------------------------------------------------------
# 網站設定
# ------------------------------------------------------------------
@bp.route("/settings", methods=["GET", "POST"])
@admin_only
def settings():
    if request.method == "POST":
        for _, items in SETTINGS_GROUPS:
            for key, _label, _t in items:
                if key in request.form:
                    set_setting(key, request.form[key].strip())
        log_action(g.user["username"], "修改", "網站設定")
        flash("網站設定已儲存。", "ok")
        return redirect(url_for("admin.settings", tab=request.form.get("tab", "")))
    return render_template("admin/settings.html", groups=SETTINGS_GROUPS, values=get_settings(),
                           tab=request.args.get("tab", ""))


# ------------------------------------------------------------------
# 上載
# ------------------------------------------------------------------
def save_upload(fs, allowed):
    if not fs or not fs.filename:
        return None
    ext = fs.filename.rsplit(".", 1)[-1].lower() if "." in fs.filename else ""
    if ext not in allowed:
        raise ValueError(f"不支援的檔案類型（.{ext}）。可上載：{'、'.join(sorted(allowed))}")
    sub = datetime.now().strftime("%Y/%m")
    folder = Path(current_app.config["UPLOAD_FOLDER"]) / sub
    folder.mkdir(parents=True, exist_ok=True)
    name = f"{uuid.uuid4().hex[:12]}.{ext}"
    fs.save(folder / name)
    return f"{sub}/{name}"


@bp.route("/upload", methods=["POST"])
def upload():
    """富文本編輯器插入相片。"""
    try:
        path = save_upload(request.files.get("file"), IMAGE_EXT)
    except ValueError as e:
        return jsonify(error=str(e)), 400
    if not path:
        return jsonify(error="未選擇檔案"), 400
    log_action(g.user["username"], "上載相片", path)
    return jsonify(url=url_for("public.uploads", name=path))


# ------------------------------------------------------------------
# 通用內容管理
# ------------------------------------------------------------------
def get_res(name):
    res = RESOURCES.get(name)
    if not res:
        abort(404)
    require_role(res["role"])
    return res


def field_choices(field):
    name, _label, type_, opt = field
    if type_ == "select":
        return opt["choices"]
    if type_ == "page":
        return {str(p["id"]): p["title"] for p in query("SELECT id, title FROM pages ORDER BY sort")}
    if type_ == "schoolyear":
        return {y: f"{y} 學年" for y in C.school_year_choices(today_str())}
    if type_ == "icon":
        return {"": "（不設圖示）", **{i: i for i in ICON_CHOICES}}
    return None


def display(field, value):
    name, _label, type_, _opt = field
    choices = field_choices(field)
    if choices is not None:
        return choices.get(str(value), value)
    if type_ == "checkbox":
        return "✓" if value else "—"
    return value


def valid_date(s):
    try:
        d = date.fromisoformat(s)
    except (TypeError, ValueError):
        return None
    return d


def parse_form(res_name, res, row):
    """讀取並驗證表單。回傳 (data, errors)。"""
    data, errors = {}, {}
    today = date.fromisoformat(today_str())
    for field in res["fields"]:
        name, label, type_, opt = field
        if type_ == "checkbox":
            data[name] = 1 if request.form.get(name) else 0
            continue
        if type_ in ("image", "file"):
            current = row[name] if row else ""
            if request.form.get(f"{name}__remove"):
                current = ""
            try:
                saved = save_upload(request.files.get(name), IMAGE_EXT if type_ == "image" else FILE_EXT)
            except ValueError as e:
                errors[name] = str(e)
                saved = None
            data[name] = saved or current
            continue
        if type_ == "password":
            pw = request.form.get(name, "")
            if pw:
                if len(pw) < 8:
                    errors[name] = "密碼最少 8 個字元。"
                data["password_hash"] = generate_password_hash(pw)
            elif not row:
                errors[name] = "請設定密碼。"
            continue
        val = request.form.get(name, "")
        val = clean_html(val) if type_ == "richtext" else val.strip()
        if opt.get("required") and not re.sub(r"<[^>]+>|&nbsp;|\s", "", val):
            errors[name] = f"請填寫「{label}」。"
        if type_ == "number":
            try:
                val = int(val or 0)
            except ValueError:
                errors[name] = "請輸入數字。"
                val = 0
        if type_ == "date" and val:
            d = valid_date(val)
            if not d:
                errors[name] = "日期格式不正確。"
            elif not (2000 <= d.year <= today.year + 2):
                errors[name] = f"年份 {d.year} 看來不正確，請核對。"
        if type_ in ("select", "page", "schoolyear", "icon") and val:
            if val not in field_choices(field):
                errors[name] = "選項無效。"
        if type_ == "url" and val and not re.match(r"^(https?://|/|#|mailto:|tel:)", val):
            errors[name] = "連結須以 https:// 或 / 開頭。"
        data[name] = val

    # 個別內容類型的額外檢查
    if res_name == "awards" and "date" not in errors and data.get("school_year"):
        start, end = C.school_year_range(data["school_year"])
        if not (start <= data["date"] <= end):
            errors["date"] = f"得獎日期不在 {data['school_year']} 學年內（{start} 至 {end}）。"
    if res_name == "events" and data.get("end_date") and data["end_date"] < data.get("date", ""):
        errors["end_date"] = "結束日期不可早於開始日期。"
    if res_name == "sections":
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", data.get("anchor", "")):
            errors["anchor"] = "只可用英文小寫、數字及「-」。"
        else:
            dup = query("SELECT id FROM sections WHERE page_id=? AND anchor=? AND id!=?",
                        (data.get("page_id"), data["anchor"], row["id"] if row else 0), one=True)
            if dup:
                errors["anchor"] = "同一頁面已有相同代號。"
    if res_name == "users":
        if not re.fullmatch(r"[A-Za-z0-9_.-]{3,32}", data.get("username", "")):
            errors["username"] = "登入名稱須為 3–32 個英文字母、數字或 _ . -"
        elif query("SELECT id FROM users WHERE username=? AND id!=?",
                   (data["username"], row["id"] if row else 0), one=True):
            errors["username"] = "此登入名稱已被使用。"
        if row and row["id"] == g.user["id"] and (data.get("role") != "admin" or not data.get("active")):
            errors["role"] = "不可移除自己的管理員權限或停用自己的帳戶。"
    if res_name == "documents" and not errors and data.get("published") and not data.get("file") and not data.get("url"):
        flash("提示：此文件尚未上載檔案或填寫連結，前台將顯示「即將上載」。", "warn")
    return data, errors


def row_label(res_name, row):
    for k in ("title", "competition", "question", "name", "display_name", "username"):
        if k in row.keys() and row[k]:
            return str(row[k])[:40]
    return f"#{row['id']}"


@bp.route("/r/<res_name>")
def res_list(res_name):
    res = get_res(res_name)
    fields = {f[0]: f for f in res["fields"]}
    where, args = [], []
    q = request.args.get("q", "").strip()
    if q:
        where.append("(" + " OR ".join(f"{c} LIKE ?" for c in res["search"]) + ")")
        args += [f"%{q}%"] * len(res["search"])
    active_filters = {}
    for f in res["fields"]:
        if f[3].get("filter") and request.args.get(f[0]):
            where.append(f"{f[0]} = ?")
            args.append(request.args[f[0]])
            active_filters[f[0]] = request.args[f[0]]
    sql_where = f"WHERE {' AND '.join(where)}" if where else ""
    total = query(f"SELECT COUNT(*) n FROM {res_name} {sql_where}", args, one=True)["n"]
    page = max(1, request.args.get("page", 1, type=int))
    rows = query(f"SELECT * FROM {res_name} {sql_where} ORDER BY {res['order']} LIMIT ? OFFSET ?",
                 args + [PER_PAGE, (page - 1) * PER_PAGE])
    cols = []
    for c in res["list"]:
        if c in fields:
            cols.append((c, fields[c][1], fields[c]))
        else:
            cols.append((c, {"slug": "網址", "last_login": "最後登入", "file": "檔案"}.get(c, c), None))
    filters = [(f[0], f[1], field_choices(f)) for f in res["fields"] if f[3].get("filter")]
    return render_template("admin/list.html", res=res, res_name=res_name, rows=rows, cols=cols, display=display,
                           q=q, filters=filters, active_filters=active_filters, total=total, page=page,
                           pages=max(1, (total + PER_PAGE - 1) // PER_PAGE))


@bp.route("/r/<res_name>/new", methods=["GET", "POST"])
@bp.route("/r/<res_name>/<int:rid>", methods=["GET", "POST"])
def res_edit(res_name, rid=None):
    res = get_res(res_name)
    row = None
    if rid:
        row = query(f"SELECT * FROM {res_name} WHERE id=?", (rid,), one=True)
        if not row:
            abort(404)
    elif res.get("no_create"):
        abort(404)
    errors, values = {}, {}
    if request.method == "POST":
        data, errors = parse_form(res_name, res, row)
        values = data
        if not errors:
            ts = now_str()
            if res_name != "users":
                data["updated_at"], data["updated_by"] = ts, g.user["display_name"]
            if row:
                sets = ", ".join(f"{k}=?" for k in data)
                execute(f"UPDATE {res_name} SET {sets} WHERE id=?", list(data.values()) + [rid])
                action = "修改"
            else:
                data["created_at"] = ts
                cols = ", ".join(data)
                rid = execute(f"INSERT INTO {res_name}({cols}) VALUES({','.join('?' * len(data))})", list(data.values()))
                action = "新增"
            row = query(f"SELECT * FROM {res_name} WHERE id=?", (rid,), one=True)
            log_action(g.user["username"], action, f"{res['singular']}：{row_label(res_name, row)}")
            flash(f"已{action}{res['singular']}「{row_label(res_name, row)}」。", "ok")
            if request.form.get("_next") == "new":
                return redirect(url_for("admin.res_edit", res_name=res_name))
            return redirect(url_for("admin.res_edit", res_name=res_name, rid=rid))
        flash("請修正以下標示的欄位。", "error")
    else:
        if row:
            values = dict(row)
        else:
            values = {f[0]: f[3].get("default", "") for f in res["fields"]}
            # 預設值：今日日期、篩選中的類別
            for f in res["fields"]:
                if f[2] == "date" and f[0] == "date":
                    values[f[0]] = today_str()
                if request.args.get(f[0]):
                    values[f[0]] = request.args[f[0]]
            if res_name == "awards":
                values["school_year"] = C.school_year_of(today_str())
    preview = res["preview"](row) if row and res.get("preview") else None
    return render_template("admin/form.html", res=res, res_name=res_name, row=row, values=values, errors=errors,
                           field_choices=field_choices, preview=preview)


@bp.route("/r/<res_name>/<int:rid>/delete", methods=["POST"])
def res_delete(res_name, rid):
    res = get_res(res_name)
    if res.get("no_delete"):
        abort(403)
    row = query(f"SELECT * FROM {res_name} WHERE id=?", (rid,), one=True)
    if not row:
        abort(404)
    if res_name == "users" and rid == g.user["id"]:
        flash("不可刪除自己的帳戶。", "error")
        return redirect(url_for("admin.res_list", res_name=res_name))
    execute(f"DELETE FROM {res_name} WHERE id=?", (rid,))
    log_action(g.user["username"], "刪除", f"{res['singular']}：{row_label(res_name, row)}")
    flash(f"已刪除「{row_label(res_name, row)}」。", "ok")
    return redirect(url_for("admin.res_list", res_name=res_name))


@bp.route("/r/<res_name>/<int:rid>/toggle", methods=["POST"])
def res_toggle(res_name, rid):
    res = get_res(res_name)
    col = "visible" if res_name == "sections" else "in_nav" if res_name == "pages" else "active" if res_name == "users" else "published"
    if res_name == "users" and rid == g.user["id"]:
        abort(400)
    execute(f"UPDATE {res_name} SET {col} = 1 - {col} WHERE id=?", (rid,))
    row = query(f"SELECT * FROM {res_name} WHERE id=?", (rid,), one=True)
    log_action(g.user["username"], "公開" if row[col] else "隱藏", f"{res['singular']}：{row_label(res_name, row)}")
    return redirect(request.referrer or url_for("admin.res_list", res_name=res_name))


@bp.route("/r/<res_name>/<int:rid>/copy", methods=["POST"])
def res_copy(res_name, rid):
    res = get_res(res_name)
    if res.get("no_create") or res_name == "users":
        abort(403)
    row = dict(query(f"SELECT * FROM {res_name} WHERE id=?", (rid,), one=True) or abort(404))
    row.pop("id")
    for k in ("title", "competition", "question"):
        if k in row:
            row[k] = f"{row[k]}（副本）"
    if res_name == "sections":
        row["anchor"] = f"{row['anchor']}-{uuid.uuid4().hex[:4]}"
    if "published" in row:
        row["published"] = 0
    row["created_at"] = row["updated_at"] = now_str()
    row["updated_by"] = g.user["display_name"]
    new_id = execute(f"INSERT INTO {res_name}({','.join(row)}) VALUES({','.join('?' * len(row))})", list(row.values()))
    flash("已建立副本（未公開），請修改後勾選「公開顯示」。", "ok")
    return redirect(url_for("admin.res_edit", res_name=res_name, rid=new_id))


# ------------------------------------------------------------------
# 學生成就：大量匯入
# ------------------------------------------------------------------
IMPORT_COLS = ["date", "category", "competition", "result", "students"]


@bp.route("/awards/import", methods=["GET", "POST"])
def awards_import():
    require_role("editor")
    report = None
    text = ""
    if request.method == "POST":
        text = request.form.get("data", "")
        if request.files.get("csvfile") and request.files["csvfile"].filename:
            text = request.files["csvfile"].read().decode("utf-8-sig", errors="replace")
        cat_lookup = {**{k: k for k in C.AWARD_CATEGORIES}, **{v: k for k, v in C.AWARD_CATEGORIES.items()}}
        ok_rows, bad = [], []
        dialect = "excel-tab" if "\t" in text else "excel"
        for i, rec in enumerate(csv.reader(io.StringIO(text), dialect=dialect), start=1):
            rec = [c.strip() for c in rec]
            if not any(rec) or rec[0] in ("日期", "date"):
                continue
            rec += [""] * (5 - len(rec))
            d, cat, comp, res_, stu = rec[:5]
            dd = valid_date(d.replace("/", "-"))
            problems = []
            if not dd:
                problems.append("日期格式不正確（應為 2026-11-15）")
            elif not (2000 <= dd.year <= date.fromisoformat(today_str()).year + 1):
                problems.append(f"年份 {dd.year} 看來不正確")
            if cat not in cat_lookup:
                problems.append("範疇須為：學術與創科／體藝／服務與領袖")
            if not comp or not res_:
                problems.append("缺少比賽名稱或獎項")
            if problems:
                bad.append((i, rec[:5], "；".join(problems)))
            else:
                ok_rows.append((C.school_year_of(dd.isoformat()), dd.isoformat(), cat_lookup[cat], comp, res_, stu))
        if request.form.get("confirm") == "1" and not bad and ok_rows:
            ts = now_str()
            db = get_db()
            db.executemany(
                "INSERT INTO awards(school_year,date,category,competition,result,students,published,created_at,updated_at,updated_by) "
                "VALUES(?,?,?,?,?,?,1,?,?,?)", [r + (ts, ts, g.user["display_name"]) for r in ok_rows])
            db.commit()
            log_action(g.user["username"], "匯入", f"學生成就 {len(ok_rows)} 項")
            flash(f"已匯入 {len(ok_rows)} 項學生成就。", "ok")
            return redirect(url_for("admin.res_list", res_name="awards"))
        report = {"ok": ok_rows, "bad": bad}
    return render_template("admin/import.html", report=report, text=text, C=C)


@bp.app_errorhandler(403)
def forbidden(_e):
    return render_template("admin/error.html", code=403, msg="你的帳戶沒有此功能的權限，請聯絡網站管理員。"), 403


@bp.app_errorhandler(400)
def bad_request(e):
    return render_template("admin/error.html", code=400, msg=getattr(e, "description", "請求無效。")), 400
