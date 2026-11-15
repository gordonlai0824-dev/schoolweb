"""內容類別及選項（前台與後台共用）。"""

POST_TYPES = {
    "news": "最新消息",
    "joy": "學生喜訊",
    "activity": "校園活動",
    "story": "校園故事",
    "work": "學生作品",
    "media": "傳媒報導",
    "message": "校長短訊",
}

POST_TAGS = {
    "": "（不設標籤）",
    "ai": "AI／STEAM",
    "char": "品格教育",
    "academic": "學術",
    "arts": "藝術",
    "sport": "體育",
    "service": "服務與領袖",
    "parent": "家長",
    "admin": "學校行政",
}

AWARD_CATEGORIES = {
    "academic": "學術與創科",
    "arts": "體藝",
    "service": "服務與領袖",
}
AWARD_TAG_CLASS = {"academic": "ai", "arts": "arts", "service": "char"}

EVENT_KINDS = {
    "event": "學校活動",
    "holiday": "假期",
    "exam": "考試／評估",
    "parent": "家長活動",
    "admission": "入學事項",
}

DOC_CATEGORIES = {
    "plan": "計劃及報告",
    "notice": "家長通告",
    "form": "表格下載",
    "p1": "小一入學",
    "other": "其他文件",
}

FAQ_GROUPS = {
    "p1": "小一入學",
    "daily": "日常校園生活",
    "learning": "學習與評估",
    "support": "學生支援",
    "general": "其他",
}

VOICE_ROLES = {"parent": "家長", "student": "學生", "alumni": "校友"}

PAGE_STYLES = {"default": "基道藍", "ai": "AI 青藍", "char": "品格綠"}
HIGHLIGHT_COLORS = {"primary": "基道藍", "ai": "AI 青藍", "char": "品格綠", "accent": "暖橙", "rose": "玫紅"}

# 內頁區塊可附加的動態內容
WIDGETS = {
    "": "（只顯示文字內容）",
    "awards": "學生成就列表（可篩選）",
    "awards_featured": "精選成果故事",
    "posts:story": "校園故事列表",
    "posts:work": "學生作品列表",
    "posts:media": "傳媒報導列表",
    "posts:message": "校長短訊列表",
    "voices:alumni": "校友心聲",
    "voices:parent": "家長心聲",
    "voices:student": "學生心聲",
    "faq": "常見問題（全部）",
    "faq:p1": "常見問題（小一入學）",
    "events": "校曆（即將舉行）",
    "docs:plan": "文件：計劃及報告",
    "docs:notice": "文件：家長通告",
    "docs:form": "文件：表格下載",
    "docs:p1": "文件：小一入學",
    "contact": "聯絡資料及地圖",
    "plan_roadmap": "三年發展路線圖",
}


def school_year_of(date_str):
    """2026-11-15 → 2026-27（九月開始新學年）。"""
    y, m = int(date_str[:4]), int(date_str[5:7])
    start = y if m >= 9 else y - 1
    return f"{start}-{str(start + 1)[-2:]}"


def school_year_range(sy):
    """2026-27 → ('2026-09-01', '2027-08-31')"""
    start = int(sy[:4])
    return f"{start}-09-01", f"{start + 1}-08-31"


def school_year_choices(today):
    cur = int(school_year_of(today)[:4])
    return [f"{y}-{str(y + 1)[-2:]}" for y in range(cur + 1, cur - 6, -1)]
