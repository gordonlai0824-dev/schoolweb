"""初始內容：首次建立資料庫時寫入。全部內容其後均可在後台修改或刪除。

注意：標示「示範」的新聞、獎項、心聲及數字為版面示範，正式發佈前須由學校核實或替換。
"""
from .db import now_str


def ph(label, kind="", ratio=""):
    cls = " ".join(c for c in ("ph", f"ph-{kind}" if kind else "", f"ph-{ratio}" if ratio else "") if c)
    return f'<div class="{cls}"><span class="ph-label">相片：{label}</span></div>'


SETTINGS = {
    # 學校資料
    "school_name": "中華基督教會灣仔堂基道小學（九龍城）",
    "school_name_en": "CCC Wanchai Church Kei To Primary School (Kowloon City)",
    "school_short": "基道小學",
    "sponsor": "中華基督教會灣仔堂",
    "address": "九龍九龍城靠背壟道170號",
    "address_en": "170 Kau Pui Lung Road, Kowloon City, Kowloon",
    "phone": "（請於後台填寫）",
    "fax": "（請於後台填寫）",
    "email": "（請於後台填寫）",
    "office_hours": "星期一至五 上午8:00 – 下午5:00（示範，請核實）",
    "map_query": "九龍城靠背壟道170號",
    "philosophy": "知識淵博、善思明辨、堅毅前行",
    # 網站
    "show_proto_note": "1",
    "proto_note": "網站設計原型：部分文字、數字及相片為示範內容，正式發佈前須由學校核實。",
    "footer_note": "本網站內容由學校老師透過網站後台更新。",
    # 首頁橫幅
    "hero_tag": "2026–2029 學校發展計劃",
    "hero_title": "培養自主探究者",
    "hero_title_hl": "培育完全品格",
    "hero_lead": "在基道，孩子學會提問、探究與創造，也學會誠信、承擔與關愛。我們以「AI新學力」及「完全品格教育」，陪伴每一位孩子成為自信、善良、有承擔的「基道人」。",
    "hero_video_url": "",
    "hero_video_caption": "一分鐘認識基道 — 校園生活短片",
    "hero_badge_num": "2026",
    "hero_badge_text": "新校長上任，開啟「基小新里程」",
    # 校長的話
    "principal_name": "（校長姓名）",
    "principal_title": "校長",
    "principal_quote": "教育不只是傳授知識，更是點燃孩子探究世界的好奇心；並以品格為根，讓他們在AI時代仍能誠信、善良、有承擔。",
    "principal_body": "2026–2027 學年，學校訂下未來三年的兩項發展重點：「培養自主探究者，掌握AI新學力」及「培育完全品格，共建基小新里程」。我們期望每位基道學生都能主動提問、善用科技解決真實問題，同時在誠信、責任感及關愛中全人成長。",
    "principal_video_url": "",
    # 發展計劃
    "plan_years": "2026–2029",
    "plan_stage": "1",
    "plan_ai_title": "培養自主探究者，掌握AI新學力",
    "plan_ai_points": "以「提問—探究—創造—反思」為課堂主線\n建立P1–P6縱向AI素養及編程課程\n善用電子學習平台，推動自主學習及預習\n跨學科專題研習，解決校園及社區真實問題",
    "plan_char_title": "培育完全品格，共建基小新里程",
    "plan_char_points": "以聖經價值及十二個首要價值觀為基礎\n「我是基道人」獎勵計劃，聚焦誠信及責任感\n僕人領袖培訓及全校服務學習\n家校同行，共同培育孩子的品格",
    "roadmap_1_title": "奠基",
    "roadmap_1_text": "建立課堂探究框架及AI素養課程；推出品格獎勵計劃。",
    "roadmap_2_title": "深化",
    "roadmap_2_text": "擴展跨學科專題；發展學生領袖及服務學習。",
    "roadmap_3_title": "展現",
    "roadmap_3_text": "學生成果展及自主學習歷程；檢視成效、持續優化。",
    # 數字一覽（示範，請核實）
    "stat_1_n": "2", "stat_1_l": "三年發展重點",
    "stat_2_n": "6+", "stat_2_l": "獲獎範疇：語文、數學、STEAM、音樂、體育、藝術",
    "stat_3_n": "P1–P6", "stat_3_l": "全校推行「我是基道人」獎勵計劃",
    "stat_4_n": "AI", "stat_4_l": "縱向AI素養及編程課程",
}

PAGES = [
    # slug, title, title_en, intro, style, sort, in_nav
    ("about", "認識基道", "About Us",
     "以基督愛人如己的精神辦學，讓每個孩子在關愛中發現自己的潛能。", "default", 1, 1),
    ("development", "發展新里程", "Development",
     "2026–2029 三年發展計劃：培養自主探究者，掌握AI新學力；培育完全品格，共建基小新里程。", "ai", 2, 1),
    ("learning", "學與教", "Learning & Teaching",
     "以學生為中心，由提問出發，讓孩子在探究、合作與反思中學得深、學得廣。", "default", 3, 1),
    ("growth", "學生成長", "Student Growth",
     "品格為本、全人關顧，讓每個孩子都有發揮所長、服務他人的機會。", "char", 4, 1),
    ("stories", "成果與故事", "Achievements & Stories",
     "不只是獎項名單，更是孩子努力、嘗試和成長的故事。", "default", 5, 1),
    ("parents", "家長專區", "Parents",
     "小一入學、校曆、午膳、校車及家長常見問題，一頁找到。", "default", 6, 1),
    ("info", "學校資訊", "School Info",
     "學校計劃及報告、通告及表格、聯絡方法。", "default", 7, 1),
    ("en", "English", "English",
     "A Christian primary school in Kowloon City nurturing independent inquirers with AI literacy and children of complete character.", "default", 99, 0),
]

