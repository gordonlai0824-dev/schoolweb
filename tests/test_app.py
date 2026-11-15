"""自動測試：python -m unittest discover -s tests"""
import io
import os
import re
import shutil
import tempfile
import unittest

TMP = tempfile.mkdtemp(prefix="kt-test-")
os.environ["KT_INSTANCE"] = TMP
os.environ["KT_ADMIN_PASSWORD"] = "admin-pass-123"
os.environ["KT_TODAY"] = "2026-11-15"

from kt import create_app  # noqa: E402
from kt.sanitize import clean_html  # noqa: E402

app = create_app({"TESTING": True})

PNG = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
       b"\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82")


def csrf(client, url):
    html = client.get(url).get_data(as_text=True)
    return re.search(r'name="_csrf" value="([^"]+)"', html).group(1)


def login(client, user="admin", pw="admin-pass-123"):
    token = csrf(client, "/admin/login")
    return client.post("/admin/login", data={"_csrf": token, "username": user, "password": pw})


class PublicTests(unittest.TestCase):
    def setUp(self):
        self.c = app.test_client()

    def test_pages(self):
        for url in ["/", "/about", "/development", "/learning", "/growth", "/stories", "/parents", "/info",
                    "/en", "/news", "/news?type=story", "/calendar", "/sitemap.xml"]:
            self.assertEqual(self.c.get(url).status_code, 200, url)
        self.assertEqual(self.c.get("/no-such-page").status_code, 404)

    def test_home_priorities(self):
        html = self.c.get("/").get_data(as_text=True)
        for text in ["培養自主探究者", "小一入學", "三年發展計劃", "校長的話", "學生喜訊", "為何選擇基道"]:
            self.assertIn(text, html)

    def test_nav_has_seven_parent_oriented_menus(self):
        html = self.c.get("/").get_data(as_text=True)
        nav = html.split('id="main-nav"')[1].split("</nav>")[0]
        for t in ["認識基道", "發展新里程", "學與教", "學生成長", "成果與故事", "家長專區", "學校資訊"]:
            self.assertIn(t, nav)

    def test_english_page_lang(self):
        self.assertIn('lang="en"', self.c.get("/en").get_data(as_text=True))


