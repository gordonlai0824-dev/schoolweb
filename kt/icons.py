"""線條圖示（24×24，stroke 風格），供前台及後台共用。"""
from markupsafe import Markup

ICONS = {
    "home": '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/>',
    "book": '<path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v17H6.5A2.5 2.5 0 0 0 4 21.5z"/><path d="M4 19.5V4.5"/><path d="M8 7h8M8 11h6"/>',
    "ai": '<rect x="5" y="5" width="14" height="14" rx="3"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/><path d="M9.5 15 11 9h2l1.5 6M10 13h4"/>',
    "heart": '<path d="M20.8 5.6a5 5 0 0 0-7.1 0L12 7.3l-1.7-1.7a5 5 0 0 0-7.1 7.1L12 21.5l8.8-8.8a5 5 0 0 0 0-7.1z"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14.2a6.5 6.5 0 0 1 3.5 5.8"/>',
    "star": '<path d="m12 2.5 2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9z"/>',
    "trophy": '<path d="M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M7 6H4a3 3 0 0 0 3 4M17 6h3a3 3 0 0 1-3 4"/><path d="M12 14v4M8 21h8M9 18h6"/>',
    "calendar": '<rect x="3" y="4.5" width="18" height="16.5" rx="2.5"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/><path d="M7.5 13.5h2M11 13.5h2M14.5 13.5h2M7.5 17h2M11 17h2"/>',
    "file": '<path d="M14 2.5H6.5A2 2 0 0 0 4.5 4.5v15a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V8z"/><path d="M14 2.5V8h5.5M8.5 13h7M8.5 17h5"/>',
    "bell": '<path d="M6 8.5a6 6 0 0 1 12 0c0 7 3 8.5 3 8.5H3s3-1.5 3-8.5"/><path d="M10 20.5a2 2 0 0 0 4 0"/>',
    "phone": '<path d="M21 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 1.1 4.2 2 2 0 0 1 3.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L7.1 9.7a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
    "mail": '<rect x="2.5" y="4.5" width="19" height="15" rx="2.5"/><path d="m3 6 9 7 9-7"/>',
    "map": '<path d="M12 21.5s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "bus": '<rect x="4" y="3" width="16" height="15" rx="3"/><path d="M4 11h16M8 21v-3M16 21v-3"/><circle cx="8" cy="14.5" r="1"/><circle cx="16" cy="14.5" r="1"/>',
    "meal": '<path d="M5 2.5v7a2 2 0 0 0 2 2h0a2 2 0 0 0 2-2v-7M7 2.5v19"/><path d="M17 21.5v-19c-2.5 1-4 3.5-4 7v4h4"/>',
    "school": '<path d="M2 21.5h20M4 21.5V10l8-5 8 5v11.5"/><path d="M12 5V2"/><path d="M12 2h3v2h-3"/><path d="M9 21.5v-5h6v5"/><path d="M7.5 12.5h2M14.5 12.5h2"/>',
    "sparkles": '<path d="M12 3 13.8 8.2 19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 15.5 19.8 17.7 22 18.5l-2.2.8L19 21.5l-.8-2.2-2.2-.8 2.2-.8z"/><path d="M5 2.5l.6 1.4L7 4.5l-1.4.6L5 6.5l-.6-1.4L3 4.5l1.4-.6z"/>',
    "compass": '<circle cx="12" cy="12" r="9.5"/><path d="m15.5 8.5-2 5-5 2 2-5z"/>',
    "flask": '<path d="M9.5 2.5h5M10 2.5v6L4.5 18.5A2 2 0 0 0 6.3 21.5h11.4a2 2 0 0 0 1.8-3L14 8.5v-6"/><path d="M7.2 15h9.6"/>',
    "globe": '<circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19M12 2.5a14.5 14.5 0 0 1 0 19M12 2.5a14.5 14.5 0 0 0 0 19"/>',
    "leaf": '<path d="M11 20.5A7 7 0 0 1 4 13.5C4 7 9.5 3.5 20 3.5c0 10.5-3.5 17-9 17z"/><path d="M4 21.5c3-6 6.5-9 11-11"/>',
    "hand": '<path d="M18 11V6.5a1.5 1.5 0 0 0-3 0V11M15 10.5V4.5a1.5 1.5 0 0 0-3 0v6M12 10.5V5.5a1.5 1.5 0 0 0-3 0V13"/><path d="M18 9.5a1.5 1.5 0 0 1 3 0V14a7.5 7.5 0 0 1-7.5 7.5h-1.3a7.5 7.5 0 0 1-5.6-2.5L3.3 15.5a1.6 1.6 0 0 1 2.4-2.1L9 16"/>',
    "music": '<path d="M9 18.5V5l12-2.5v13"/><circle cx="6" cy="18.5" r="3"/><circle cx="18" cy="16" r="3"/>',
    "palette": '<path d="M12 2.5a9.5 9.5 0 0 0 0 19c1.1 0 1.8-.9 1.8-1.9 0-.5-.2-.9-.5-1.3-.3-.3-.5-.8-.5-1.3 0-1 .8-1.9 1.9-1.9H17a4.5 4.5 0 0 0 4.5-4.5c0-4.6-4.3-8.1-9.5-8.1z"/><circle cx="7.5" cy="11" r="1.2"/><circle cx="10" cy="7" r="1.2"/><circle cx="15" cy="7.5" r="1.2"/>',
    "run": '<circle cx="14" cy="4" r="2"/><path d="m6 21 3.5-5 3 2V13l-3-3 2.5-3 3 3.5H19"/><path d="M5 11l3-3.5h3.5"/>',
    "chat": '<path d="M21 12a8.5 8.5 0 0 1-12.4 7.6L3 21l1.4-5.4A8.5 8.5 0 1 1 21 12z"/><path d="M8 10.5h8M8 14h5"/>',
    "shield": '<path d="M12 21.5s8-3.5 8-10V5l-8-2.5L4 5v6.5c0 6.5 8 10 8 10z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
    "target": '<circle cx="12" cy="12" r="9.5"/><circle cx="12" cy="12" r="5.5"/><circle cx="12" cy="12" r="1.5"/>',
    "bulb": '<path d="M9 18h6M10 21.5h4"/><path d="M12 2.5a6.5 6.5 0 0 0-4 11.6c.6.5 1 1.2 1 2V18h6v-1.9c0-.8.4-1.5 1-2A6.5 6.5 0 0 0 12 2.5z"/>',
    "grad": '<path d="M2 9 12 4l10 5-10 5z"/><path d="M6 11v5c0 1.5 2.7 3 6 3s6-1.5 6-3v-5M22 9v6"/>',
    "clipboard": '<rect x="5" y="4" width="14" height="17.5" rx="2"/><path d="M9 2.5h6v3H9z"/><path d="M8.5 11h7M8.5 15h5"/>',
    "video": '<rect x="2.5" y="5.5" width="14" height="13" rx="2.5"/><path d="m16.5 10 5-3v10l-5-3"/>',
    "image": '<rect x="3" y="3.5" width="18" height="17" rx="2.5"/><circle cx="8.5" cy="9" r="1.8"/><path d="m21 15.5-5-5L5 20.5"/>',
    "news": '<path d="M4 4.5h13v15a2 2 0 0 0 2 2H6a2 2 0 0 1-2-2z"/><path d="M17 8.5h3v11a2 2 0 0 1-4 0"/><path d="M7.5 8.5h6M7.5 12h6M7.5 15.5h4"/>',
    "cross": '<path d="M12 3v18M7 8h10"/>',
    "church": '<path d="M12 2v5M10 4h4"/><path d="M6 21.5V12l6-5 6 5v9.5"/><path d="M3 21.5h18M10 21.5v-4a2 2 0 0 1 4 0v4"/>',
    "check": '<path d="m4.5 12.5 5 5 10-11"/>',
    "edit": '<path d="M12 20.5h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
    "trash": '<path d="M3 6h18M8 6V4h8v2M6 6l1 15h10l1-15"/><path d="M10 10.5v6M14 10.5v6"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "logout": '<path d="M9 21.5H5a2 2 0 0 1-2-2v-15a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',
    "settings": '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>',
    "alert": '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/>',
    "layers": '<path d="m12 2.5 9.5 5-9.5 5-9.5-5z"/><path d="m2.5 12.5 9.5 5 9.5-5M2.5 17l9.5 5 9.5-5"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "arrow-up": '<path d="M12 19V5M5 12l7-7 7 7"/>',
    "arrow-right": '<path d="M5 12h14M12 5l7 7-7 7"/>',
    "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>',
    "close": '<path d="M18 6 6 18M6 6l12 12"/>',
    "play": '<path d="M7 4.5v15l12-7.5z" fill="currentColor" stroke="none"/>',
    "lock": '<rect x="4" y="10.5" width="16" height="11" rx="2.5"/><path d="M8 10.5V7a4 4 0 0 1 8 0v3.5"/>',
}

ICON_CHOICES = sorted(ICONS.keys())


def icon(name, cls="", size=None):
    path = ICONS.get(name, ICONS["star"])
    style = f' width="{size}" height="{size}"' if size else ""
    cls_attr = f' class="{cls}"' if cls else ""
    return Markup(
        f'<svg{cls_attr}{style} viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" '
        f'focusable="false">{path}</svg>'
    )
