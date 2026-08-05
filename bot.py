import json
import os
import random
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import datetime
from zoneinfo import ZoneInfo

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["CHAT_ID"]

LAT = "36.5486"
LON = "7.2286"
CITY_NAME = "الركنية، قالمة - الجزائر"

MAIN_INTERVAL = 90 * 60
RIDDLE_DELAY = 20 * 60

STATE_FILE = "state.json"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) WeatherBot/1.0"}

NEWS_QUERY = urllib.parse.quote("جرائم التحقيقات الجنائية")
NEWS_URL = (
    "https://news.google.com/rss/search?q=" + NEWS_QUERY
    + "&hl=ar&gl=DZ&ceid=DZ:ar"
)

ARABIC_TIPS = [
    "اشرب الماء قبل أن تشعر بالعطش، فالعطش علامة تأخر.",
    "ابدأ يومك بكوب ماء دافئ مع ليمون، ينشط الجسم والهضم.",
    "خصص 30 دقيقة يومياً للمشي، تحمي قلبك وتهدئ أعصابك.",
    "نام 7-8 ساعات يومياً؛ فالنوم الكافي يقوي المناعة والذاكرة.",
    "وجبة الإفطار سر الطاقة؛ لا تهملها حتى لو خفيفة.",
    "خذ استراحة 5 دقائق كل ساعة عمل، سترفع إنتاجيتك.",
    "ابتسم للآخرين، فالابتسامة تفتح القلوب وتبسط الأجواء.",
    "رتب سريرك فور الاستيقاظ؛ خطوة صغيرة تهيئك ليوم منظم.",
    "قلل السكر والمشروبات الغازية، ستشعر بفرق كبير في نشاطك.",
    "خصم من وقت الجوال ساعة يومياً لقراءة كتاب.",
    "قبل النوم، اكتب ثلاثة أشياء امتنّت لها اليوم.",
    "تجنب الأكل قبل النوم بساعتين على الأقل لهضم أفضل.",
    "تعلم شيئاً جديداً كل يوم، ولو صفحة واحدة.",
    "صاحب الناس الطيبين، فالأخلاق تنتقل بالمجالسة.",
    "لا تؤجل عمل اليوم إلى الغد، فالوقت أغلى ما تملك.",
    "ممارسة الرياضة 3 مرات أسبوعياً تحسن مزاجك ومظهرك.",
    "استخدم درج بدلاً من المصعد، حركة بسيطة تفيد جسمك.",
    "أكثر من شرب الماء في الطقس الحار خاصةً صيفاً.",
    "نظّم مهامك بأهميتها أولاً ثم بأسرعها.",
    "احترم وقت الآخرين كما تحترم وقتك.",
    "حاول أن تتعلم لغة جديدة، فهي تفتح لك آفاقاً واسعة.",
    "خض تجربة جديدة كل شهر، فالروتين قاتل الحماس.",
    "بعد العمل، خصص وقتاً للعائلة ولو كان قصيراً.",
    "راقب إنفاقك الصغير، فهي التي تكوّن مدخراتك.",
    "اجلس بوضعية صحيحة، ظهرك سيشكرك لاحقاً.",
    "قلل من الشاشات قبل النوم بساعة لنوم أعمق.",
    "أعطِ نفسك يوم إجازة من الالتزامات مرة أسبوعياً.",
    "الصدقة تريح النفس وتزيل الهم، جربها اليوم.",
    "استمع أكثر مما تتكلم، ففي الإنصات حكمة.",
    "ابدأ المهمات الصعبة أول شيء في الصباح وأنت منتعش.",
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


def gtranslate(text):
    q = urllib.parse.quote(text[:2000])
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ar&dt=t&q={q}"
    req = urllib.request.Request(url, headers=HEADERS)
    d = json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
    return "".join(part[0] for part in d[0])


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


def get_advice():
    try:
        d = http_get("https://api.adviceslip.com/advice")
        return gtranslate(d["slip"]["advice"])
    except Exception:
        return random.choice(ARABIC_TIPS)


def get_news():
    try:
        req = urllib.request.Request(NEWS_URL, headers=HEADERS)
        data = urllib.request.urlopen(req, timeout=25).read()
        root = ET.fromstring(data)
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            source = (item.findtext("source") or "").strip()
            if not title:
                continue
            for sep in (" - " + source, " -" + source):
                if title.endswith(sep):
                    title = title[: -len(sep)].strip()
                    break
            if source:
                return f"📰 {title}\n🗞️ المصدر: {source}"
            return f"📰 {title}"
    except Exception:
        pass
    return random.choice(FALLBACK_NEWS)


def get_riddle():
    return random.choice(ARABIC_RIDDLES)


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


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"last_main_ts": 0, "riddle_answer": "", "riddle_sent_ts": 0}


def save_state(st):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)


def run():
    st = load_state()
    now = time.time()
    changed = False

    if now - st["last_main_ts"] >= MAIN_INTERVAL:
        w = get_weather()
        advice = get_advice()
        news = get_news()
        riddle_q, riddle_a = get_riddle()
        msg = build_message(w, advice, news, riddle_q)
        send_telegram(msg)
        print("Main message sent", flush=True)
        st["last_main_ts"] = now
        st["riddle_answer"] = riddle_a
        st["riddle_sent_ts"] = now
        changed = True

    if st["riddle_answer"] and now - st["riddle_sent_ts"] >= RIDDLE_DELAY:
        text = f"🤔 <b>حل اللغز</b>\n\nاللغز اللي أرسلته لك، حله هو:\n\n<b>{st['riddle_answer']}</b>\n\nهل حليته؟ 😄"
        send_telegram(text)
        print("Riddle answer sent", flush=True)
        st["riddle_answer"] = ""
        changed = True

    if changed:
        save_state(st)
    print("Tick done", flush=True)


if __name__ == "__main__":
    run()
