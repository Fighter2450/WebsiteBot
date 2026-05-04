import smtplib
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# English templates (default)
SUBJECTS_EN = [
    "I made something for {name}",
    "{name} — took me 20 minutes, wanted to share it",
    "Quick thing I built for {name}",
    "Found {name} on Google Maps — made you something",
    "No website? I fixed that for {name}",
]
OPENERS_EN = [
    "I was looking up {category} spots in {city} and your name came up — but no website. So I just built one.",
    "Searched for the best {category} in {city} earlier. Found {name}. No website though, which felt like a missed opportunity — so I made one.",
    "I was browsing Google Maps for {category} places in {city} and noticed {name} didn't have a website. Took me a bit, but I built one for you.",
    "Quick story — I was looking for a great {category} in {city} and came across {name}. No website. That's costing you customers. So I built you one.",
]

# Spanish templates
SUBJECTS_ES = [
    "Hice algo para {name}",
    "{name} — me tomó 20 minutos, quería compartirlo",
    "Algo rápido que construí para {name}",
    "Encontré {name} en Google Maps — te hice algo",
    "¿Sin sitio web? Lo resolví para {name}",
]
OPENERS_ES = [
    "Estaba buscando lugares de {category} en {city} y tu nombre apareció — pero sin sitio web. Así que simplemente construí uno.",
    "Busqué los mejores {category} en {city}. Encontré {name}. Sin sitio web, lo que parecía una oportunidad perdida — así que hice uno.",
    "Estaba navegando en Google Maps buscando {category} en {city} y noté que {name} no tenía sitio web. Me tomó un momento, pero te construí uno.",
]

# French templates
SUBJECTS_FR = [
    "J'ai créé quelque chose pour {name}",
    "{name} — ça m'a pris 20 minutes, je voulais le partager",
    "Quelque chose que j'ai construit pour {name}",
    "J'ai trouvé {name} sur Google Maps — je vous ai fait quelque chose",
]
OPENERS_FR = [
    "Je cherchais des {category} à {city} et votre nom est apparu — mais pas de site web. Alors j'en ai créé un.",
    "J'ai cherché les meilleurs {category} à {city}. J'ai trouvé {name}. Pas de site web, ce qui semblait être une occasion manquée — alors j'en ai fait un.",
    "Je naviguais sur Google Maps pour des {category} à {city} et j'ai remarqué que {name} n'avait pas de site web. J'en ai construit un pour vous.",
]

# Portuguese templates
SUBJECTS_PT = [
    "Fiz algo para {name}",
    "{name} — me levou 20 minutos, queria compartilhar",
    "Algo rápido que construí para {name}",
    "Encontrei {name} no Google Maps — fiz algo para você",
]
OPENERS_PT = [
    "Estava procurando {category} em {city} e seu nome apareceu — mas sem site. Então simplesmente criei um.",
    "Pesquisei os melhores {category} em {city}. Encontrei {name}. Sem site, o que parecia uma oportunidade perdida — então fiz um.",
]

# German templates
SUBJECTS_DE = [
    "Ich habe etwas für {name} gemacht",
    "{name} — hat mich 20 Minuten gekostet, wollte es teilen",
    "Etwas, das ich für {name} gebaut habe",
    "{name} auf Google Maps gefunden — habe etwas für Sie gemacht",
]
OPENERS_DE = [
    "Ich suchte nach {category} in {city} und Ihr Name tauchte auf — aber keine Website. Also habe ich einfach eine erstellt.",
    "Ich suchte die besten {category} in {city}. Ich fand {name}. Keine Website, was wie eine verpasste Gelegenheit wirkte — also habe ich eine gemacht.",
]

# Italian templates
SUBJECTS_IT = [
    "Ho creato qualcosa per {name}",
    "{name} — mi ha richiesto 20 minuti, volevo condividerlo",
    "Qualcosa che ho costruito per {name}",
]
OPENERS_IT = [
    "Stavo cercando {category} a {city} e il tuo nome è apparso — ma senza sito web. Così ne ho creato uno.",
    "Ho cercato i migliori {category} a {city}. Ho trovato {name}. Nessun sito web, il che sembrava un'opportunità persa — così ne ho fatto uno.",
]

