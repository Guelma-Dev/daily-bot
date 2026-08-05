import html
import json
import os
import random
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

NEWS_QUERY = urllib.parse.quote("جرائم التحقيقات الجنائية")
NEWS_URL = (
    "https://news.google.com/rss/search?q=" + NEWS_QUERY
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


def http_get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
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
    state["used_advice"] = used_list[:20]
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


def fetch_article_text(link):
    req = urllib.request.Request(link, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=25) as resp:
        raw = resp.read()
        try:
            html_str = raw.decode("utf-8")
        except UnicodeDecodeError:
            html_str = raw.decode("iso-8859-6", errors="replace")
    p = TextExtractor()
    p.feed(html_str)
    return p.paras[:4]


def get_news(state):
    try:
        req = urllib.request.Request(NEWS_URL, headers=HEADERS)
        data = urllib.request.urlopen(req, timeout=25).read()
        root = ET.fromstring(data)
        items = []
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
            items.append({"title": title, "source": source, "link": link})
        if not items:
            return None
        used = set(state.get("used_news", []))
        fresh = [it for it in items if it["title"] not in used]
        chosen = random.choice(fresh or items)
        used_list = state.get("used_news", [])
        used_list.insert(0, chosen["title"])
        state["used_news"] = used_list[:30]
        return chosen
    except Exception:
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


def build_message(w, advice, news, riddle_q):
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

<b>📰 أخبار الجرائم والتحقيقات</b>
{news}
{line}

<b>🤔 لغز اليوم</b>
{riddle_q}
<i>(الحل يوصلك بعد 20 دقيقة)</i>
{line}

<i>أرسلت تلقائياً 🤖</i>"""
    return msg


def build_news_block(article):
    if article is None:
        return html.escape(random.choice(FALLBACK_NEWS), quote=False)
    title = html.escape(article["title"], quote=False)
    source = html.escape(article["source"], quote=False) if article["source"] else "غير معروف"
    body = ""
    try:
        from googlenewsdecoder import gnewsdecoder
        res = gnewsdecoder(article["link"])
        real = (res.get("decoded_url") or "").strip() or article["link"]
        paras = fetch_article_text(real)
        if paras:
            body = "\n\n".join(html.escape(p, quote=False) for p in paras)
    except Exception:
        pass
    if body:
        return f"📰 <b>{title}</b>\n🗞️ المصدر: {source}\n\n{body}"
    return f"📰 <b>{title}</b>\n🗞️ المصدر: {source}"


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"last_main_ts": 0, "riddle_answer": "", "riddle_sent_ts": 0,
            "used_news": [], "used_advice": []}


def save_state(st):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)


def run():
    st = load_state()
    now = time.time()
    changed = False

    if now - st["last_main_ts"] >= MAIN_INTERVAL:
        w = get_weather()
        advice = get_advice(st)
        article = get_news(st)
        news = build_news_block(article)
        riddle_q, riddle_a = random.choice(ARABIC_RIDDLES)
        msg = build_message(w, advice, news, riddle_q)
        send_telegram(msg)
        print("Main message sent", flush=True)
        st["last_main_ts"] = now
        st["riddle_answer"] = riddle_a
        st["riddle_sent_ts"] = now
        changed = True

    if st["riddle_answer"] and now - st["riddle_sent_ts"] >= RIDDLE_DELAY:
        answer = html.escape(st["riddle_answer"], quote=False)
        text = f"🤔 <b>حل اللغز</b>\n\nاللغز اللي أرسلته لك، حله هو:\n\n<b>{answer}</b>\n\nهل حليته؟ 😄"
        send_telegram(text)
        print("Riddle answer sent", flush=True)
        st["riddle_answer"] = ""
        changed = True

    if changed:
        save_state(st)
    print("Tick done", flush=True)


if __name__ == "__main__":
    run()
