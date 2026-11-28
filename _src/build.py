"""Build the essay pages for brickblair.com from the Markdown in _src/essays.

Run: python3 _src/build.py   (writes <slug>/index.html at the repo root)
Pages keep their old WordPress addresses so existing links and Google results work again.
"""
import html, pathlib, re
import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_src" / "essays"

ESSAYS = [
    dict(slug="what-are-we-doing-here", title="What Are We Doing Here?", when="June 2021",
         dek="Why make music at all, and why tell anyone about it."),
    dict(slug="we-are-time-prisoners", title="We Are Prisoners of Time", when="June 2021",
         dek="Time is a currency with no fixed exchange rate."),
    dict(slug="on-the-zooms-essay", title="If You Stop Using Zoom, Do You Cease to Exist?", when="December 2021",
         kicker="On the Zooms: the story behind the song", strip_h3=True, lyrics="on-the-zooms-lyrics",
         dek="The story behind On the Zooms: a pandemic love affair, told in Zoom grids and COVID tests. With the lyrics in English and Portuguese.",
         listen=[("Spotify", "https://open.spotify.com/album/1Oe4D4e4wAFyAO3Yq0aVM0"),
                 ("Apple Music", "https://music.apple.com/us/album/on-the-zooms-single/1594350093"),
                 ("SoundCloud", "https://soundcloud.com/brick-blair/on-the-zooms"),
                 ("YouTube", "https://youtu.be/LJVhJ7JicE4")]),
    dict(slug="two-dollar-coat-qa", title="Two Dollar Coat: Answers and Questions", when="March 2022",
         kicker="Two Dollar Coat: the story behind the song",
         dek="What the song is about, free coats, and nearly thirty takes.",
         listen=[("Spotify", "https://open.spotify.com/track/0xqbfcP4kkb3BoOeqOyNJ2"),
                 ("Apple Music", "https://music.apple.com/us/album/two-dollar-coat/1611238389?i=1611238390"),
                 ("SoundCloud", "https://soundcloud.com/brick-blair/two-dollar-coat"),
                 ("YouTube", "https://youtu.be/6Fl8En8sthA")]),
]

LYRICS_SRC = ROOT / "_src" / "lyrics"

# Lyrics pages. "slug" is the page address; Your Device keeps its old WordPress address.
SONGS = [
    dict(src="the-things-i-know", slug="the-things-i-know-lyrics", title="The Things I Know", year="2025",
         credit="Written by Brick Blair",
         listen=[("Spotify", "https://open.spotify.com/track/5NUxcUqPBld3zrTpJ9a1L8"),
                 ("Apple Music", "https://music.apple.com/us/artist/brick-blair/1570843805")]),
    dict(src="white-horse", slug="white-horse-lyrics", title="White Horse", year="2023",
         credit="Written by Brick Blair",
         listen=[("Spotify", "https://open.spotify.com/track/5kckr3vwyTCFsCz4fGupcM"),
                 ("Apple Music", "https://music.apple.com/us/artist/brick-blair/1570843805"),
                 ("SoundCloud", "https://soundcloud.com/brick-blair/white-horse")]),
    dict(src="anthem-in-our-hearts", slug="anthem-in-our-hearts-lyrics", title="Anthem In Our Hearts", year="2022",
         credit='Written by Brick Blair, <a href="https://www.instagram.com/mayalove1/">Maya Coppola</a> and <a href="https://www.midasroyal.com/">Midas Royal</a>',
         audio="/audio/anthem-in-our-hearts.mp3", listen=[]),
    dict(src="ball-of-gold", slug="ball-of-gold-lyrics", title="Ball of Gold", year="2022",
         credit="Written by Brick Blair",
         listen=[("SoundCloud", "https://soundcloud.com/brick-blair/ball-of-gold"),
                 ("YouTube", "https://youtu.be/inNTdfsNJPg")]),
    dict(src="two-dollar-coat", slug="two-dollar-coat-lyrics", title="Two Dollar Coat", year="2022",
         credit="Written by Brick Blair",
         listen=[("Spotify", "https://open.spotify.com/track/0xqbfcP4kkb3BoOeqOyNJ2"),
                 ("Apple Music", "https://music.apple.com/us/album/two-dollar-coat/1611238389?i=1611238390"),
                 ("SoundCloud", "https://soundcloud.com/brick-blair/two-dollar-coat"),
                 ("YouTube", "https://youtu.be/6Fl8En8sthA")]),
    dict(src="your-device", slug="your-device-song-lyrics", title="Your Device", year="2021",
         credit="Written by Brick Blair",
         listen=[("Spotify", "https://open.spotify.com/track/5caLd4nbxAEiYID8kzFs0w"),
                 ("Apple Music", "https://music.apple.com/us/album/your-device-single/1571174090"),
                 ("SoundCloud", "https://soundcloud.com/brick-blair/your-device")]),
]