# Japanese templates
SUBJECTS_JA = [
    "{name}のためにサイトを作りました",
    "{name} — Googleマップで見つけました",
]
OPENERS_JA = [
    "{city}で{category}を探していて、{name}を見つけました。ウェブサイトがなかったので、作ってみました。",
]

# Korean templates
SUBJECTS_KO = [
    "{name}을 위해 무언가를 만들었습니다",
    "Google Maps에서 {name}을 찾았습니다",
]
OPENERS_KO = [
    "{city}에서 {category}를 찾다가 {name}을 발견했습니다. 웹사이트가 없어서 하나 만들어 드렸습니다.",
]

# Chinese templates
SUBJECTS_ZH = [
    "我为{name}制作了一个网站",
    "在谷歌地图上找到了{name}",
]
OPENERS_ZH = [
    "我在{city}寻找{category}时发现了{name}，但没有网站。所以我为您制作了一个。",
]

# Arabic templates
SUBJECTS_AR = [
    "صنعت شيئاً لـ {name}",
    "وجدت {name} على خرائط جوجل",
]
OPENERS_AR = [
    "كنت أبحث عن {category} في {city} ووجدت {name} — لكن بدون موقع إلكتروني. فقمت ببناء واحد.",
]

TEMPLATES = {
    "en": (SUBJECTS_EN, OPENERS_EN),
    "es": (SUBJECTS_ES, OPENERS_ES),
    "fr": (SUBJECTS_FR, OPENERS_FR),
    "pt": (SUBJECTS_PT, OPENERS_PT),
    "de": (SUBJECTS_DE, OPENERS_DE),
    "it": (SUBJECTS_IT, OPENERS_IT),
    "ja": (SUBJECTS_JA, OPENERS_JA),
    "ko": (SUBJECTS_KO, OPENERS_KO),
    "zh": (SUBJECTS_ZH, OPENERS_ZH),
    "ar": (SUBJECTS_AR, OPENERS_AR),
}

BODY_HTML = """\
<html>
<body style="font-family:Georgia,serif;max-width:560px;margin:40px auto;color:#1a1a1a;line-height:1.75;padding:0 16px">

  <p style="font-size:16px">{opener}</p>

  <div style="text-align:center;margin:32px 0">
    <a href="{preview_url}"
       style="background:#111;color:#fff;padding:15px 34px;border-radius:6px;
              text-decoration:none;font-size:15px;font-weight:600;
              font-family:Arial,sans-serif;letter-spacing:0.02em">
      {cta_view} →
    </a>
  </div>

  <p style="font-size:15px;color:#333">{body_details}</p>

  <p style="font-size:15px;color:#333">
    {body_customize}
    <a href="{customize_url}" style="color:#2563eb;text-decoration:none;font-weight:600">{cta_customize} →</a>
  </p>

  <hr style="border:none;border-top:1px solid #e5e7eb;margin:28px 0">

  <p style="font-size:15px;color:#333">{body_pricing}</p>

  <p style="font-size:15px;color:#333">{body_reply}</p>

  <p style="font-size:16px;margin-top:32px">— {from_name}</p>

  <p style="font-size:13px;color:#9ca3af;margin-top:24px;border-top:1px solid #f3f4f6;padding-top:16px">
    P.S. <a href="{guide_url}" style="color:#6b7280">{cta_guide}</a>
  </p>

</body>
</html>
"""

