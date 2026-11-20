import html
import json
import os
import random
import re
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import datetime
from html.parser import HTMLParser
from zoneinfo import ZoneInfo

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["CHAT_ID"]

LAT = "36.5486"
LON = "7.2286"
CITY_NAME = "الركنية، قالمة - الجزائر"

MAIN_INTERVAL = 90 * 60
RIDDLE_DELAY = 20 * 60

STATE_FILE = "state.json"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

NEWS_TOPICS = [
    ("⚡️ أمن سيبراني", "أخبار الأمن السيبراني اختراق ثغرات"),
    ("🤖 ذكاء اصطناعي", "أخبار الذكاء الاصطناعي نماذج جديدة"),
    ("⚡️ تقنية وألعاب", "تقنية هواتف تطبيقات ألعاب إلكترونية"),
    ("📰 أخبار الجزائر", "أخبار الجزائر اليوم"),
    ("⚡️ أمن سيبراني", "أخبار تسريب بيانات برمجيات خبيثة"),
    ("🌱 أخبار إيجابية", "أخبار إيجابية وقصص نجاح"),
]


def news_url(query):
    return (
        "https://news.google.com/rss/search?q=" + urllib.parse.quote(query)
        + "&hl=ar&gl=DZ&ceid=DZ:ar"
    )

ARABIC_TIPS = [
    "اشرب كوب ماء بعد الاستيقاظ مباشرة؛ جسدك كان بلا ترطيب طوال الليل.",
    "ابدأ يومك بأهم مهمة لديك قبل فتح الجوال ورسائل العمل.",
    "المشي نصف ساعة يومياً يحسّن القلب والمزاج ويخفض التوتر.",
    "النوم من 7 إلى 8 ساعات بمواعيد ثابتة يقوي الذاكرة والمناعة.",
    "وجبة الإفطار المتوازنة تمنحك طاقة الصباح وتركيزاً أطول.",
    "قلل السكر والمشروبات الغازية وستلاحظ فرقاً في نشاطك ووزنك.",
    "خصص وقتاً يومياً للقراءة ولو 20 دقيقة؛ فوائدها تتراكم مع الوقت.",
    "اجلس بوضعية سليمة ولا تطأطئ رأسك طويلاً للهاتف.",
    "قبل النوم، أطفئ الشاشات بساعة لتنام أعمق وأهدأ.",
    "تنفس بعمق عشر مرات عند التوتر؛ يهدئ جهازك العصبي فوراً.",
    "نظم مالك: سجل مصاريفك الأسبوعية وستكتشف أين تذهب الأموال.",
    "ادخر ولو مبلغاً صغيراً شهرياً؛ الاستمرار أهم من المقدار.",
    "حافظ على صلواتك؛ السكينة تبدأ من اتصالك بخالقك.",
    "احفظ ولو آيات قليلة أسبوعياً من القرآن، فالبركة في المواظبة.",
    "صاحب أهل الخير والأخلاق؛ فصحبتك من أعظم ما يكسبك.",
    "أنصت أكثر مما تتكلم؛ فالإنسان الذي يصغي تُفتح له القلوب.",
    "لا تؤجل عمل اليوم إلى الغد؛ اجعل مبدأك التنفيذ الفوري.",
    "خصص وقتاً للعائلة يومياً بعيداً عن الشاشات.",
    "أشكر الله على نعمك صباح مساء؛ الشكر يزيد النعم.",
    "ابدأ مشاريعك الصغيرة بدل تأجيلها؛ الخبرة من التجربة لا من التردد.",
    "اكتب أهدافك على ورقة؛ الأهداف المكتوبة تتحقق أكثر من المنسية.",
    "تعلم مهارة رقمية واحدة هذا الشهر؛ تفتح لك فرص عمل جديدة.",
    "ابتسم؛ فالابتسامة صدقة وتخفف هموم يومك.",
    "قلل من مقارنة نفسك بالآخرين؛ قارن نفسك بنسختك السابقة فقط.",
    "نظم منزلك ومكتبك؛ الفوضى الخارجية تخلق فوضى داخلية.",
    "اشرب الشاي أو القهوة باعتدال ولا تتجاوز فنجانين صباحاً.",
    "أعطِ جسمك يوماً من الراحة من الرياضة أسبوعياً كي يتعافى.",
    "استخدم السلالم بدل المصعد كلما سنحت الفرصة.",
    "حافظ على وقتك ولا تسرفه في مواقع التواصل بلا فائدة.",
    "نظم نومك مع الفجر؛ القيام المبكر يبارك في وقتك.",
    "استشر من يقول لك الحقيقة لا من يجامل؛ النصيحة الصادقة كنز.",
    "زر والديك وأرحهما بكلمة طيبة؛ فالبر خير ربح في الدنيا.",
    "تجنب الجدال العقيم، ولا تجعل آخر كلامك خطأ.",
    "خطط ليومك في الليلة السابقة؛ وفر وقت القرارات صباحاً.",
    "اقرأ في السيرة والتاريخ؛ فالعبرة بهم خير معلم.",
    "استغفر كثيراً؛ يريح النفس ويوسع الرزق.",
    "ارتقِ بالرد الجميل حتى لمن أساء؛ فالعفو زينة.",
    "حافظ على صحة أسنانك: نظفها مرتين يومياً وزر الطبيب كل ستة أشهر.",
    "تعرض للشمس ربع ساعة صباحاً لامتصاص فيتامين د.",
    "احمل معك زجاجة ماء دائماً وتذكر أن تشرب كل ساعة.",
    "تعلم أن تقول لا بلطف؛ لا تكن جسراً لكل من يريد العبور.",
    "حسنات اليوم الصغيرة تتراكم لتصبح إنجازات كبيرة.",
    "اعتزل الراحة الزائدة؛ فالخمول يفسد الجسم والعقل.",
    "احفظ أرقام الطوارئ والمستشفيات القريبة في هاتفك.",
    "خطة أسبوعية بسيطة تكفيك فوضى الأشهر؛ نظم أولوياتك.",
    "لا تستهن بالكلمة الطيبة؛ فقد تكون سبب هداية شخص.",
    "جدد نيتك في كل عمل تعمله، فالأعمال بالنيات.",
    "خذ نفساً قبل الغضب؛ فالغضب قرار متسرع تندم عليه.",
]