SECTIONS = {
"about": [
("vision", "辦學理念", "church", f"""
<p class="lead">本校由中華基督教會灣仔堂主辦，以《聖經》原則及基督教信念辦學，透過教育貫徹教會傳道服務的精神。</p>
<div class="grid grid-3">
  <div class="card"><h3>知識淵博</h3><p>建立穩固的語文及數理基礎，培養閱讀習慣，讓孩子終身熱愛學習。</p></div>
  <div class="card"><h3>善思明辨</h3><p>鼓勵提問、探究及反思，善用科技與AI，作出明智而合乎倫理的判斷。</p></div>
  <div class="card"><h3>堅毅前行</h3><p>在挑戰中學習堅持，以誠信、責任感及關愛之心面對生活。</p></div>
</div>
<div class="callout"><strong>校訓</strong><p>（請於後台填寫校訓及其釋義）</p></div>
"""),
("principal", "校長的話", "chat", f"""
<div class="media-split">
  {ph("校長近照（請上載）", "navy", "tall")}
  <div>
    <blockquote class="quote">教育不只是傳授知識，更是點燃孩子探究世界的好奇心；並以品格為根，讓他們在AI時代仍能誠信、善良、有承擔。</blockquote>
    <p>各位家長、同學：</p>
    <p>2026–2027 學年，學校踏入新的發展階段。我們訂下未來三年的兩項發展重點：</p>
    <ol>
      <li><strong>培養自主探究者，掌握AI新學力</strong> — 讓學生學會提出好問題、搜集及判斷資料，並負責任地運用AI工具解決真實問題。</li>
      <li><strong>培育完全品格，共建基小新里程</strong> — 以誠信、責任感及關愛為核心，透過「我是基道人」獎勵計劃、服務學習及家校合作，培育學生全人發展。</li>
    </ol>
    <p>期望與家長攜手，陪伴孩子成為自信、善良、有承擔的「基道人」。</p>
    <p><a class="link-more" href="/info#reports">下載校長的話（PDF）</a></p>
  </div>
</div>
<h3>校長短訊</h3>
<p>校長每月與家長分享學校發展的點滴。</p>
"""),
("history", "學校歷史", "book", """
<ol class="timeline">
  <li><span class="yr">（年份）</span>中華基督教會灣仔堂創辦本校。（請於後台補充）</li>
  <li><span class="yr">（年份）</span>遷入九龍城靠背壟道現址。（請於後台補充）</li>
  <li><span class="yr">2024</span>接受教育局校外評核。</li>
  <li><span class="yr">2026</span>新校長上任，制訂「2026–2029學校發展計劃」。</li>
  <li class="future"><span class="yr">2029</span>完成三年計劃，展現「基小新里程」成果。</li>
</ol>
"""),
("facilities", "校園設施", "school", f"""
<p>（請按學校實際設施更新以下內容及相片）</p>
<div class="grid grid-3">
  <div class="card">{ph("創科及AI學習室", "ai", "wide")}<h3 style="margin-top:14px">創科及AI學習室</h3><p>編程、機械人及AI專題研習的基地。</p></div>
  <div class="card">{ph("圖書館", "warm", "wide")}<h3 style="margin-top:14px">圖書館</h3><p>中英文圖書及電子書，推動從閱讀中學習。</p></div>
  <div class="card">{ph("禮堂", "navy", "wide")}<h3 style="margin-top:14px">禮堂</h3><p>早會、崇拜、表演及大型活動場地。</p></div>
  <div class="card">{ph("音樂室", "rose", "wide")}<h3 style="margin-top:14px">音樂室</h3><p>合唱、樂器班及音樂課堂。</p></div>
  <div class="card">{ph("視藝室", "warm", "wide")}<h3 style="margin-top:14px">視藝室</h3><p>結合傳統媒材與數碼創作。</p></div>
  <div class="card">{ph("學生輔導室", "char", "wide")}<h3 style="margin-top:14px">學生輔導室</h3><p>為學生提供安心傾訴及支援的空間。</p></div>
</div>
"""),
("teachers", "教師團隊", "users", """
<p>我們的老師專業、有愛心，並持續進修。新學年重點的教師專業發展包括：</p>
<ul class="check-list">
  <li>AI素養及電子教學工作坊，讓老師能設計以AI輔助的探究課堂</li>
  <li>共同備課及同儕觀課，聚焦「提問—探究—反思」課堂設計</li>
  <li>價值觀教育及正向管教培訓</li>
  <li>照顧學習多樣性及特殊教育需要專業培訓</li>
</ul>
<p>學校組織架構、行政成員及教職員編制，請參閱 <a href="/info#reports">學校資訊 › 計劃及報告</a>。</p>
"""),
],
"development": [
("plan", "2026–2029 發展計劃", "target", """
<p class="lead">學校以兩項關注事項為未來三年的發展方向，並每學期公布進程，讓家長清楚看見孩子的成長。</p>
<div class="grid grid-2">
  <div class="card" style="border-top:5px solid var(--c-ai)"><span class="tag tag-ai">關注事項一</span><h3 style="margin-top:10px">培養自主探究者，掌握AI新學力</h3><p>學生能主動提問、計劃及調整學習，並負責任地運用AI及數碼工具解決問題。</p><a class="link-more" href="#ai">了解詳情</a></div>
  <div class="card" style="border-top:5px solid var(--c-char)"><span class="tag tag-char">關注事項二</span><h3 style="margin-top:10px">培育完全品格，共建基小新里程</h3><p>學生在誠信、責任感及關愛中成長，樂於服務，成為僕人領袖。</p><a class="link-more" href="#character">了解詳情</a></div>
</div>
<h3>三年路線圖</h3>
"""),
("ai", "自主探究與AI新學力", "ai", f"""
<div class="media-split">
  <div>
    <p class="lead">AI時代最重要的能力，不是背答案，而是懂得提出好問題、判斷資訊，並創造解決方案。</p>
    <p>我們以「<strong>提問 → 探究 → 創造 → 反思</strong>」作為課堂主線，讓學生由小一開始逐步建立自主學習的習慣。</p>
  </div>
  {ph("學生於AI學習室進行專題研習", "ai", "wide")}
</div>
<h3>P1–P6 AI素養學習進程</h3>
<div class="table-wrap"><table>
  <thead><tr><th>級別</th><th>學習重點</th><th>學生表現例子</th></tr></thead>
  <tbody>
    <tr><td>P1–P2</td><td>認識AI在生活中的應用；不插電編程；資訊安全</td><td>分辨「人」與「機器」做的決定；用指令卡讓機械人走迷宮</td></tr>
    <tr><td>P3–P4</td><td>積木式編程；認識數據；善用搜尋及AI工具提問</td><td>設計互動故事；比較AI答案與書本資料的分別</td></tr>
    <tr><td>P5–P6</td><td>AI專題研習；簡單機器學習概念；AI倫理</td><td>以AI圖像辨識設計校園方案；討論AI的公平與私隱</td></tr>
  </tbody>
</table></div>
<div class="callout ai"><strong>負責任地使用AI</strong><p>學校訂立學生使用AI守則：誠實註明AI協助的部分、保護個人私隱、不以AI代替思考。家長可參閱「家長專區」的AI素養家長指南。</p></div>
<h3>例子：校園節能大使（P5 專題研習）</h3>
<div class="gpor">
  <div><span class="k">目標</span><p>運用數據及AI找出校園浪費能源的地方。</p></div>
  <div><span class="k">過程</span><p>學生收集各課室用電數據，以AI工具分析並提出方案。</p></div>
  <div><span class="k">成果</span><p>設計「離開課室關燈」智能提示裝置。</p></div>
  <div><span class="k">反思</span><p>「AI幫我們看數據，但方案要我們自己想。」</p></div>
</div>
"""),
("character", "完全品格教育", "heart", f"""
<div class="media-split rev">
  <div>
    <p class="lead">品格是孩子一生的根。我們以聖經價值為基礎，配合教育局十二個首要價值觀，聚焦<strong>誠信</strong>、<strong>責任感</strong>及<strong>關愛</strong>。</p>
    <ul class="check-list">
      <li><strong>「我是基道人」獎勵計劃</strong>：以具體行為指標鼓勵學生實踐良好品格</li>
      <li><strong>僕人領袖培訓</strong>：學生由服務身邊的人開始學習領導</li>
      <li><strong>全校服務學習</strong>：每級設有服務主題，走進社區關愛他人</li>
      <li><strong>家校同行</strong>：家長工作坊及親子品格任務</li>
    </ul>
  </div>
  {ph("「我是基道人」品格啟動禮", "char", "wide")}
</div>
<h3>「我是基道人」品格指標</h3>
<div class="grid grid-3">
  <div class="card"><span class="tag tag-char">誠信</span><p style="margin-top:8px">做錯事會承認及補救；完成功課不抄襲；誠實使用AI。</p></div>
  <div class="card"><span class="tag tag-char">責任感</span><p style="margin-top:8px">準時交功課；盡責擔任班務；愛護校園環境。</p></div>
  <div class="card"><span class="tag tag-char">關愛</span><p style="margin-top:8px">主動幫助同學；感恩父母師長；關心社區有需要的人。</p></div>
</div>
"""),
("leadership", "校長領導與學校革新", "compass", """
<p>新校長上任後，與全體老師共同檢視學校現況，推動以下革新：</p>
<div class="grid grid-2">
  <div class="card"><h3>課程更新</h3><p>重整各科課程，加入探究及AI元素，減少重複操練。</p></div>
  <div class="card"><h3>教師專業</h3><p>建立專業學習社群，定期共同備課及觀課。</p></div>
  <div class="card"><h3>數據為本</h3><p>以學生學習數據及持分者問卷檢視成效，持續改善。</p></div>
  <div class="card"><h3>家校溝通</h3><p>每月校長短訊、每學期公布三年計劃進程，讓家長看得見學校的發展。</p></div>
</div>
<h3>校長短訊及學校發展札記</h3>
"""),
],
"learning": [
("curriculum", "課程特色", "book", """
<p class="lead">課程以學生為中心，重視基礎、探究與應用並重。</p>
<div class="grid grid-3">
  <div class="card"><h3>探究式課堂</h3><p>每課由一個好問題開始，學生透過觀察、討論及實作建構知識。</p></div>
  <div class="card"><h3>從閱讀中學習</h3><p>早讀、主題閱讀及跨課程閱讀，培養閱讀習慣及能力。</p></div>
  <div class="card"><h3>照顧學習多樣性</h3><p>課堂分層任務、小組協作及延伸學習，讓每個孩子都有進步。</p></div>
</div>
"""),
("steam", "AI、STEAM 及數字教育", "flask", f"""
<div class="media-split">
  {ph("STEAM 課堂", "ai", "wide")}
  <div>
    <ul class="check-list">
      <li>P1–P6 縱向編程及AI素養課程</li>
      <li>STEAM 專題研習：結合科學、科技、工程、藝術及數學</li>
      <li>電子學習：課堂互動平台、網上預習及學習歷程檔案</li>
      <li>高年級自攜裝置（BYOD）學習（請按實際情況更新）</li>
      <li>創科校隊：機械人、編程及科創比賽</li>
    </ul>
    <p><a class="link-more" href="/development#ai">AI新學力發展重點</a></p>
  </div>
</div>
"""),
("languages", "語文教育", "globe", """
<div class="grid grid-2">
  <div class="card"><h3>中文及普通話</h3><p>重視閱讀及寫作；朗誦、說話訓練及中華文化活動，培養表達能力及文化素養。</p></div>
  <div class="card"><h3>English</h3><p>Phonics、閱讀計劃、English Day 及外籍英語教師協作教學，營造豐富的英語環境。</p></div>
</div>
"""),
("cross", "跨學科及體驗式學習", "compass", """
<p>每級設跨學科主題學習，並配合全方位學習日走出課室：</p>
<div class="table-wrap"><table>
  <thead><tr><th>級別</th><th>主題（示範）</th><th>體驗活動</th></tr></thead>
  <tbody>
    <tr><td>P1</td><td>我愛我的學校</td><td>校園尋寶、認識校園職工</td></tr>
    <tr><td>P2</td><td>健康生活</td><td>健康小廚師</td></tr>
    <tr><td>P3</td><td>我的社區</td><td>社區小記者</td></tr>
    <tr><td>P4</td><td>走進九龍城</td><td>社區探究日、文化導賞</td></tr>
    <tr><td>P5</td><td>校園可持續發展</td><td>AI節能專題</td></tr>
    <tr><td>P6</td><td>我的未來</td><td>畢業專題、職業探索</td></tr>
  </tbody>
</table></div>
"""),
("assessment", "評估與自主學習", "clipboard", """
<p>評估是為了促進學習。我們結合進展性評估及總結性評估，讓學生及家長清楚了解學習進度。</p>
<ul class="check-list">
  <li>課堂即時回饋及電子評估，及早發現學習難點</li>
  <li>學生自評、互評及學習反思</li>
  <li>專題研習及學習歷程檔案，記錄成長</li>
  <li>每學期考試／評估安排見 <a href="/parents#daily">校曆</a></li>
</ul>
"""),
],
"growth": [
("values", "價值觀與生命教育", "leaf", """
<p class="lead">以基督教信仰及教育局十二個首要價值觀（堅毅、尊重他人、責任感、國民身份認同、承擔精神、誠信、關愛、守法、同理心、勤勞、團結、孝親）為基礎，透過早會、崇拜、成長課及生活事件培育學生。</p>
<div class="grid grid-3">
  <div class="card"><h3>信仰培育</h3><p>早禱、崇拜、福音週及團契。</p></div>
  <div class="card"><h3>成長課</h3><p>情緒管理、人際相處及正向思維。</p></div>
  <div class="card"><h3>國民教育</h3><p>升旗禮、中華文化及國情認識活動。</p></div>
</div>
"""),
("support", "學生支援", "shield", """
<p>學校採用「全校參與」模式照顧學生的多樣性：</p>
<ul class="check-list">
  <li>學生支援小組：及早識別及支援有特殊教育需要的學生</li>
  <li>駐校社工及輔導服務：個人及小組輔導、家長諮詢</li>
  <li>教育心理學家及言語治療服務</li>
  <li>資優教育：校本拔尖課程及校外培訓</li>
  <li>非華語學生支援</li>
</ul>
<p>如有查詢，歡迎聯絡校務處轉介學生支援組。</p>
"""),
("leaders", "領袖及服務學習", "hand", f"""
<div class="media-split">
  <div>
    <p>我們相信真正的領袖是「僕人領袖」— 先服務、後領導。</p>
    <ul class="check-list">
      <li>風紀、班長、圖書館及科技大使</li>
      <li>學生會：學生參與校政、籌辦活動</li>
      <li>服務學習：探訪長者、社區清潔、義賣籌款</li>
      <li>領袖訓練營</li>
    </ul>
  </div>
  {ph("服務學習：探訪長者", "char", "wide")}
</div>
"""),
("eca", "體藝及課外活動", "palette", """
<p>推動「一生一體藝」，讓每位學生發掘興趣及潛能。</p>
<div class="grid grid-4">
  <div class="card"><h3>音樂</h3><p>合唱團、樂器班、手鐘隊</p></div>
  <div class="card"><h3>體育</h3><p>田徑、游泳、籃球、乒乓球</p></div>
  <div class="card"><h3>藝術</h3><p>視藝、舞蹈、戲劇、數碼創作</p></div>
  <div class="card"><h3>學術及創科</h3><p>奧數、編程、機械人、辯論</p></div>
</div>
<p style="margin-top:16px">（請按學校實際課外活動更新）</p>
"""),
],
"stories": [
("awards", "學生成就", "trophy", """
<p>按範疇及學年瀏覽學生成就。每項重點成果附有學生的努力故事。</p>
"""),
("works", "學生作品", "palette", "<p>學生在不同學科的優秀作品。</p>"),
("campus", "校園故事", "chat", "<p>每兩週一篇學生學習故事：記錄目標、過程、成果及學生反思。</p>"),
("media", "傳媒報導", "news", "<p>報章及媒體對本校的報導。</p>"),
("alumni", "畢業生與校友", "grad", """
<p>基道畢業生升讀不同中學，並在各自的領域發光發亮。歡迎校友與我們分享近況。</p>
"""),
],
"parents": [
("p1", "小一入學", "grad", """
<div class="callout warn"><strong>2027年9月小一入學</strong><p>請留意教育局「小一入學統籌辦法」的時間表，以及本校的簡介會及開放日安排。</p></div>
<ol class="steps">
  <li><span class="when">九月</span><strong>自行分配學位申請</strong>家長可向一所參加統籌辦法的官立或資助小學遞交申請。</li>
  <li><span class="when">十一月</span><strong>自行分配學位結果公布</strong>學校公布取錄名單；獲取錄的家長須按時辦理註冊。</li>
  <li><span class="when">一月</span><strong>統一派位選校</strong>未獲自行分配學位的家長填寫統一派位選擇表。</li>
  <li><span class="when">六月</span><strong>統一派位結果公布</strong>家長須按指定日期到獲派學校辦理註冊。</li>
</ol>
<p>確實日期以教育局公布為準。本校《自行分配學位計分準則》及學校簡介請參閱下方文件。</p>
<h3>幼小銜接</h3>
<ul class="check-list">
  <li>小一新生適應課程及暑期銜接活動</li>
  <li>小一家長工作坊：認識學習及生活轉變</li>
  <li>大哥哥大姐姐計劃：高年級學生協助新生適應</li>
</ul>
"""),
("transfer", "插班申請", "file", """
<p>如有學位空缺，學校會於本頁公布插班申請安排。家長可下載插班申請表，連同最近兩年成績表副本交回校務處。</p>
<p>查詢：請致電校務處（見 <a href="/info#contact">聯絡方法</a>）。</p>
"""),
("faq", "家長常見問題", "chat", "<p>如未能找到答案，歡迎聯絡校務處。</p>"),
("daily", "校曆、午膳及校車", "calendar", """
<div class="grid grid-2">
  <div class="card"><h3>午膳安排</h3><p>由學校委託之午膳供應商提供，每月經通告訂購。餐單及訂購表格可於「通告及表格」下載。</p></div>
  <div class="card"><h3>校車／保姆車</h3><p>由服務營辦商提供，路線及收費請參閱表格或聯絡校務處。</p></div>
</div>
<h3>即將舉行</h3>
"""),
("pta", "家教會及家長教育", "users", """
<p>家長教師會致力促進家校合作，定期舉辦親子活動及家長講座。</p>
<ul class="check-list">
  <li>家長講座：AI素養、正向管教、升中準備</li>
  <li>家長義工：協助圖書館、活動日及服務學習</li>
  <li>校長茶聚：與校長面對面交流</li>
</ul>
"""),
],
"info": [
("reports", "計劃及報告", "file", "<p>學校發展計劃、周年計劃、學校報告及校外評核報告。</p>"),
("notices", "通告及表格", "bell", "<p>最新家長通告及常用表格下載。</p>"),
("contact", "聯絡方法", "phone", ""),
],
"en": [
("about", "About Kei To", "church", """
<p>CCC Wanchai Church Kei To Primary School (Kowloon City) is a Christian aided primary school sponsored by the Church of Christ in China Wanchai Church. Guided by Biblical principles, we nurture children to be <strong>knowledgeable, discerning and persevering</strong>.</p>
"""),
("plan", "2026–2029 School Development Plan", "target", """
<div class="grid grid-2">
  <div class="card" style="border-top:5px solid var(--c-ai)"><h3>Independent Inquirers with AI Literacy</h3><p>Students learn to ask good questions, investigate, create and reflect, and use AI tools responsibly to solve real problems.</p></div>
  <div class="card" style="border-top:5px solid var(--c-char)"><h3>Complete Character</h3><p>Integrity, responsibility and care, nurtured through the "I am a Kei To Student" award scheme, servant leadership and service learning.</p></div>
</div>
"""),
("learning", "Learning & Growth", "book", """
<ul class="check-list">
  <li>Inquiry-based lessons: question → investigate → create → reflect</li>
  <li>P1–P6 coding and AI literacy curriculum, STEAM projects</li>
  <li>Reading across the curriculum; rich English environment with NET collaboration</li>
  <li>Whole-school approach to student support; "One Student, One Art &amp; Sport"</li>
</ul>
"""),
("admission", "P1 Admission", "grad", """
<p>Please refer to the Education Bureau's Primary One Admission System timetable. Our school briefing sessions and open day are announced on the <a href="/parents#p1">Parents page</a> (Chinese).</p>
"""),
("contact", "Contact", "phone", ""),
],
}