# Localized UI strings for the email body
LOCALE_STRINGS = {
    "en": {
        "cta_view": "See your website",
        "cta_customize": "personalize it yourself",
        "cta_guide": "Step-by-step guide to go live yourself (under 30 min, ~$12)",
        "body_details": "It's got your hours, address, and pulls in highlights from your Google reviews. Looks good on phones too.",
        "body_customize": "Want to add your logo, real photos, or fix the description? There's a simple editor:",
        "body_pricing": "If you want it live on a real domain — I'll handle everything for $500 to launch + $99/month after that.",
        "body_reply": "No pressure. Just reply and let me know what you think.",
    },
    "es": {
        "cta_view": "Ver tu sitio web",
        "cta_customize": "personalizarlo tú mismo",
        "cta_guide": "Guía paso a paso para publicarlo tú mismo (menos de 30 min, ~$12)",
        "body_details": "Tiene tus horarios, dirección y los aspectos más destacados de tus reseñas de Google. También se ve bien en teléfonos.",
        "body_customize": "¿Quieres agregar tu logo, fotos reales o corregir la descripción? Hay un editor simple:",
        "body_pricing": "Si quieres publicarlo en un dominio real — me encargo de todo por $500 para lanzar + $99/mes después.",
        "body_reply": "Sin presión. Solo responde y dime qué piensas.",
    },
    "fr": {
        "cta_view": "Voir votre site web",
        "cta_customize": "le personnaliser vous-même",
        "cta_guide": "Guide étape par étape pour le mettre en ligne vous-même (moins de 30 min, ~12€)",
        "body_details": "Il contient vos horaires, votre adresse et les points forts de vos avis Google. Il est aussi adapté aux téléphones.",
        "body_customize": "Vous voulez ajouter votre logo, de vraies photos ou corriger la description ? Il y a un éditeur simple :",
        "body_pricing": "Si vous voulez le mettre en ligne sur un vrai domaine — je m'occupe de tout pour 500€ au lancement + 99€/mois ensuite.",
        "body_reply": "Sans pression. Répondez simplement et dites-moi ce que vous en pensez.",
    },
    "pt": {
        "cta_view": "Ver seu site",
        "cta_customize": "personalize você mesmo",
        "cta_guide": "Guia passo a passo para publicar você mesmo (menos de 30 min, ~R$60)",
        "body_details": "Tem seus horários, endereço e destaca suas avaliações do Google. Também fica ótimo no celular.",
        "body_customize": "Quer adicionar seu logo, fotos reais ou corrigir a descrição? Há um editor simples:",
        "body_pricing": "Se quiser publicar em um domínio real — cuido de tudo por $500 para lançar + $99/mês depois.",
        "body_reply": "Sem pressão. Só responda e me diga o que acha.",
    },
    "de": {
        "cta_view": "Ihre Website ansehen",
        "cta_customize": "selbst personalisieren",
        "cta_guide": "Schritt-für-Schritt-Anleitung zum selbst Veröffentlichen (unter 30 Min, ~12€)",
        "body_details": "Sie enthält Ihre Öffnungszeiten, Adresse und Highlights aus Ihren Google-Bewertungen. Sieht auch auf Handys gut aus.",
        "body_customize": "Möchten Sie Ihr Logo, echte Fotos oder die Beschreibung anpassen? Es gibt einen einfachen Editor:",
        "body_pricing": "Wenn Sie sie auf einer echten Domain veröffentlichen möchten — ich kümmere mich um alles für 500€ + 99€/Monat danach.",
        "body_reply": "Kein Druck. Antworten Sie einfach und sagen Sie mir, was Sie denken.",
    },
    "it": {
        "cta_view": "Vedi il tuo sito",
        "cta_customize": "personalizzalo tu stesso",
        "cta_guide": "Guida passo passo per andare online da solo (meno di 30 min, ~12€)",
        "body_details": "Ha i tuoi orari, l'indirizzo e i punti salienti delle tue recensioni Google. Funziona bene anche sui telefoni.",
        "body_customize": "Vuoi aggiungere il tuo logo, foto reali o correggere la descrizione? C'è un editor semplice:",
        "body_pricing": "Se vuoi metterlo online su un dominio reale — mi occupo di tutto per 500€ per il lancio + 99€/mese dopo.",
        "body_reply": "Nessuna pressione. Rispondi e dimmi cosa ne pensi.",
    },
    "ja": {
        "cta_view": "ウェブサイトを見る",
        "cta_customize": "自分でカスタマイズ",
        "cta_guide": "自分で公開するステップバイステップガイド（30分以内、約1,500円）",
        "body_details": "営業時間、住所、Googleレビューのハイライトが含まれています。スマートフォンでも見やすいです。",
        "body_customize": "ロゴ、実際の写真、または説明を追加したい場合は、簡単なエディターがあります：",
        "body_pricing": "実際のドメインで公開したい場合は、すべてお任せください。初期費用50,000円 + 月額10,000円。",
        "body_reply": "プレッシャーはありません。返信して、ご意見をお聞かせください。",
    },
    "ko": {
        "cta_view": "웹사이트 보기",
        "cta_customize": "직접 맞춤 설정",
        "cta_guide": "직접 게시하는 단계별 가이드 (30분 이내, 약 15,000원)",
        "body_details": "영업 시간, 주소, Google 리뷰 하이라이트가 포함되어 있습니다. 휴대폰에서도 잘 보입니다.",
        "body_customize": "로고, 실제 사진 또는 설명을 추가하려면 간단한 편집기가 있습니다:",
        "body_pricing": "실제 도메인에 게시하려면 모든 것을 처리해 드립니다. 출시 $500 + 월 $99.",
        "body_reply": "부담 없습니다. 그냥 답장해서 생각을 알려주세요.",
    },
    "zh": {
        "cta_view": "查看您的网站",
        "cta_customize": "自己定制",
        "cta_guide": "自己上线的分步指南（30分钟内，约80元）",
        "body_details": "包含您的营业时间、地址和Google评论亮点。在手机上也显示良好。",
        "body_customize": "想添加您的Logo、真实照片或修改描述？这里有一个简单的编辑器：",
        "body_pricing": "如果您想在真实域名上上线——我负责一切，启动费$500 + 每月$99。",
        "body_reply": "没有压力。只需回复告诉我您的想法。",
    },
    "ar": {
        "cta_view": "شاهد موقعك",
        "cta_customize": "خصّصه بنفسك",
        "cta_guide": "دليل خطوة بخطوة للنشر بنفسك (أقل من 30 دقيقة، ~45 ريال)",
        "body_details": "يتضمن ساعات عملك وعنوانك وأبرز تقييماتك على Google. يبدو جيداً على الهواتف أيضاً.",
        "body_customize": "هل تريد إضافة شعارك أو صور حقيقية أو تصحيح الوصف؟ هناك محرر بسيط:",
        "body_pricing": "إذا أردت نشره على نطاق حقيقي — سأتولى كل شيء مقابل $500 للإطلاق + $99/شهرياً بعد ذلك.",
        "body_reply": "لا ضغط على الإطلاق. فقط رد وأخبرني برأيك.",
    },
}