ARABIC_RIDDLES = [
    ("ما هو الشيء الذي يكتب ولا يقرأ؟", "القلم ✍️"),
    ("شيء كلما أخذت منه كبر، فما هو؟", "الحفرة 🕳️"),
    ("ما هو الشيء الذي له أسنان ولا يعض؟", "المشط 🪮"),
    ("ما هو الشيء الذي يمشي ولا أرجل له؟", "السحاب ☁️"),
    ("ما هو الشيء الذي يسمع بلا أذن ويتكلم بلا لسان؟", "الهاتف 📞"),
    ("ما هو الشيء الذي يمر من الزجاج ولا يكسره؟", "الضوء 💡"),
    ("ما هو الشيء الذي كلما زاد نقص؟", "العمر ⏳"),
    ("ما هو الشيء الذي له عين واحدة ولا يرى؟", "الإبرة 🪡"),
    ("ما هو البيت الذي لا أبواب له ولا نوافذ؟", "بيت الشعر 🏛️"),
    ("ما هو الشيء الذي لا يمشي إلا بالضرب؟", "المسمار 🔨"),
    ("ما هو الشيء الموجود في كل مكان ولا تراه؟", "الهواء 🌬️"),
    ("شيء له رقبة ولا رأس، ما هو؟", "الزجاجة 🍾"),
    ("ما هو الشيء الذي يعبر البحر ولا يبتل؟", "الطريق/السفينة ⛵"),
    ("ما هو الشيء الذي يتحرك أمامك دائماً ولا تسبقه؟", "الظل 🌓"),
    ("ما هو الشيء الذي يتكلم جميع لغات العالم؟", "صدى الصوت 📢"),
    ("شيء كلما مشى زادت أرجله، ما هو؟", "المشط عند شيب.. الأمشاط في المزرعة؟ 😅"),
]

