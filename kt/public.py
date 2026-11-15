"""前台：家長及公眾瀏覽的頁面。"""
from flask import Blueprint, abort, current_app, render_template, request, send_from_directory, url_for, Response

from . import content as C
from .db import query
from . import today_str

bp = Blueprint("public", __name__)
PAGE_SIZE = 12


def nav_pages():
    pages = query("SELECT * FROM pages WHERE in_nav=1 ORDER BY sort, id")
    secs = query("SELECT page_id, anchor, title FROM sections WHERE visible=1 ORDER BY sort, id")
    by_page = {}
    for s in secs:
        by_page.setdefault(s["page_id"], []).append(s)
    return [{"page": p, "sections": by_page.get(p["id"], [])} for p in pages]


@bp.app_context_processor
def inject_nav():
    if request.blueprint == "public":
        return {"NAV": nav_pages()}
    return {}


def posts(types, limit=None, featured=False):
    types = [types] if isinstance(types, str) else list(types)
    sql = f"SELECT * FROM posts WHERE published=1 AND type IN ({','.join('?' * len(types))})"
    if featured:
        sql += " AND featured=1"
    sql += " ORDER BY date DESC, id DESC"
    if limit:
        sql += f" LIMIT {int(limit)}"
    return query(sql, types)


def upcoming_events(limit=6):
    t = today_str()
    return query(
        "SELECT * FROM events WHERE published=1 AND (CASE WHEN end_date!='' THEN end_date ELSE date END) >= ? "
        "ORDER BY date LIMIT ?", (t, limit))


def load_widget(widget):
    """把區塊附加的動態內容載入。"""
    if not widget:
        return None
    kind, _, arg = widget.partition(":")
    if kind == "posts":
        return {"kind": "posts", "items": posts(arg)}
    if kind == "awards":
        rows = query("SELECT * FROM awards WHERE published=1 ORDER BY school_year DESC, date DESC")
        years = sorted({r["school_year"] for r in rows}, reverse=True)
        return {"kind": "awards", "items": rows, "years": years}
    if kind == "awards_featured":
        return {"kind": "awards_featured",
                "items": query("SELECT * FROM awards WHERE published=1 AND featured=1 ORDER BY date DESC LIMIT 6")}
    if kind == "voices":
        return {"kind": "voices", "items": query(
            "SELECT * FROM voices WHERE published=1 AND role=? ORDER BY sort, id", (arg,))}
    if kind == "faq":
        if arg:
            rows = query("SELECT * FROM faqs WHERE published=1 AND grp=? ORDER BY sort, id", (arg,))
        else:
            rows = query("SELECT * FROM faqs WHERE published=1 ORDER BY sort, id")
        groups = {}
        for r in rows:
            groups.setdefault(r["grp"], []).append(r)
        ordered = [(k, C.FAQ_GROUPS.get(k, k), groups[k]) for k in C.FAQ_GROUPS if k in groups]
        return {"kind": "faq", "groups": ordered, "grouped": not arg}
    if kind == "events":
        return {"kind": "events", "items": upcoming_events(8)}
    if kind == "docs":
        cats = arg.split("+")
        rows = query(
            f"SELECT * FROM documents WHERE published=1 AND category IN ({','.join('?' * len(cats))}) "
            "ORDER BY date DESC, id DESC", cats)
        return {"kind": "docs", "items": rows, "multi": len(cats) > 1}
    if kind in ("contact", "plan_roadmap"):
        return {"kind": kind}
    return None


@bp.route("/")
def home():
    return render_template(
        "index.html",
        news=posts("news", 6),
        joy=posts("joy", 6),
        activity=posts("activity", 6),
        stories=posts(["story", "activity", "joy"], 5, featured=True),
        featured_awards=query("SELECT * FROM awards WHERE published=1 AND featured=1 ORDER BY date DESC LIMIT 3"),
        events=upcoming_events(5),
        voices=query("SELECT * FROM voices WHERE published=1 ORDER BY sort, id LIMIT 3"),
        highlights=query("SELECT * FROM highlights WHERE published=1 ORDER BY sort, id"),
        message=(posts("message", 1) or [None])[0],
    )


@bp.route("/news")
def news_list():
    t = request.args.get("type", "")
    page = max(1, request.args.get("page", 1, type=int))
    types = [t] if t in C.POST_TYPES else list(C.POST_TYPES)
    ph = ",".join("?" * len(types))
    total = query(f"SELECT COUNT(*) n FROM posts WHERE published=1 AND type IN ({ph})", types, one=True)["n"]
    rows = query(
        f"SELECT * FROM posts WHERE published=1 AND type IN ({ph}) ORDER BY date DESC, id DESC LIMIT ? OFFSET ?",
        types + [PAGE_SIZE, (page - 1) * PAGE_SIZE])
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    return render_template("news_list.html", items=rows, cur_type=t, page=page, pages=pages)


@bp.route("/news/<int:post_id>")
def news_detail(post_id):
    p = query("SELECT * FROM posts WHERE id=? AND published=1", (post_id,), one=True)
    if not p:
        abort(404)
    related = query(
        "SELECT * FROM posts WHERE published=1 AND type=? AND id!=? ORDER BY date DESC LIMIT 3", (p["type"], p["id"]))
    return render_template("news_detail.html", p=p, related=related)


@bp.route("/calendar")
def calendar():
    rows = query("SELECT * FROM events WHERE published=1 ORDER BY date")
    months = {}
    for r in rows:
        months.setdefault(r["date"][:7], []).append(r)
    return render_template("calendar.html", months=months)


@bp.route("/uploads/<path:name>")
def uploads(name):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], name, max_age=86400)


@bp.route("/sitemap.xml")
def sitemap():
    urls = [url_for("public.home", _external=True), url_for("public.news_list", _external=True),
            url_for("public.calendar", _external=True)]
    urls += [url_for("public.page", slug=p["slug"], _external=True) for p in query("SELECT slug FROM pages")]
    urls += [url_for("public.news_detail", post_id=r["id"], _external=True)
             for r in query("SELECT id FROM posts WHERE published=1")]
    body = "".join(f"<url><loc>{u}</loc></url>" for u in urls)
    return Response(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>',
                    mimetype="application/xml")


@bp.route("/<slug>")
def page(slug):
    p = query("SELECT * FROM pages WHERE slug=?", (slug,), one=True)
    if not p:
        abort(404)
    secs = query("SELECT * FROM sections WHERE page_id=? AND visible=1 ORDER BY sort, id", (p["id"],))
    sections = [{"s": s, "w": load_widget(s["widget"])} for s in secs]
    return render_template("page.html", p=p, sections=sections, is_en=(slug == "en"))


@bp.app_errorhandler(404)
def not_found(_e):
    if request.path.startswith("/admin"):
        return render_template("admin/error.html", code=404, msg="找不到此頁"), 404
    return render_template("404.html"), 404
