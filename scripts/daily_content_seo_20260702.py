#!/usr/bin/env python3
"""Daily ParisComedy content/SEO pass for 2026-07-02.

Bounded, source-cited enrichment only. English-only public copy. No invented claims.
"""
import html, json, re, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_DB = Path.home() / ".openclaw" / "workspace" / "apps" / "paris-comedy" / "data" / "paris.db"
COMICS = ROOT / "data" / "comedians.json"
OUTBOX = ROOT / "data" / "social_queue.json"
TODAY = "2026-07-02"

RICH_COLUMNS = ["one_man_show", "one_man_show_url", "imdb_url", "filmography", "fun_fact", "press"]

ENRICHMENTS = {
    "paul-taylor": {
        "bio": "Paul Taylor is a British comedian in France. His official site says he created, wrote and starred in WTF France and built a large audience with French-culture comedy; his current official homepage spotlights F*** me I’m French!, a 100% English show.",
        "one_man_show": "F*** me I’m French!",
        "one_man_show_url": "https://paultaylorcomedy.com/",
        "imdb_url": "https://www.imdb.com/name/nm4778088/",
        "filmography": "IMDb lists Paul Taylor - So British ou Presque, Paul Taylor - Bisoubye - Spectacle Complet and Paul Taylor: #Franglais among his credits; his official site also points to TV projects including WTF France and Stereotrip.",
        "fun_fact": "His official site says F*** me I’m French! follows three sold-out world tours and is his first 100% English version of this expat-in-France story.",
        "press": "L’Olympia’s event page describes him as a comedian with more than 1.5 million followers and hundreds of millions of social video views.",
        "sources": [
            {"label": "Official site", "url": "https://paultaylorcomedy.com/"},
            {"label": "Official tickets page", "url": "https://paultaylorcomedy.com/tickets"},
            {"label": "IMDb", "url": "https://www.imdb.com/name/nm4778088/"},
            {"label": "L’Olympia", "url": "https://www.olympiahall.com/en/upcoming-events/paul-taylor/"},
        ],
    },
    "sarah-donnelly": {
        "bio": "Sarah Donnelly is an American comedian, screenwriter, podcaster and actress living in Paris. Her official site says she performs across the U.S., Europe and Asia, has opened for Jerry Seinfeld, toured with Gad Elmaleh and released The Only American in Paris on YouTube.",
        "one_man_show": "The Only American in Paris",
        "one_man_show_url": "https://www.youtube.com/@sarahdcomedy",
        "imdb_url": "",
        "filmography": "Her official site says she co-created, co-wrote and co-starred in Audible Original series God Save My English, won a CNC FAIA grant for TV series Monteton, and has written for Canal+, Paradiso Media, 2P2L, BlackPills, Ausha and Welcome to the Jungle Productions.",
        "fun_fact": "Her official bio closes by saying her French husband, two French children and the French language keep her humble.",
        "press": "Theatre in Paris presents The Only American in Paris as a stand-up hour about French bureaucracy, shopping at Zara and the non-fantasy side of Paris life.",
        "sources": [
            {"label": "Official site", "url": "https://www.sarahdcomedy.com/"},
            {"label": "YouTube channel", "url": "https://www.youtube.com/@sarahdcomedy"},
            {"label": "Theatre in Paris", "url": "https://www.theatreinparis.com/en/show/the-only-american-in-paris-by-sarah-donnelly"},
        ],
    },
    "noman-hosni": {
        "bio": "Noman Hosni is a comedian, actor, writer and director. IMDb says he was a Swiss Comedy Club regular, hosted Garage Live on RTS 2, won the Nuit de l’Humour prize in 2009 and later created the French-language live show Noman’s Land.",
        "one_man_show": "Noman’s Land",
        "one_man_show_url": "",
        "imdb_url": "https://www.imdb.com/name/nm7439962/",
        "filmography": "IMDb identifies him as an actor, writer, director and comedian; his official U.S. site currently points visitors to live dates and a French-side site.",
        "fun_fact": "His official U.S. site includes a dedicated link for French-speaking visitors, while IMDb notes he has performed across Switzerland, France and London.",
        "press": "Offi listed Contes psychédéliques et Green card at Théâtre Le Point Virgule in 2025, describing it as a show about starting over after leaving everything behind.",
        "sources": [
            {"label": "Official site", "url": "https://www.nomancomedy.com/home"},
            {"label": "IMDb", "url": "https://www.imdb.com/name/nm7439962/"},
            {"label": "IMDb biography", "url": "https://www.imdb.com/name/nm7439962/bio/"},
            {"label": "Offi", "url": "https://www.offi.fr/theatre/le-point-virgule-3019/noman-hosni-contes-psychedeliques-et-green-card-101153.html"},
        ],
    },
}