POSTS = [
    # type, date, tag, title, summary, featured, body
    ("news", "2026-11-14", "admin", "2027年9月小一自行分配學位結果公布安排",
     "結果將按教育局指定日期公布，獲取錄家長請留意註冊安排。", 1,
     "<p>本校將按教育局指定日期公布2027年9月小一自行分配學位取錄名單。獲取錄的家長請按通告指示辦理註冊手續。</p><p>未獲取錄的家長，可參與統一派位階段。如有查詢，請致電校務處。</p>"),
    ("news", "2026-11-05", "parent", "校長茶聚：與家長談2026–2029發展計劃",
     "校長與家長分享新三年發展重點，並解答家長提問。", 1,
     "<p>校長與四十多位家長分享「AI新學力」及「完全品格」兩項發展重點，並即場解答家長對AI學習及品格教育的提問。（示範內容）</p>"),
    ("news", "2026-10-20", "ai", "AI素養家長工作坊：與孩子一起善用AI",
     "認識AI工具的好處與風險，學習在家陪伴孩子負責任地使用AI。", 0,
     "<p>工作坊介紹學校的學生使用AI守則，並示範如何與孩子一起討論AI的答案是否可信。（示範內容）</p>"),
    ("joy", "2026-11-08", "ai", "創科隊於全港小學AI創意編程比賽奪金",
     "P5 同學以「校園節能小幫手」作品獲評審讚賞。", 1,
     "<p>三位五年級同學以AI圖像辨識設計「校園節能小幫手」，在比賽中奪得金獎。（示範內容）</p>"),
    ("joy", "2026-10-28", "arts", "合唱團於音樂比賽獲優異獎",
     "團員每週練習，以和諧歌聲贏得評判肯定。", 0,
     "<p>合唱團同學在比賽中展現默契及自信。（示範內容）</p>"),
    ("joy", "2026-10-15", "sport", "田徑隊於分區小學田徑比賽獲團體殿軍",
     "多位隊員刷新個人最佳成績。", 0,
     "<p>田徑隊同學努力不懈，奪得男子甲組團體殿軍。（示範內容）</p>"),
    ("activity", "2026-11-10", "academic", "P4 社區探究日：走進九龍城",
     "學生化身小記者，訪問街坊、記錄社區故事。", 1,
     """<div class="gpor"><div><span class="k">目標</span><p>認識社區文化及歷史。</p></div><div><span class="k">過程</span><p>分組訪問街坊、拍攝及記錄。</p></div><div><span class="k">成果</span><p>製作社區故事電子書。</p></div><div><span class="k">反思</span><p>「原來九龍城有這麼多故事！」</p></div></div><p>（示範內容）</p>"""),
    ("activity", "2026-10-30", "char", "「我是基道人」品格啟動禮",
     "全校師生一同承諾實踐誠信、責任感及關愛。", 0,
     "<p>啟動禮上，各級代表分享品格承諾，並展示班級品格目標。（示範內容）</p>"),
    ("activity", "2026-09-25", "service", "中秋關愛行動：學生探訪長者",
     "高年級學生親手製作燈籠送贈社區長者。", 0,
     "<p>服務生與長者一同猜燈謎、分享月餅，實踐關愛。（示範內容）</p>"),
    ("story", "2026-11-01", "ai", "一個問題的旅程：P5 同學如何用AI設計校園節能方案",
     "由「為甚麼課室總是開着燈？」開始的一次探究。", 1,
     """<p>一切由一位同學的提問開始：「為甚麼小息時課室總是開着燈？」</p><div class="gpor"><div><span class="k">目標</span><p>找出浪費能源的原因。</p></div><div><span class="k">過程</span><p>記錄用電數據，用AI工具找規律。</p></div><div><span class="k">成果</span><p>設計智能提示裝置，於全校試行。</p></div><div><span class="k">反思</span><p>「AI幫我們看數據，但方案要我們自己想。」</p></div></div><p>（示範內容）</p>"""),
    ("story", "2026-10-12", "char", "從「我做錯了」到「我會補救」：一個誠信小故事",
     "一位三年級同學勇於承認錯誤的故事。", 0,
     "<p>同學不小心弄壞了同學的文具，主動承認並用零用錢補償。班主任在班上分享這個故事，全班一同學習誠信。（示範內容）</p>"),
    ("work", "2026-10-25", "academic", "P3 中文科：我的社區小記者",
     "學生以訪問稿形式介紹社區人物。", 0, "<p>（請上載學生作品相片）</p>"),
    ("work", "2026-10-18", "arts", "P6 視藝科：AI輔助設計的環保海報",
     "學生先手繪草圖，再以AI工具探索配色，最後親手完成作品。", 0, "<p>（請上載學生作品相片）</p>"),
    ("media", "2025-06-01", "char", "星島教育：品格學業並重　成就每一個孩子",
     "報導本校品格及學業並重的辦學方向。（日期請核實）", 0,
     '<p><a href="https://www.stheadline.com/local-school/3304700/中華基督教會灣仔堂基道小學-品格學業並重-成就每一個孩子" target="_blank">閱讀原文（星島頭條）</a></p>'),
    ("media", "2025-07-01", "academic", "星島教育：重視幼小銜接　多元措施有助小學生開開心心上小一",
     "介紹本校幼小銜接措施。（日期請核實）", 0,
     '<p><a href="https://www.stheadline.com/local-school/3346964/中華基督教會灣仔堂基道小學-重視幼小銜接多元措施有助小學生開開心心上小一" target="_blank">閱讀原文（星島頭條）</a></p>'),
    ("media", "2026-03-01", "char", "星島教育：以愛為本　塑造未來僕人領袖「我是基道人」獎勵計劃",
     "介紹「我是基道人」獎勵計劃及僕人領袖培育。（日期請核實）", 0,
     '<p><a href="https://www.stheadline.com/ad-edu/3503173/中華基督教會灣仔堂基道小學-以愛為本-塑造未來僕人領袖-我是基道人獎勵計劃" target="_blank">閱讀原文（星島頭條）</a></p>'),
    ("media", "2026-04-01", "service", "星島教育：傳播愛　實踐愛　學生以愛與平安回饋社會",
     "報導學生服務社區的經歷。（日期請核實）", 0,
     '<p><a href="https://www.stheadline.com/ad-edu/3529095/傳播愛-實踐愛-中華基督教會灣仔堂基道小學學生以愛與平安回饋社會" target="_blank">閱讀原文（星島頭條）</a></p>'),
    ("message", "2026-11-01", "", "校長短訊（十一月）：讓提問成為習慣",
     "孩子問「為甚麼」的時候，正是學習最好的開始。", 0,
     "<p>親愛的家長：當孩子問「為甚麼」，請先別急着給答案，試試反問：「你覺得呢？我們可以怎樣找答案？」這正是我們在課堂推動的探究精神。（示範內容）</p>"),
    ("message", "2026-09-01", "", "開學寄語：一起開展基小新里程",
     "新學年，新開始，與家長攜手同行。", 0,
     "<p>歡迎各位同學回校！新學年，學校以「AI新學力」及「完全品格」為發展重點……（示範內容）</p>"),
]