FALLBACK_NEWS = [
    "الجزائر تحتضن فعاليات ثقافية وفنية متنوعة تعكس غنى التراث الوطني.",
    "الأسواق العالمية تشهد تحولات في أسعار الطاقة تهم الدول المنتجة للنفط.",
    "تقنيات الذكاء الاصطناعي تتوسع في التعليم والصحة والصناعة عالمياً.",
    "الدول العربية تطلق مبادرات للطاقة المتجددة ضمن استراتيجيات التنمية.",
    "فرق كرة القدم العربية تستعد لمنافسات قارية جديدة.",
]


def urlopen_retry(req, timeout=30, attempts=4):
    """urlopen with backoff on 429/5xx: GitHub runner IPs get rate-limited
    by the weather/news providers, and one 429 must not kill the tick."""
    delay = 10
    for i in range(attempts):
        try:
            return urllib.request.urlopen(req, timeout=timeout)
        except Exception:
            if i == attempts - 1:
                raise
            time.sleep(delay)
            delay = min(delay * 2, 60)


def http_get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urlopen_retry(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_weather():
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,pressure_msl,uv_index"
        f"&daily=sunrise,sunset&timezone=auto"
    )
    d = http_get(url)
    cur = d["current"]
    code = cur.get("weather_code", 0)
    wmo = {
        0: "سماء صافية ☀️", 1: "صافي غالباً 🌤️", 2: "غائم جزئياً ⛅", 3: "غائم ☁️",
        45: "ضباب 🌫️", 48: "ضباب متجمد 🌫️",
        51: "رذاذ خفيف 🌦️", 53: "رذاذ 🌦️", 55: "رذاذ كثيف 🌧️",
        61: "مطر خفيف 🌦️", 63: "مطر 🌧️", 65: "مطر غزير 🌧️",
        80: "زخات مطر 🌦️", 81: "زخات مطر 🌧️", 82: "زخات رعدية ⛈️",
        71: "ثلج خفيف ❄️", 73: "ثلج ❄️", 75: "ثلج كثيف ❄️",
        95: "عاصفة رعدية ⛈️", 96: "عاصفة مع برد ⛈️", 99: "عاصفة شديدة ⛈️",
    }
    desc = wmo.get(code, f"كود {code}")
    wind_dir = cur.get("wind_direction_10m", 0)
    dirs = ["شمال", "شمال شرق", "شرق", "جنوب شرق", "جنوب", "جنوب غرب", "غرب", "شمال غرب"]
    wind_name = dirs[round(wind_dir % 360 / 45) % 8]
    return {
        "temp": cur["temperature_2m"],
        "feels": cur["apparent_temperature"],
        "humidity": cur["relative_humidity_2m"],
        "desc": desc,
        "wind": cur["wind_speed_10m"],
        "wind_dir": wind_name,
        "pressure": cur["pressure_msl"],
        "uv": cur.get("uv_index", "-"),
        "sunrise": d["daily"]["sunrise"][0].split("T")[1],
        "sunset": d["daily"]["sunset"][0].split("T")[1],
    }


def get_advice(state):
    used = set(state.get("used_advice", []))
    fresh = [t for t in ARABIC_TIPS if t not in used]
    pool = fresh or ARABIC_TIPS
    tip = random.choice(pool)
    used_list = state.get("used_advice", [])
    used_list.insert(0, tip)
    state["used_advice"] = used_list[:45]
    return tip


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paras = []
        self._cur = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip += 1
        if tag == "p":
            self._cur = []

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self._skip:
            self._skip -= 1
        if tag == "p":
            txt = " ".join("".join(self._cur).split())
            if len(txt) >= 60:
                self.paras.append(txt)
            self._cur = []

    def handle_data(self, data):
        if not self._skip:
            self._cur.append(data)


