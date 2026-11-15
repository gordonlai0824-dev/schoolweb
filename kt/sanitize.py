"""後台富文本內容清理：只保留安全標籤及屬性，移除 script／事件屬性／javascript: 連結。"""
from html import escape
from html.parser import HTMLParser
import re

ALLOWED_TAGS = {
    "p", "br", "hr", "strong", "b", "em", "i", "u", "s", "small", "mark", "sub", "sup",
    "h2", "h3", "h4", "ul", "ol", "li", "blockquote", "a", "img", "figure", "figcaption",
    "table", "thead", "tbody", "tr", "th", "td", "caption", "div", "span", "section",
    "details", "summary", "iframe",
}
VOID_TAGS = {"br", "hr", "img"}
GLOBAL_ATTRS = {"class", "id", "title", "lang", "style"}
TAG_ATTRS = {
    "a": {"href", "target", "rel"},
    "img": {"src", "alt", "width", "height", "loading"},
    "td": {"colspan", "rowspan"},
    "th": {"colspan", "rowspan", "scope"},
    "ol": {"start"},
    "details": {"open"},
    "iframe": {"src", "width", "height", "allow", "allowfullscreen", "title", "loading"},
}
# 只容許嵌入以下影片平台
IFRAME_HOSTS = ("https://www.youtube.com/embed/", "https://www.youtube-nocookie.com/embed/",
                "https://player.vimeo.com/video/")
DROP_CONTENT = {"script", "style", "noscript", "template", "object", "embed", "form"}
SAFE_URL = re.compile(r"^(https?:|mailto:|tel:|/|#|\.{0,2}/|[\w\-./?=&%#]+$)", re.I)
SAFE_STYLE = re.compile(r"^[\w\s\-:;#%.,()]*$")


class _Cleaner(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.stack = []
        self.drop_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in DROP_CONTENT:
            self.drop_depth += 1
            return
        if self.drop_depth or tag not in ALLOWED_TAGS:
            return
        allowed = GLOBAL_ATTRS | TAG_ATTRS.get(tag, set())
        clean = []
        for name, value in attrs:
            name = name.lower()
            if name not in allowed or name.startswith("on"):
                continue
            value = value or ""
            if name in ("href", "src"):
                v = value.strip()
                if not SAFE_URL.match(v) or v.lower().startswith(("javascript:", "data:", "vbscript:")):
                    continue
                if tag == "iframe" and not v.startswith(IFRAME_HOSTS):
                    return  # 不安全的嵌入，整個略過
            if name == "style" and ("expression" in value.lower() or "url(" in value.lower()
                                    or not SAFE_STYLE.match(value)):
                continue
            clean.append((name, value))
        if tag == "iframe" and not any(n == "src" for n, _ in clean):
            return
        if tag == "a" and any(n == "target" and v == "_blank" for n, v in clean):
            clean = [(n, v) for n, v in clean if n != "rel"] + [("rel", "noopener noreferrer")]
        attr_str = "".join(f' {n}="{escape(v, quote=True)}"' for n, v in clean)
        self.out.append(f"<{tag}{attr_str}>")
        if tag not in VOID_TAGS:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_TAGS and self.stack and self.stack[-1] == tag.lower():
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in DROP_CONTENT:
            self.drop_depth = max(0, self.drop_depth - 1)
            return
        if self.drop_depth or tag not in ALLOWED_TAGS or tag in VOID_TAGS:
            return
        if tag in self.stack:
            while self.stack:
                t = self.stack.pop()
                self.out.append(f"</{t}>")
                if t == tag:
                    break

    def handle_data(self, data):
        if not self.drop_depth:
            self.out.append(escape(data, quote=False))

    def close(self):
        super().close()
        while self.stack:
            self.out.append(f"</{self.stack.pop()}>")
        return "".join(self.out)


def clean_html(html):
    if not html:
        return ""
    parser = _Cleaner()
    parser.feed(html)
    return parser.close()