AWARDS = [
    # school_year, date, category, competition, result, students, story, featured
    ("2026-27", "2026-11-08", "academic", "全港小學AI創意編程比賽", "金獎", "5A 陳同學、5B 李同學、5C 黃同學",
     "三位同學由一個生活提問出發，用了六星期反覆測試AI模型，最終設計出「校園節能小幫手」。", 1),
    ("2026-27", "2026-10-22", "academic", "全港小學數學比賽（初賽）", "一等獎", "6A 何同學", "", 0),
    ("2026-27", "2026-10-15", "arts", "九龍城區小學分區田徑比賽", "男子甲組團體殿軍", "田徑隊",
     "隊員每週三天晨操，在比賽中互相打氣，多人刷新個人最佳成績。", 1),
    ("2026-27", "2026-10-28", "arts", "校際音樂比賽 合唱", "優異獎", "合唱團", "", 0),
    ("2026-27", "2026-10-05", "service", "地區傑出服務學生獎", "傑出學生獎", "6B 張同學",
     "張同學擔任圖書館大使三年，每週為低年級同學講故事，並帶領同學探訪長者。", 1),
    ("2025-26", "2026-06-20", "academic", "香港學校朗誦節 粵語詩詞獨誦", "冠軍", "3A 林同學", "", 0),
    ("2025-26", "2026-05-15", "academic", "全港小學STEAM創科挑戰賽", "一等獎", "創科隊（P5–P6）", "", 0),
    ("2025-26", "2026-04-18", "arts", "學校舞蹈節 中國舞", "甲級獎", "中國舞組", "", 0),
    ("2025-26", "2026-03-12", "arts", "全港青少年繪畫比賽", "優異獎", "4B 吳同學", "", 0),
    ("2025-26", "2026-02-25", "service", "「好人好事」嘉許計劃", "嘉許狀", "五年級服務團隊", "", 0),
    ("2025-26", "2026-01-10", "academic", "英文話劇比賽", "傑出劇本獎", "English Drama Club", "", 0),
    ("2025-26", "2025-12-06", "arts", "分區小學游泳比賽 女子乙組50米自由泳", "亞軍", "4A 鄭同學", "", 0),
]