# Fallback to English for unsupported languages
def _get_locale(lang):
    return LOCALE_STRINGS.get(lang, LOCALE_STRINGS["en"])

def _get_templates(lang):
    return TEMPLATES.get(lang, (SUBJECTS_EN, OPENERS_EN))


def send_pitch(
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_pass: str,
    from_name: str,
    to_email: str,
    business: dict,
    preview_url: str,
    customize_url: str = "",
    language: str = "en",
):
    name     = business["name"]
    category = business["category"].replace("_", " ")
    city     = business["city"].split(",")[0]
    safe     = name.lower().replace(" ", "").replace("'", "")[:20]
    domain_example = f"www.{safe}.com"
    guide_url = customize_url.rsplit("/customize/", 1)[0] + "/guide" if customize_url else ""

    subjects, openers = _get_templates(language)
    locale = _get_locale(language)

    subject = random.choice(subjects).format(name=name, city=city, category=category)
    opener  = random.choice(openers).format(name=name, category=category, city=city)

    fmt = dict(
        opener=opener, preview_url=preview_url, customize_url=customize_url,
        guide_url=guide_url, from_name=from_name, domain_example=domain_example,
        **locale,
    )

    body_text = f"{opener}\n\n{preview_url}\n\n{locale['body_details']}\n\n{locale['body_pricing']}\n\n— {from_name}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{from_name} <{smtp_user}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(BODY_HTML.format(**fmt), "html"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())