def esc(v):
    return html.escape(str(v or ""), quote=True)


def ensure_db_columns():
    if not APP_DB.exists():
        return "db-missing"
    with sqlite3.connect(APP_DB) as conn:
        existing = {r[1] for r in conn.execute("PRAGMA table_info(comics)")}
        for col in RICH_COLUMNS:
            if col not in existing:
                conn.execute(f"ALTER TABLE comics ADD COLUMN {col} TEXT")
        for slug, fields in ENRICHMENTS.items():
            conn.execute(
                "UPDATE comics SET bio=?, one_man_show=?, one_man_show_url=?, imdb_url=?, filmography=?, fun_fact=?, press=?, actuality=?, actuality_updated=? WHERE slug=?",
                (fields["bio"], fields["one_man_show"], fields["one_man_show_url"], fields["imdb_url"], fields["filmography"], fields["fun_fact"], fields["press"], f"Spotlight updated {TODAY}: {fields['one_man_show'] or 'profile enriched'}.", TODAY, slug),
            )
    return "db-ok"


def load_comics():
    return json.loads(COMICS.read_text())


def update_comics_json():
    data = load_comics()
    by_slug = {c.get("slug"): c for c in data}
    touched = []
    for slug, fields in ENRICHMENTS.items():
        c = by_slug.get(slug)
        if not c:
            continue
        for k, v in fields.items():
            if k != "sources":
                c[k] = v
        c["source_citations"] = fields["sources"]
        c["actuality"] = f"Spotlight updated {TODAY}: {fields['one_man_show'] or 'profile enriched'}."
        if c.get("language") not in ("en", "fr"):
            c["language"] = "en"
        if c.get("langs"):
            c["langs"] = [x for x in c["langs"] if x in ("en", "fr")] or ["en"]
        touched.append(slug)
    COMICS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return data, touched