EVENTS = [
    ("2026-11-21", "", "開放日暨小一入學簡介會", "歡迎準小一家長及幼稚園學生參加", "admission"),
    ("2026-11-27", "", "家長日（P1–P6）", "與班主任面談，了解學生學習進度", "parent"),
    ("2026-12-04", "2026-12-10", "第一次考試（P3–P6）", "考試時間表見家長通告", "exam"),
    ("2026-12-18", "", "聖誕崇拜及班際聯歡", "", "event"),
    ("2026-12-21", "2027-01-01", "聖誕及新年假期", "", "holiday"),
    ("2027-01-15", "", "AI創科展", "學生展示AI專題研習成果，歡迎家長參觀", "event"),
    ("2027-02-05", "2027-02-13", "農曆新年假期", "", "holiday"),
    ("2027-03-05", "", "陸運會", "", "event"),
]

DOCUMENTS = [
    ("plan", "2026–2029 學校發展計劃", "2026-10-31", "", ""),
    ("plan", "2026–2027 學校周年計劃", "2026-10-31", "", ""),
    ("plan", "2025–2026 學校報告", "2026-10-31", "", ""),
    ("plan", "校長的話（2026–2027）", "2026-09-01", "", ""),
    ("plan", "校外評核報告（2024）", "2024-12-31",
     "", "https://www.edb.gov.hk/attachment/tc/sch-admin/sch-quality-assurance/reports/esr-report/2024/The%20Church%20of%20Christ%20in%20China%20Wanchai%20Church%20Kei%20To%20Primary%20School%20(Kowloon%20City)_tc.pdf"),
    ("plan", "學校組織架構、行政成員及教職員編制", "2026-09-01", "", ""),
    ("notice", "家長日安排", "2026-11-10", "", ""),
    ("notice", "第一次考試時間表", "2026-11-12", "", ""),
    ("form", "午膳訂購表格（十二月）", "2026-11-12", "", ""),
    ("form", "校車服務申請表", "2026-09-01", "", ""),
    ("form", "學生請假申請表", "2026-09-01", "", ""),
    ("form", "插班申請表", "2026-09-01", "", ""),
    ("p1", "2027年9月小一自行分配學位計分準則", "2026-09-01", "", ""),
    ("p1", "學校簡介小冊子", "2026-09-01", "", ""),
]