CSS = """
:root{color-scheme:dark;--bg:#0f0d0c;--bg2:#171412;--ink:#f1e9df;--mute:#b3a89b;--rule:#2c2622;--rust:#d0532c;--rust2:#e5693f}
*{box-sizing:border-box;min-width:0}
body{margin:0;background:var(--bg);color:var(--ink);font:18px/1.7 "Archivo",system-ui,sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit}
a:focus-visible{outline:2px solid var(--rust2);outline-offset:3px}
.wrap{max-width:1240px;margin:0 auto;padding:0 max(5vw,18px)}
.top{border-bottom:1px solid var(--rule)}
.top .wrap{display:flex;justify-content:space-between;align-items:center;gap:16px;min-height:64px}
.home{font-stretch:68%;font-weight:850;text-transform:uppercase;font-size:28px;letter-spacing:-.01em;text-decoration:none;line-height:1;white-space:nowrap}
.top nav{display:flex;gap:20px;font-size:15px}
.top nav a{text-decoration:none;color:var(--mute);padding:8px 0;white-space:nowrap}
.top nav a:hover{color:var(--ink)}
article{max-width:680px;margin:0 auto;padding:clamp(44px,7vw,88px) max(5vw,18px) 24px}
.kicker{color:var(--rust2);font-size:15px;font-weight:600;margin:0 0 14px;letter-spacing:.01em}
h1{font-stretch:75%;font-weight:800;text-transform:uppercase;font-size:clamp(38px,6vw,64px);line-height:1;margin:0 0 18px;letter-spacing:-.005em}
.when{color:var(--mute);font-size:15px;margin:0 0 40px;padding-bottom:28px;border-bottom:1px solid var(--rule)}
.body p{margin:0 0 1.15em}
.body h2,.body h3{font-weight:700;line-height:1.25;margin:2em 0 .6em}
.body h2{font-size:24px}.body h3{font-size:21px}
.body em{font-style:italic}
.body ul{padding-left:1.2em}
.body li{margin:.2em 0}
.body a{text-decoration:none;border-bottom:1px solid var(--rust)}
.listen{display:flex;flex-wrap:wrap;gap:6px 18px;margin:0 0 36px}
.listen a{font-size:15px;font-weight:600;text-decoration:none;border-bottom:1px solid var(--rust);padding:6px 0}
.lyrics{margin-top:56px;padding-top:32px;border-top:1px solid var(--rule)}
.lyrics h2{font-stretch:75%;font-weight:800;text-transform:uppercase;font-size:30px;margin:0 0 20px}
.cols{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px 40px}
.cols h3{font-size:15px;font-weight:600;color:var(--mute);margin:0 0 14px;text-transform:none}
.cols p{margin:0 0 1.1em;line-height:1.55;font-size:16px}
.next{max-width:680px;margin:0 auto;padding:24px max(5vw,18px) 72px}
.cta{background:var(--rust);color:#fff;border-radius:6px;padding:26px 26px 28px}
.cta p{margin:0 0 16px;font-size:17px}
.cta a{display:inline-flex;align-items:center;min-height:48px;padding:0 22px;border-radius:999px;background:#1a1513;color:#fff;font-weight:700;text-decoration:none}
.more{margin-top:36px}
.more h2{font-size:15px;font-weight:600;color:var(--mute);margin:0 0 10px}
.more ul{list-style:none;margin:0;padding:0}
.more li{border-top:1px solid var(--rule)}
.more a{display:block;padding:12px 0;text-decoration:none;font-weight:600}
.more a:hover{color:var(--rust2)}
footer{border-top:1px solid var(--rule);padding:28px 0 40px;color:var(--mute);font-size:15px}
footer .wrap{display:flex;flex-wrap:wrap;justify-content:space-between;gap:12px 32px}
footer a{text-decoration:none;border-bottom:1px solid var(--rule)}
.credit a{text-decoration:none;border-bottom:1px solid var(--rust)}
.lyric p{margin:0 0 1.4em;font-size:19px;line-height:1.6}
.player{display:block;width:100%;margin:0 0 36px}
@media (min-width:960px){.lyrics{margin-left:-120px;margin-right:-120px}}
@media (max-width:640px){.cols{grid-template-columns:minmax(0,1fr)}.top nav{gap:14px}.home{font-size:22px}}
"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Brick Blair</title>
<meta name="description" content="{dek}">
<link rel="canonical" href="https://brickblair.com/{slug}/">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{dek}">
<meta property="og:image" content="https://brickblair.com/img/brick.jpg">
<meta property="og:url" content="https://brickblair.com/{slug}/">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,300..900&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<header class="top"><div class="wrap">
  <a class="home" href="/">Brick Blair</a>
  <nav aria-label="Site"><a href="/#songs">Songs</a><a href="/#writing">Writing</a><a href="/#list">Sign up</a></nav>
</div></header>
<main>
<article>
  {kicker}<h1>{title}</h1>
  <p class="when">Originally published {when}</p>
  {listen}<div class="body">
{body}
  </div>
  {lyrics}
</article>
<section class="next">
  <div class="cta"><p>There's a finished album and an EP still to come out. Get each song by email the day it's released.</p><a href="/#list">Sign up</a></div>
  <div class="more"><h2>More writing</h2><ul>{more}</ul></div>
</section>
</main>
<footer><div class="wrap">
  <span>© 2026 Brick Blair</span>
  <span><a href="https://open.spotify.com/artist/53nM47TLE6Is8HlyEZO4ru">Spotify</a> · <a href="https://music.apple.com/us/artist/brick-blair/1570843805">Apple Music</a> · <a href="https://www.instagram.com/brickblair/">Instagram</a> · <a href="mailto:brick@brickblair.com">brick@brickblair.com</a></span>
</div></footer>
</body>
</html>
"""

