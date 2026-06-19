from flask import Flask, request
import requests
from bs4 import BeautifulSoup
import urllib.parse

app = Flask(__name__)

# -----------------------
# URL FIX
# -----------------------
def fix_url(url):
    if not url:
        return ""

    url = url.strip()

    if "uddg=" in url:
        url = urllib.parse.unquote(url.split("uddg=")[-1])

    if url.startswith("//"):
        url = "https:" + url

    if not url.startswith("http"):
        url = "https://" + url

    return url

# -----------------------
# READER MODE (TEMİZ GÖRÜNÜM)
# -----------------------
def reader_mode(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "iframe"]):
        tag.decompose()

    content = ""

    for tag in soup.find_all(["h1", "h2", "h3"]):
        t = tag.get_text(strip=True)
        if t:
            content += f"<h2 style='color:#00ff88'>{t}</h2>"

    for p in soup.find_all("p"):
        t = p.get_text(strip=True)
        if t:
            content += f"<p style='color:#ddd;line-height:1.5'>{t}</p>"

    return content

# -----------------------
# ANA SAYFA (MODERN UI)
# -----------------------
@app.route("/")
def home():
    return """
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body {
            margin:0;
            font-family:Arial;
            background: radial-gradient(circle at top, #1a1a1a, #0a0a0a);
            color:white;
            display:flex;
            justify-content:center;
            align-items:center;
            height:100vh;
        }

        .container {
            width:90%;
            max-width:700px;
            text-align:center;
        }

        .logo {
            font-size:42px;
            font-weight:bold;
            color:#00ff88;
        }

        .subtitle {
            color:#aaa;
            margin-bottom:20px;
        }

        .box {
            background:#111;
            padding:20px;
            border-radius:15px;
            box-shadow:0 0 20px rgba(0,255,136,0.1);
        }

        input {
            width:100%;
            padding:16px;
            margin-top:10px;
            border:none;
            border-radius:12px;
            font-size:16px;
        }

        button {
            width:100%;
            padding:16px;
            margin-top:10px;
            border:none;
            border-radius:12px;
            font-size:16px;
            font-weight:bold;
            cursor:pointer;
        }

        .search {
            background:#00ff88;
            color:black;
        }

        .go {
            background:#222;
            color:white;
            border:1px solid #333;
        }

        @media (max-width:600px) {
            .logo { font-size:32px; }
        }
    </style>
    </head>

    <body>

    <div class="container">

        <div class="logo">YS BROWSER</div>
        <div class="subtitle">Hızlı • Basit • Mobil Uyumlu</div>

        <div class="box">

            <form action="/ara">
                <input name="q" placeholder="Ara...">
                <button class="search">Ara</button>
            </form>

            <form action="/git">
                <input name="url" placeholder="https://site.com">
                <button class="go">Siteye Git</button>
            </form>

        </div>

    </div>

    </body>
    </html>
    """

# -----------------------
# SİTE AÇ
# -----------------------
@app.route("/git")
def git():
    url = fix_url(request.args.get("url"))

    try:
        r = requests.get(url, timeout=10, headers={"User-Agent":"YS Browser"})
        html = reader_mode(r.text)

        return f"""
        <html>
        <body style="background:#111;color:white;font-family:Arial;margin:0;padding:10px;">

        <div style="padding:10px;background:#222;">
            <a href="/" style="color:#00ff88;text-decoration:none;">← Ana Sayfa</a>
            |
            <a href="{url}" style="color:#00ff88;">Orijinal Site</a>
        </div>

        {html}

        </body>
        </html>
        """

    except Exception as e:
        return f"""
        <h3>Site açılamadı</h3>
        <p>{e}</p>
        <a href="/">Geri dön</a>
        """

# -----------------------
# ARAMA (20 SONUÇ + AÇIKLAMA)
# -----------------------
@app.route("/ara")
def ara():
    q = request.args.get("q")

    url = f"https://html.duckduckgo.com/html/?q={q}"
    r = requests.get(url, headers={"User-Agent":"YS Browser"})

    soup = BeautifulSoup(r.text, "html.parser")

    results = soup.find_all("a", class_="result__a")
    descs = soup.find_all("a", class_="result__snippet")

    html = "<h2>SONUÇLAR</h2>"

    for i in range(min(len(results), 20)):
        title = results[i].text
        link = fix_url(results[i].get("href"))
        desc = descs[i].text if i < len(descs) else ""

        safe = urllib.parse.quote(link, safe="")

        html += f"""
        <div style="background:#222;margin:10px;padding:10px;border-radius:10px;">
            <a href="/git?url={safe}" style="color:#00ff88;font-size:18px;text-decoration:none;">
                {title}
            </a>
            <p style="color:#aaa;font-size:12px;">{desc}</p>
        </div>
        """

    return f"""
    <html>
    <body style="background:#111;color:white;font-family:Arial;padding:10px;">
    {html}
    </body>
    </html>
    """

# -----------------------
# START
# -----------------------
app.run(host="0.0.0.0", port=5000)