FAQS = [
    ("p1", "小一入學有沒有面試或筆試？",
     "<p>按教育局「小一入學統籌辦法」，學校於收生時不會為兒童舉行任何形式的筆試或面試。自行分配學位按學校公布的計分準則處理。</p>"),
    ("p1", "本校屬於哪一個小一學校網？",
     "<p>本校位於九龍城區。所屬學校網請參閱教育局《小學概覽》或致電校務處查詢。（請於後台填寫校網編號）</p>"),
    ("p1", "學校如何幫助小一新生適應？",
     "<p>學校設有小一適應課程、暑期銜接活動、小一家長工作坊及「大哥哥大姐姐」計劃，協助孩子由幼稚園順利過渡至小學。</p>"),
    ("daily", "上學及放學時間是怎樣的？",
     "<p>本校為全日制小學。上學及放學時間請參閱最新《家長手冊》或家長通告。（請於後台填寫）</p>"),
    ("daily", "學校有午膳及校車服務嗎？",
     "<p>有。午膳由學校委託之供應商提供，每月經通告訂購；校車／保姆車由服務營辦商提供。表格可於「學校資訊 › 通告及表格」下載。</p>"),
    ("learning", "學校如何教授AI？會否讓孩子過度依賴AI？",
     "<p>學校按年級循序漸進地教授AI素養，並訂立學生使用AI守則，強調「AI是助手，不是代替思考」。低年級以不插電活動為主，高年級才在老師指導下使用AI工具。</p>"),
    ("learning", "功課量如何？",
     "<p>學校按教育局指引訂立家課政策，重視質素多於數量，並安排課後功課輔導。</p>"),
    ("support", "如孩子有特殊學習需要，學校如何支援？",
     "<p>學校以「全校參與」模式支援學生，設有學生支援小組、駐校社工、教育心理學家及言語治療服務。家長可聯絡班主任或校務處轉介。</p>"),
    ("general", "家長如何與老師聯絡？",
     "<p>家長可透過學生手冊、學校流動應用程式或致電校務處與老師聯絡。</p>"),
]