def render_comic(c):
    slug = c["slug"]
    name = c.get("name") or c.get("stage_name") or slug.replace("-", " ").title()
    fields = ENRICHMENTS[slug]
    photo = c.get("photo") or c.get("photo_url") or f"https://api.dicebear.com/9.x/initials/svg?seed={esc(name).replace(' ','+')}&backgroundColor=1a1a2e&textColor=ffffff&fontSize=40"
    langs = [x for x in (c.get("langs") or [c.get("language") or "en"]) if x in ("en", "fr")]
    badges = "".join(f'<span class="badge badge-{esc(x)}">{esc(x).upper()}</span>' for x in (langs[:2] or ["en"]))
    links = []
    if c.get("instagram"):
        links.append(f'<a class="btn" href="{esc(c["instagram"])}" target="_blank" rel="noopener">Instagram ↗</a>')
    if fields.get("one_man_show_url"):
        links.append(f'<a class="btn primary" href="{esc(fields["one_man_show_url"])}" target="_blank" rel="noopener">Official show / tickets ↗</a>')
    if fields.get("imdb_url"):
        links.append(f'<a class="btn" href="{esc(fields["imdb_url"])}" target="_blank" rel="noopener">IMDb ↗</a>')
    sources = "".join(f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["label"])} ↗</a></li>' for s in fields["sources"])
    same_as = [u for u in [c.get("instagram"), fields.get("imdb_url"), fields.get("one_man_show_url")] if u]
    person = {"@context":"https://schema.org", "@type":"Person", "name":name, "url":f"https://pariscomedy.com/c/{slug}.html", "image":photo, "jobTitle":"Comedian", "sameAs":same_as}
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(name)} — Paris Comedy comedian profile</title>
<meta name="description" content="{esc(name)} profile: source-cited bio, solo show, screen credits, press notes and Paris comedy links.">
<link rel="canonical" href="https://pariscomedy.com/c/{esc(slug)}.html">
<meta property="og:title" content="{esc(name)} — Paris Comedy"><meta property="og:type" content="profile"><meta property="og:image" content="{esc(photo)}">
<script type="application/ld+json">{json.dumps(person, ensure_ascii=False)}</script>
<style>*{{box-sizing:border-box}}body{{margin:0;background:#0a0a0a;color:#f0f0f0;font:15px/1.55 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}a{{color:#b794f6}}.topnav{{display:flex;justify-content:space-between;gap:16px;align-items:center;padding:14px 24px;border-bottom:1px solid #222;position:sticky;top:0;background:#0a0a0a}}.brand{{font-weight:800;color:#fff;text-decoration:none}}.brand span{{color:#f5c518}}.links{{display:flex;gap:14px;flex-wrap:wrap;font-size:13px}}.links a{{color:#aaa;text-decoration:none}}main{{max-width:980px;margin:auto;padding:32px 24px 80px}}.hero{{display:grid;grid-template-columns:240px 1fr;gap:28px}}@media(max-width:720px){{.hero{{grid-template-columns:1fr}}}}img{{width:240px;height:240px;object-fit:cover;border-radius:14px;background:#222}}h1{{font-size:clamp(30px,5vw,44px);margin:.1em 0}}.badge{{display:inline-block;padding:3px 9px;border-radius:999px;background:#1a3a5c;color:#7ab3e0;font-size:11px;font-weight:800;text-transform:uppercase;margin-right:5px}}.badge-fr{{background:#3a2a1a;color:#e0a07a}}.btn{{display:inline-block;margin:6px 8px 6px 0;padding:10px 14px;border-radius:8px;background:#181818;border:1px solid #2a2a2a;color:#fff;text-decoration:none;font-weight:700}}.primary{{background:#7c3aed;border-color:#7c3aed}}.block{{margin-top:20px;padding:22px;border:1px solid #222;border-radius:12px;background:#111}}.muted{{color:#aaa}}li{{margin:6px 0}}</style></head>
<body><nav class="topnav"><a href="/" class="brand">Paris<span>Comedy</span></a><div class="links"><a href="/shows.html">Shows</a><a href="/venues.html">Venues</a><a href="/comedians.html">Comedians</a><a href="/connect.html">Connect</a></div></nav>
<main><section class="hero"><img src="{esc(photo)}" alt="{esc(name)}" loading="lazy" decoding="async"><div><h1>{esc(name)}</h1><p>{badges}</p><p>{esc(fields['bio'])}</p><p class="muted">{esc(c.get('actuality',''))}</p><p>{''.join(links)}</p></div></section>
<section class="block"><h2>Solo show</h2>{('<p><strong>'+esc(fields['one_man_show'])+'</strong></p><p><a class="btn primary" href="'+esc(fields['one_man_show_url'])+'" target="_blank" rel="noopener">Official tickets / information ↗</a></p>') if fields.get('one_man_show_url') else ('<p><strong>'+esc(fields['one_man_show'])+'</strong></p><p class="muted">No verified current ticket link yet.</p>' if fields.get('one_man_show') else '<p class="muted">No verified solo-show link yet.</p>')}</section>
<section class="block"><h2>Screen and stage credits</h2><p>{esc(fields.get('filmography',''))}</p></section>
<section class="block"><h2>Fun fact</h2><p>{esc(fields.get('fun_fact',''))}</p></section>
<section class="block"><h2>Press notes</h2><p>{esc(fields.get('press',''))}</p></section>
<section class="block"><h2>Sources</h2><ul>{sources}</ul><p class="muted">Claims are source-cited; unknown fields are left blank.</p></section>
<div data-ad-slot="comic-footer"></div></main><script src="/assets/ads.js" defer></script></body></html>'''


def render_pages(data, touched):
    out = ROOT / "c"
    out.mkdir(exist_ok=True)
    by_slug = {c.get("slug"): c for c in data}
    for slug in touched:
        (out / f"{slug}.html").write_text(render_comic(by_slug[slug]))


def write_whatson(touched):
    p = ROOT / "blog" / "whats-on-paris-comedy-this-week-2026-07-02.html"
    p.parent.mkdir(exist_ok=True)
    by_slug = {c.get("slug"): c for c in load_comics()}
    cards = []
    for slug in touched:
        c = by_slug.get(slug, {})
        fields = ENRICHMENTS[slug]
        link = fields.get("one_man_show_url") or f"/c/{slug}.html"
        cards.append(f'<div class="card"><h2><a href="/c/{esc(slug)}.html">{esc(c.get("name", slug))}</a></h2><p>{esc(fields["one_man_show"] or "Fresh profile")} — {esc(fields["fun_fact"])} <a href="{esc(link)}">Official link ↗</a></p></div>')
    item_list = {"@context":"https://schema.org","@type":"ItemList","name":"Paris comedy spotlight week of 2 July 2026","itemListElement":[{"@type":"ListItem","position":i+1,"url":f"https://pariscomedy.com/c/{slug}.html","name":by_slug.get(slug, {}).get("name", slug)} for i,slug in enumerate(touched[:3])]}
    p.write_text(f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>What's on in Paris comedy this week — Paris Comedy</title><meta name="description" content="This week's Paris comedy spotlight: source-cited comedian profiles and official links."><link rel="canonical" href="https://pariscomedy.com/blog/whats-on-paris-comedy-this-week-2026-07-02.html"><script type="application/ld+json">{json.dumps(item_list, ensure_ascii=False)}</script><style>body{{margin:0;background:#0a0a0a;color:#f0f0f0;font:16px/1.6 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}main{{max-width:820px;margin:auto;padding:40px 24px}}a{{color:#b794f6}}.card{{border:1px solid #222;background:#111;border-radius:12px;padding:20px;margin:16px 0}}</style></head><body><main><p><a href="/">← Paris Comedy</a></p><h1>What's on in Paris comedy this week</h1><p>Fresh source-cited picks for the week of 2 July 2026. Today's update focuses on verified comedian profiles and official links; no unsourced listings were added.</p>{''.join(cards)}</main></body></html>''')
    return p.relative_to(ROOT).as_posix()


def update_sitemap_robots(touched, blog_path):
    sitemap = ROOT / "sitemap.xml"
    existing = re.findall(r"<loc>(.*?)</loc>", sitemap.read_text()) if sitemap.exists() else []
    urls = set(existing)
    urls.update({"https://pariscomedy.com/", "https://pariscomedy.com/shows.html", "https://pariscomedy.com/venues.html", "https://pariscomedy.com/comedians.html"})
    urls.update(f"https://pariscomedy.com/c/{s}.html" for s in touched)
    urls.add(f"https://pariscomedy.com/{blog_path}")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in sorted(urls):
        xml += f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n"
    xml += "</urlset>\n"
    sitemap.write_text(xml)
    robots = ROOT / "robots.txt"
    text = robots.read_text() if robots.exists() else "User-agent: *\nAllow: /\n"
    if "Sitemap: https://pariscomedy.com/sitemap.xml" not in text:
        text = text.rstrip() + "\nSitemap: https://pariscomedy.com/sitemap.xml\n"
    robots.write_text(text)


def fix_binary_language_copy():
    for p in [ROOT / "comedians.html", ROOT / "data" / "comedians.json"]:
        if p.exists():
            text = p.read_text()
            text = text.replace("bilingual", "English and French")
            text = text.replace("Bilingual", "English and French")
            p.write_text(text)


def write_social_queue():
    queue = []
    if OUTBOX.exists():
        try:
            queue = json.loads(OUTBOX.read_text())
        except Exception:
            queue = []
    queue.append({
        "created_at": TODAY,
        "type": "comic_spotlight",
        "status": "queued",
        "title": "Comic spotlight: Sarah Donnelly",
        "language": "en",
        "url": "https://pariscomedy.com/c/sarah-donnelly.html",
        "copy": "Comic spotlight: Sarah Donnelly’s Paris Comedy profile now has source-cited notes on The Only American in Paris, writing credits and official links.",
        "sources": ENRICHMENTS["sarah-donnelly"]["sources"],
    })
    OUTBOX.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n")


def main():
    db_status = ensure_db_columns()
    data, touched = update_comics_json()
    render_pages(data, touched)
    blog_path = write_whatson(touched)
    update_sitemap_robots(touched, blog_path)
    fix_binary_language_copy()
    write_social_queue()
    print(json.dumps({"db": db_status, "enriched": touched, "blog": blog_path, "queue": str(OUTBOX.relative_to(ROOT))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