class AdminTests(unittest.TestCase):
    def setUp(self):
        self.c = app.test_client()

    def test_requires_login(self):
        r = self.c.get("/admin/r/posts")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/admin/login", r.headers["Location"])

    def test_bad_password(self):
        r = login(self.c, pw="wrong")
        self.assertIn("不正確", r.get_data(as_text=True))

    def test_csrf_required(self):
        login(self.c)
        r = self.c.post("/admin/r/posts/new", data={"title": "x"})
        self.assertEqual(r.status_code, 400)

    def test_create_edit_delete_post(self):
        login(self.c)
        token = csrf(self.c, "/admin/r/posts/new")
        r = self.c.post("/admin/r/posts/new", data={
            "_csrf": token, "type": "news", "title": "測試消息", "date": "2026-11-15", "tag": "ai",
            "summary": "摘要", "body": '<p>內容<script>alert(1)</script><a href="javascript:x">壞</a></p>',
            "published": "1", "image": (io.BytesIO(PNG), "a.png")},
            content_type="multipart/form-data")
        self.assertEqual(r.status_code, 302)
        pid = int(r.headers["Location"].rstrip("/").split("/")[-1])
        page = app.test_client().get(f"/news/{pid}").get_data(as_text=True)
        self.assertIn("測試消息", page)
        self.assertNotIn("alert(1)", page)
        self.assertNotIn("javascript:", page)
        self.assertIn("/uploads/", page)
        token = csrf(self.c, f"/admin/r/posts/{pid}")
        self.c.post(f"/admin/r/posts/{pid}/toggle", data={"_csrf": token})
        self.assertEqual(app.test_client().get(f"/news/{pid}").status_code, 404)
        self.c.post(f"/admin/r/posts/{pid}/delete", data={"_csrf": token})
        self.assertEqual(self.c.get(f"/admin/r/posts/{pid}").status_code, 404)

    def test_award_year_validation(self):
        login(self.c)
        token = csrf(self.c, "/admin/r/awards/new")
        base = {"_csrf": token, "school_year": "2026-27", "category": "academic",
                "competition": "測試比賽", "result": "冠軍", "published": "1"}
        r = self.c.post("/admin/r/awards/new", data={**base, "date": "2036-03-01"})
        self.assertIn("看來不正確", r.get_data(as_text=True))
        r = self.c.post("/admin/r/awards/new", data={**base, "date": "2025-03-01"})
        self.assertIn("不在 2026-27 學年內", r.get_data(as_text=True))
        r = self.c.post("/admin/r/awards/new", data={**base, "date": "2026-10-01"})
        self.assertEqual(r.status_code, 302)

    def test_section_edit_updates_nav(self):
        login(self.c)
        token = csrf(self.c, "/admin/r/sections/new")
        r = self.c.post("/admin/r/sections/new", data={
            "_csrf": token, "page_id": "6", "title": "新增測試區塊", "anchor": "test-block",
            "body": "<p>你好</p>", "widget": "", "sort": "99", "visible": "1", "icon": ""})
        self.assertEqual(r.status_code, 302)
        html = app.test_client().get("/parents").get_data(as_text=True)
        self.assertIn("新增測試區塊", html)
        self.assertIn('href="/parents#test-block"', html)
        r = self.c.post("/admin/r/sections/new", data={
            "_csrf": token, "page_id": "6", "title": "重複", "anchor": "test-block", "sort": "1"})
        self.assertIn("相同代號", r.get_data(as_text=True))

    def test_settings_and_check(self):
        login(self.c)
        token = csrf(self.c, "/admin/settings")
        r = self.c.post("/admin/settings", data={"_csrf": token, "phone": "2345 6789", "show_proto_note": "0"})
        self.assertEqual(r.status_code, 302)
        html = app.test_client().get("/").get_data(as_text=True)
        self.assertIn("2345 6789", html)
        self.assertNotIn("proto-note", html)
        self.assertEqual(self.c.get("/admin/check").status_code, 200)

    def test_editor_role_limits(self):
        login(self.c)
        token = csrf(self.c, "/admin/r/users/new")
        r = self.c.post("/admin/r/users/new", data={
            "_csrf": token, "username": "teacher1", "display_name": "陳老師", "role": "editor",
            "password": "teacher-pass", "active": "1"})
        self.assertEqual(r.status_code, 302)
        t = app.test_client()
        login(t, "teacher1", "teacher-pass")
        self.assertEqual(t.get("/admin/r/posts").status_code, 200)
        self.assertEqual(t.get("/admin/r/users").status_code, 403)
        self.assertEqual(t.get("/admin/settings").status_code, 403)

    def test_awards_import(self):
        login(self.c)
        token = csrf(self.c, "/admin/awards/import")
        data = "2026-11-01\t體藝\t測試舞蹈比賽\t金獎\t4A 王同學\n2036-01-01\t體藝\t錯誤比賽\t銀獎\t"
        r = self.c.post("/admin/awards/import", data={"_csrf": token, "data": data})
        self.assertIn("1 項有問題", r.get_data(as_text=True))
        data = "2026-11-01\t體藝\t測試舞蹈比賽\t金獎\t4A 王同學"
        r = self.c.post("/admin/awards/import", data={"_csrf": token, "data": data, "confirm": "1"})
        self.assertEqual(r.status_code, 302)
        self.assertIn("測試舞蹈比賽", app.test_client().get("/stories").get_data(as_text=True))

    def test_editor_image_upload(self):
        login(self.c)
        token = csrf(self.c, "/admin/r/posts/new")
        r = self.c.post("/admin/upload", data={"file": (io.BytesIO(PNG), "x.png")},
                        headers={"X-CSRF-Token": token}, content_type="multipart/form-data")
        self.assertEqual(r.status_code, 200)
        resp = self.c.get(r.get_json()["url"]); self.assertEqual(resp.status_code, 200); resp.close()
        r = self.c.post("/admin/upload", data={"file": (io.BytesIO(b"x"), "x.exe")},
                        headers={"X-CSRF-Token": token}, content_type="multipart/form-data")
        self.assertEqual(r.status_code, 400)


class SanitizeTests(unittest.TestCase):
    def test_clean(self):
        self.assertEqual(clean_html('<p onclick="x()">a</p>'), "<p>a</p>")
        self.assertEqual(clean_html("<script>bad()</script><b>ok</b>"), "<b>ok</b>")
        self.assertNotIn("javascript", clean_html('<a href="javascript:alert(1)">x</a>'))
        self.assertIn('class="card"', clean_html('<div class="card">x</div>'))
        self.assertEqual(clean_html('<iframe src="https://evil.com/x"></iframe>'), "")
        self.assertIn("youtube-nocookie", clean_html('<iframe src="https://www.youtube-nocookie.com/embed/abc"></iframe>'))
        self.assertIn('rel="noopener noreferrer"', clean_html('<a href="https://x.com" target="_blank">x</a>'))


def tearDownModule():
    shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