VOICES = [
    ("parent", "陳太（二年級家長）", "孩子回家會主動問「為甚麼」，還會教我怎樣用平板查資料，看到他對學習越來越有興趣。（示範）"),
    ("parent", "李先生（五年級家長）", "學校的品格計劃很具體，孩子會記錄自己每週幫助別人的事，我們一家也一起參與。（示範）"),
    ("student", "六年級 黃同學", "做AI專題時我們失敗了很多次，但老師說失敗也是學習，最後我們成功了！（示範）"),
    ("alumni", "2020年畢業生 何同學", "在基道學到的服務精神，讓我升中後也繼續當義工。（示範）"),
]

HIGHLIGHTS = [
    ("自主探究 × AI新學力", "由P1開始建立提問、探究及反思的習慣；P1–P6縱向AI素養課程。", "ai", "ai", "/development#ai"),
    ("完全品格教育", "「我是基道人」獎勵計劃，聚焦誠信、責任感及關愛。", "heart", "char", "/development#character"),
    ("兩文三語　從閱讀中學習", "重視語文基礎，豐富的閱讀及英語環境。", "globe", "primary", "/learning#languages"),
    ("一生一體藝", "音樂、體育、藝術及創科，讓每位孩子發揮所長。", "palette", "rose", "/growth#eca"),
    ("全人關顧", "全校參與照顧學生多樣性，駐校社工及專業團隊支援。", "shield", "accent", "/growth#support"),
    ("家校同行", "校長茶聚、家長工作坊、每學期公布發展進程。", "users", "primary", "/parents#pta"),
]