LYRIC_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} Lyrics | Brick Blair</title>
<meta name="description" content="{dek}">
<link rel="canonical" href="https://brickblair.com/{slug}/">
<meta property="og:title" content="{title}: lyrics">
<meta property="og:description" content="{dek}">
<meta property="og:image" content="https://brickblair.com/img/{src}.jpg">
<meta property="og:url" content="https://brickblair.com/{slug}/">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,300..900&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<header class="top"><div class="wrap">
  <a class="home" href="/">Brick Blair</a>
  <nav aria-label="Site"><a href="/#songs">Songs</a><a href="/#writing">Writing</a><a href="/#list">Sign up</a></nav>
</div></header>
<main>
<article>
  <p class="kicker">Lyrics</p><h1>{title}</h1>
  <p class="when credit">{credit} &middot; {year}</p>
  {listen}<div class="lyric">
{lyric}
  </div>
</article>
<section class="next">
  <div class="cta"><p>There's a finished album and an EP still to come out. Get each song by email the day it's released.</p><a href="/#list">Sign up</a></div>
  <div class="more"><h2>More lyrics</h2><ul>{more}</ul></div>
</section>
</main>
<footer><div class="wrap">
  <span>&copy; 2026 Brick Blair</span>
  <span><a href="https://open.spotify.com/artist/53nM47TLE6Is8HlyEZO4ru">Spotify</a> · <a href="https://music.apple.com/us/artist/brick-blair/1570843805">Apple Music</a> · <a href="https://www.instagram.com/brickblair/">Instagram</a></span>
</div></footer>
</body>
</html>
"""

REDIRECT = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Brick Blair</title>
<link rel="canonical" href="https://brickblair.com/{to}">
<meta http-equiv="refresh" content="0; url=/{to}">
</head><body><p><a href="/{to}">Continue to brickblair.com/{to}</a></p></body></html>
"""

