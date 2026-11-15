"""基道小學網站（前台 + 後台內容管理系統）。"""
import os
import secrets
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import click
from flask import Flask, g
from werkzeug.security import generate_password_hash

from . import content as C
from .db import close_db, get_settings, init_schema, now_str
from .icons import icon

BASE_DIR = Path(__file__).resolve().parent.parent


def _secret_key(instance):
    env = os.environ.get("KT_SECRET_KEY")
    if env:
        return env
    f = instance / "secret_key"
    if not f.exists():
        f.write_text(secrets.token_hex(32))
        f.chmod(0o600)
    return f.read_text().strip()


def create_app(test_config=None):
    instance = Path(os.environ.get("KT_INSTANCE", BASE_DIR / "instance"))
    instance.mkdir(parents=True, exist_ok=True)
    (instance / "uploads").mkdir(exist_ok=True)

    app = Flask(__name__, instance_path=str(instance))
    app.config.update(
        SECRET_KEY=_secret_key(instance),
        DATABASE=str(instance / "site.db"),
        UPLOAD_FOLDER=str(instance / "uploads"),
        MAX_CONTENT_LENGTH=25 * 1024 * 1024,          # 單一上載上限 25MB
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("KT_SECURE_COOKIES") == "1",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        TODAY=os.environ.get("KT_TODAY"),               # 測試用：固定「今日」日期
    )
    if test_config:
        app.config.update(test_config)

    app.teardown_appcontext(close_db)
    _ensure_db(app)

    from .public import bp as public_bp
    from .admin import bp as admin_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.context_processor
    def inject():
        return {"S": get_settings(), "icon": icon, "C": C, "today": today_str()}

    app.jinja_env.filters["zhdate"] = zhdate
    app.jinja_env.filters["lines"] = lambda s: [x.strip() for x in (s or "").splitlines() if x.strip()]
    app.jinja_env.globals["month_short"] = lambda d: f"{int(d[5:7])}月"
    app.jinja_env.globals["day_of"] = lambda d: str(int(d[8:10]))

    @app.after_request
    def security_headers(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return resp

    _register_cli(app)
    return app


def today_str():
    from flask import current_app
    return current_app.config.get("TODAY") or date.today().isoformat()


def zhdate(d, short=False):
    if not d:
        return ""
    y, m, dd = d[:4], int(d[5:7]), int(d[8:10])
    return f"{m}月{dd}日" if short else f"{y}年{m}月{dd}日"


def _ensure_db(app):
    """首次啟動時自動建立資料庫及示範內容。"""
    fresh = not Path(app.config["DATABASE"]).exists()
    conn = sqlite3.connect(app.config["DATABASE"])
    try:
        init_schema(conn)
        if fresh:
            from .seed import seed
            seed(conn)
            pw = os.environ.get("KT_ADMIN_PASSWORD") or secrets.token_urlsafe(9)
            conn.execute(
                "INSERT INTO users(username, display_name, password_hash, role, created_at) VALUES(?,?,?,?,?)",
                ("admin", "網站管理員", generate_password_hash(pw), "admin", now_str()))
            conn.commit()
            if not os.environ.get("KT_ADMIN_PASSWORD"):
                print("=" * 60)
                print(" 已建立網站管理員帳戶")
                print(f"   登入名稱：admin    密碼：{pw}")
                print("   請登入 /admin 後立即更改密碼。")
                print("=" * 60)
    finally:
        conn.close()


def _register_cli(app):
    @app.cli.command("create-user")
    @click.argument("username")
    @click.option("--name", default="", help="顯示名稱")
    @click.option("--admin", is_flag=True, help="設為管理員")
    @click.password_option()
    def create_user(username, name, admin, password):
        """建立後台帳戶。"""
        conn = sqlite3.connect(app.config["DATABASE"])
        conn.execute(
            "INSERT INTO users(username, display_name, password_hash, role, created_at) VALUES(?,?,?,?,?)",
            (username, name or username, generate_password_hash(password), "admin" if admin else "editor", now_str()))
        conn.commit()
        conn.close()
        click.echo(f"已建立帳戶 {username}")

    @app.cli.command("reset-password")
    @click.argument("username")
    @click.password_option()
    def reset_password(username, password):
        """重設後台帳戶密碼。"""
        conn = sqlite3.connect(app.config["DATABASE"])
        n = conn.execute("UPDATE users SET password_hash=? WHERE username=?",
                         (generate_password_hash(password), username)).rowcount
        conn.commit()
        conn.close()
        click.echo("已重設密碼" if n else "找不到此帳戶")