# 區塊附加的動態內容
SECTION_WIDGETS = {
    ("about", "principal"): "posts:message",
    ("development", "plan"): "plan_roadmap",
    ("development", "leadership"): "posts:message",
    ("stories", "awards"): "awards",
    ("stories", "works"): "posts:work",
    ("stories", "campus"): "posts:story",
    ("stories", "media"): "posts:media",
    ("stories", "alumni"): "voices:alumni",
    ("parents", "p1"): "docs:p1",
    ("parents", "faq"): "faq",
    ("parents", "daily"): "events",
    ("info", "reports"): "docs:plan",
    ("info", "notices"): "docs:notice+form",
    ("info", "contact"): "contact",
    ("en", "contact"): "contact",
}


def seed(conn):
    ts = now_str()
    by = "system"
    for k, v in SETTINGS.items():
        conn.execute("INSERT OR IGNORE INTO settings(key, value) VALUES(?, ?)", (k, v))
    for slug, title, title_en, intro, style, sort, in_nav in PAGES:
        cur = conn.execute(
            "INSERT INTO pages(slug,title,title_en,intro,style,sort,in_nav,updated_at,updated_by) VALUES(?,?,?,?,?,?,?,?,?)",
            (slug, title, title_en, intro, style, sort, in_nav, ts, by))
        page_id = cur.lastrowid
        for i, (anchor, stitle, ic, body) in enumerate(SECTIONS.get(slug, []), start=1):
            conn.execute(
                "INSERT INTO sections(page_id,anchor,title,icon,body,widget,sort,visible,updated_at,updated_by) VALUES(?,?,?,?,?,?,?,1,?,?)",
                (page_id, anchor, stitle, ic, body.strip(), SECTION_WIDGETS.get((slug, anchor), ""), i * 10, ts, by))
    for t, d, tag, title, summary, featured, body in POSTS:
        conn.execute(
            "INSERT INTO posts(type,date,tag,title,summary,body,featured,published,created_at,updated_at,updated_by) VALUES(?,?,?,?,?,?,?,1,?,?,?)",
            (t, d, tag, title, summary, body, featured, ts, ts, by))
    for sy, d, cat, comp, res, stu, story, featured in AWARDS:
        conn.execute(
            "INSERT INTO awards(school_year,date,category,competition,result,students,story,featured,published,created_at,updated_at,updated_by) VALUES(?,?,?,?,?,?,?,?,1,?,?,?)",
            (sy, d, cat, comp, res, stu, story, featured, ts, ts, by))
    for d, e, title, note, kind in EVENTS:
        conn.execute(
            "INSERT INTO events(date,end_date,title,note,kind,published,created_at,updated_at,updated_by) VALUES(?,?,?,?,?,1,?,?,?)",
            (d, e, title, note, kind, ts, ts, by))
    for cat, title, d, f, url in DOCUMENTS:
        conn.execute(
            "INSERT INTO documents(category,title,date,file,url,published,created_at,updated_at,updated_by) VALUES(?,?,?,?,?,1,?,?,?)",
            (cat, title, d, f, url, ts, ts, by))
    for i, (grp, q, a) in enumerate(FAQS, start=1):
        conn.execute(
            "INSERT INTO faqs(grp,question,answer,sort,published,created_at,updated_at,updated_by) VALUES(?,?,?,?,1,?,?,?)",
            (grp, q, a, i * 10, ts, ts, by))
    for i, (role, name, quote) in enumerate(VOICES, start=1):
        conn.execute(
            "INSERT INTO voices(role,name,quote,sort,published,created_at,updated_at,updated_by) VALUES(?,?,?,?,1,?,?,?)",
            (role, name, quote, i * 10, ts, ts, by))
    for i, (title, text, ic, color, link) in enumerate(HIGHLIGHTS, start=1):
        conn.execute(
            "INSERT INTO highlights(title,text,icon,color,link,sort,published,created_at,updated_at,updated_by) VALUES(?,?,?,?,?,?,1,?,?,?)",
            (title, text, ic, color, link, i * 10, ts, ts, by))
    conn.commit()