def md(text):
    text = re.sub(r"(?m)^(\s*\* .*)\n\n(?=\s*\* )", r"\1\n", text)  # tight lists
    return markdown.markdown(text, extensions=["sane_lists"])

def stanzas(text):
    return "\n".join("<p>" + "<br>\n".join(html.escape(l.rstrip()) for l in s.strip().splitlines()) + "</p>"
                     for s in re.split(r"\n\s*\n", text.strip()) if s.strip())

def build():
    for e in ESSAYS:
        text = (SRC / f"{e['slug']}.md").read_text()
        if e.get("strip_h3"):
            text = re.sub(r"\A\s*###[^\n]*\n", "", text)
        body = md(text)
        kicker = f'<p class="kicker">{html.escape(e["kicker"])}</p>' if e.get("kicker") else ""
        listen = ""
        if e.get("listen"):
            listen = '<div class="listen">' + "".join(f'<a href="{u}">Listen on {n}</a>' for n, u in e["listen"]) + "</div>\n  "
        lyrics = ""
        if e.get("lyrics"):
            t = (SRC / f"{e['lyrics']}.md").read_text()
            en, pt = t.split("## Em português: No Zooms")
            lyrics = ('<section class="lyrics" id="lyrics" aria-labelledby="lyrics-h"><h2 id="lyrics-h">Lyrics</h2><div class="cols">'
                      f'<div><h3>On the Zooms</h3>{stanzas(en)}</div>'
                      f'<div lang="pt-BR"><h3>Em português: No Zooms</h3>{stanzas(pt)}</div></div></section>')
        more = "".join(f'<li><a href="/{o["slug"]}/">{html.escape(o["title"])}</a></li>' for o in ESSAYS if o is not e)
        out = PAGE.format(title=html.escape(e["title"]), dek=html.escape(e["dek"]), slug=e["slug"], css=CSS,
                          kicker=kicker, when=e["when"], listen=listen, body=body, lyrics=lyrics, more=more)
        d = ROOT / e["slug"]; d.mkdir(exist_ok=True)
        (d / "index.html").write_text(out)
    # the old lyrics address now points at the lyrics on the essay page
    d = ROOT / "on-the-zooms-lyrics-annotated"; d.mkdir(exist_ok=True)
    (d / "index.html").write_text(REDIRECT.format(to="on-the-zooms-essay/#lyrics"))
    # lyrics pages
    for s in SONGS:
        text = (LYRICS_SRC / f"{s['src']}.md").read_text()
        first = text.strip().splitlines()[0]
        dek = f"Lyrics to {s['title']} by Brick Blair: “{first}”"
        listen = '<div class="listen">' + "".join(f'<a href="{u}">Listen on {n}</a>' for n, u in s["listen"]) + "</div>\n  " if s["listen"] else ""
        if s.get("audio"):
            listen = (f'<audio class="player" controls preload="metadata" controlslist="nodownload" src="{s["audio"]}" '
                      f'aria-label="Play {html.escape(s["title"])}"></audio>\n  ') + listen
        more = "".join(f'<li><a href="/{o["slug"]}/">{html.escape(o["title"])}</a></li>' for o in SONGS if o is not s)
        more += '<li><a href="/on-the-zooms-essay/#lyrics">On the Zooms</a></li>'
        out = LYRIC_PAGE.format(title=html.escape(s["title"]), dek=html.escape(dek), slug=s["slug"], src=s["src"],
                                css=CSS, credit=s["credit"], year=s["year"], listen=listen,
                                lyric=stanzas(text), more=more)
        d = ROOT / s["slug"]; d.mkdir(exist_ok=True)
        (d / "index.html").write_text(out)
    # sitemap so Google picks the pages up
    urls = (["https://brickblair.com/"] + [f"https://brickblair.com/{e['slug']}/" for e in ESSAYS]
            + [f"https://brickblair.com/{s['slug']}/" for s in SONGS])
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                     + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    print("built", [e["slug"] for e in ESSAYS])

if __name__ == "__main__":
    build()