BOILERPLATE_MARKERS = (
    "انضم إلى", "انضم الى", "اشترك", "النشرة البريدية", "تابعنا",
    "جميع الحقوق", "حقوق النشر", "ملفات تعريف الارتباط", "سياسة الخصوصية",
    "subscribe", "newsletter", "sign up", "sign-up", "cookies",
    "all rights reserved", "follow us", "©",
)


def clean_paras(paras):
    """Drop site boilerplate (newsletter boxes, footers, cookie notices)
    so the excerpt is the article's own text, not the page furniture."""
    return [t for t in paras
            if not any(m in t.lower() for m in BOILERPLATE_MARKERS)]


def fetch_article(link):
    """Return (paragraphs, image_url) from the article page; ([], "") on failure."""
    req = urllib.request.Request(link, headers=HEADERS)
    with urlopen_retry(req, timeout=25) as resp:
        raw = resp.read()
        final_url = resp.geturl()
    try:
        html_str = raw.decode("utf-8")
    except UnicodeDecodeError:
        html_str = raw.decode("iso-8859-6", errors="replace")
    image = ""
    for pat in (
        r'<meta[^>]+property=["\']og:image["\'][^>]*content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']',
        r'<meta[^>]+name=["\']twitter:image["\'][^>]*content=["\']([^"\']+)',
    ):
        m = re.search(pat, html_str, re.IGNORECASE)
        if m:
            image = urllib.parse.urljoin(final_url, html.unescape(m.group(1).strip()))
            break
    p = TextExtractor()
    p.feed(html_str)
    return clean_paras(p.paras)[:4], image

def normalize_title(t):
    t = t or ""
    t = re.sub(r"[\u064B-\u0652\u0640]", "", t)
    t = (t.replace("\u0623", "\u0627").replace("\u0625", "\u0627")
          .replace("\u0622", "\u0627").replace("\u0624", "\u0648")
          .replace("\u0626", "\u064a").replace("\u0629", "\u0647")
          .replace("\u0649", "\u064a"))
    t = re.sub(r"[^\w\s]", " ", t)
    return " ".join(t.lower().split())


def title_similar(a, b):
    sa, sb = set(a.split()), set(b.split())
    if not sa or not sb:
        return False
    return len(sa & sb) / len(sa | sb) >= 0.55


def fetch_feed_items(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urlopen_retry(req, timeout=25) as resp:
        data = resp.read()
    root = ET.fromstring(data)
    items = []
    seen_keys = set()
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        source = (item.findtext("source") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not title:
            continue
        for sep in (" - " + source, " -" + source):
            if title.endswith(sep):
                title = title[: -len(sep)].strip()
                break
        key = normalize_title(title)
        if not key or key in seen_keys:
            continue
        seen_keys.add(key)
        items.append({"title": title, "source": source, "link": link, "key": key})
    return items


def get_news(state):
    """Pick one fresh story, rotating across NEWS_TOPICS so the feed is not
    all crime: start at the saved topic index, walk forward until a topic
    has a genuinely new item, and advance the index past the topic used."""
    used = [normalize_title(u) for u in state.get("used_news", [])]
    used_set = set(used)
    try:
        start = int(state.get("news_topic_idx", 0)) % len(NEWS_TOPICS)
    except Exception:
        start = 0
    for off in range(len(NEWS_TOPICS)):
        ti = (start + off) % len(NEWS_TOPICS)
        label, query = NEWS_TOPICS[ti]
        try:
            items = fetch_feed_items(news_url(query))
        except Exception:
            continue
        fresh = [it for it in items
                 if it["key"] not in used_set
                 and not any(title_similar(it["key"], u) for u in used)]
        if not fresh:
            continue
        chosen = random.choice(fresh)
        chosen["topic"] = label
        used.insert(0, chosen["key"])
        state["used_news"] = used[:400]
        state["news_topic_idx"] = (ti + 1) % len(NEWS_TOPICS)
        return chosen
    return None

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode()
    req = urllib.request.Request(url, data=data, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_photo(photo_url, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    data = urllib.parse.urlencode({
        "chat_id": TELEGRAM_CHAT_ID,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "HTML",
    }).encode()
    req = urllib.request.Request(url, data=data, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_photo_upload(img_bytes, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    boundary = "----dailybot" + str(int(time.time() * 1000))
    body = b""
    for name, value in (("chat_id", TELEGRAM_CHAT_ID),
                        ("caption", caption), ("parse_mode", "HTML")):
        body += (f"--{boundary}\r\nContent-Disposition: form-data; "
                 f"name=\"{name}\"\r\n\r\n{value}\r\n").encode("utf-8")
    body += (f"--{boundary}\r\nContent-Disposition: form-data; "
             f"name=\"photo\"; filename=\"news.jpg\"\r\n"
             f"Content-Type: image/jpeg\r\n\r\n").encode("utf-8")
    body += img_bytes + b"\r\n"
    body += f"--{boundary}--\r\n".encode("utf-8")
    headers = dict(HEADERS)
    headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_message(w, advice, news, riddle_q, topic="📰 أخبار متنوعة"):
    tz = ZoneInfo("Africa/Algiers")
    now = datetime.datetime.now(tz)
    weekdays = {"Monday": "الاثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء",
                "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت", "Sunday": "الأحد"}
    date_str = now.strftime("%A %d/%m/%Y")
    for en, ar in weekdays.items():
        date_str = date_str.replace(en, ar)
    time_str = now.strftime("%I:%M %p").replace("AM", "صباحاً").replace("PM", "مساءً")
    line = "━" * 28
    msg = f"""<b>🌤️ بوت الطقس والثقافة اليومي</b>
{line}
📅 {date_str}
🕐 {time_str}
{line}

<b>🌡️ حالة الطقس - {CITY_NAME}</b>
• الحرارة: <b>{w['temp']}°C</b>
• الإحساس: {w['feels']}°C
• الحالة: {w['desc']}
• الرطوبة: {w['humidity']}%
• الرياح: {w['wind']} كم/س ({w['wind_dir']})
• الضغط: {w['pressure']} هكتوباسكال
• الأشعة فوق البنفسجية: {w['uv']}
🌅 الشروق: {w['sunrise']} | الغروب: {w['sunset']}
{line}

<b>💡 نصيحة اليوم</b>
{advice}
{line}

<b>{topic}</b>
{news}
{line}

<b>🤔 لغز اليوم</b>
{riddle_q}
<i>(الحل يوصلك بعد 20 دقيقة)</i>
{line}

<i>أرسلت تلقائياً 🤖</i>"""
    return msg


def prepare_news(article):
    """Return (block, image_url, caption): block goes in the main message;
    when the article page has an og:image, a photo post follows it."""
    if article is None:
        return html.escape(random.choice(FALLBACK_NEWS), quote=False), "", ""
    title = html.escape(article["title"], quote=False)
    source = html.escape(article["source"], quote=False) if article["source"] else "\u063a\u064a\u0631 \u0645\u0639\u0631\u0648\u0641"
    paras, image = [], ""
    real = article["link"]
    try:
        from googlenewsdecoder import gnewsdecoder
        res = gnewsdecoder(article["link"])
        real = (res.get("decoded_url") or "").strip() or article["link"]
        paras, image = fetch_article(real)
    except Exception:
        paras, image = [], ""
    head = f"\U0001F4F0 <b>{title}</b>\n\U0001F5DE\uFE0F \u0627\u0644\u0645\u0635\u062F\u0631: {source}"
    if any(k in (article.get("topic") or "") for k in ("سيبراني", "ذكاء اصطناعي", "تقنية")):
        head = f"⚡️ <b>{title}</b>\n\U0001F5DE\uFE0F \u0627\u0644\u0645\u0635\u062F\u0631: {source}"
    link_html = "\U0001F517 <a href=\"" + html.escape(real, quote=True) + "\">\u0627\u0642\u0631\u0623 \u0627\u0644\u062E\u0628\u0631 \u0643\u0627\u0645\u0644\u0627\u064B</a>"
    if image:
        excerpt = html.escape(paras[0], quote=False) if paras else ""
        if len(paras) > 1 and len(excerpt) < 380:
            excerpt += " " + html.escape(paras[1], quote=False)
        if len(excerpt) > 700:
            excerpt = excerpt[:697].rsplit(" ", 1)[0] + "\u2026"
        caption = head
        if excerpt:
            caption += "\n\n" + excerpt
        caption += "\n\n" + link_html
        return head + "\n" + link_html, image, caption
    if paras:
        body = "\n\n".join(html.escape(p, quote=False) for p in paras)
        return f"{head}\n\n{body}", "", ""
    return head, "", ""

def pick_riddle(state):
    used = state.get("used_riddles", [])
    fresh = [r for r in ARABIC_RIDDLES if r[0] not in used]
    q, a = random.choice(fresh or ARABIC_RIDDLES)
    used.insert(0, q)
    state["used_riddles"] = used[:len(ARABIC_RIDDLES) - 2]
    return q, a


def load_state():
    st = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding="utf-8") as f:
            st = json.load(f)
    st.setdefault("last_main_ts", 0)
    st.setdefault("riddle_answer", "")
    st.setdefault("riddle_sent_ts", 0)
    st.setdefault("used_news", [])
    st.setdefault("used_advice", [])
    st.setdefault("used_riddles", [])
    st.setdefault("news_topic_idx", 0)
    return st

def save_state(st):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)


def run():
    st = load_state()
    now = time.time()
    changed = False

    if now - st["last_main_ts"] >= MAIN_INTERVAL:
        try:
            w = get_weather()
            advice = get_advice(st)
            article = get_news(st)
            news_block, image, caption = prepare_news(article)
            riddle_q, riddle_a = pick_riddle(st)
            topic = article.get("topic") if article else "📰 أخبار متنوعة"
            msg = build_message(w, advice, news_block, riddle_q, topic)
            send_telegram(msg)
            print("Main message sent", flush=True)
            if image:
                try:
                    r = send_photo(image, caption)
                    if not r.get("ok"):
                        raise RuntimeError("sendPhoto rejected the URL")
                    print("News photo sent", flush=True)
                except Exception:
                    try:
                        req = urllib.request.Request(image, headers=HEADERS)
                        with urllib.request.urlopen(req, timeout=25) as resp:
                            img_bytes = resp.read()
                        send_photo_upload(img_bytes, caption)
                        print("News photo uploaded", flush=True)
                    except Exception as e2:
                        print("Photo failed, text fallback:", e2, flush=True)
                        try:
                            send_telegram(caption)
                        except Exception:
                            pass
            st["last_main_ts"] = now
            st["riddle_answer"] = riddle_a
            st["riddle_sent_ts"] = now
            changed = True
        except Exception as e:
            print("Main tick failed:", e, flush=True)

    if st["riddle_answer"] and now - st["riddle_sent_ts"] >= RIDDLE_DELAY:
        try:
            answer = html.escape(st["riddle_answer"], quote=False)
            text = f"\U0001F914 <b>\u062D\u0644 \u0627\u0644\u0644\u063A\u0632</b>\n\n\u0627\u0644\u0644\u063A\u0632 \u0627\u0644\u0644\u064A \u0623\u0631\u0633\u0644\u062A\u0647 \u0644\u0643\u060C \u062D\u0644\u0647 \u0647\u0648:\n\n<b>{answer}</b>\n\n\u0647\u0644 \u062D\u0644\u064A\u062A\u0647\u061F \U0001F604"
            send_telegram(text)
            print("Riddle answer sent", flush=True)
            st["riddle_answer"] = ""
            changed = True
        except Exception as e:
            print("Riddle answer failed:", e, flush=True)

    if changed:
        save_state(st)
    print("Tick done", flush=True)
if __name__ == "__main__":
    run()
