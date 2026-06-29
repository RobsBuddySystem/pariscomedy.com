#!/usr/bin/env python3
"""Daily ParisComedy content/SEO pass for 2026-06-29.

Bounded, source-cited enrichment only. English-only public copy. No invented claims.
"""
import html, json, sqlite3
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_DB = Path.home() / ".openclaw" / "workspace" / "apps" / "paris-comedy" / "data" / "paris.db"
COMICS = ROOT / "data" / "comedians.json"
OUTBOX = ROOT / "data" / "social_queue.json"
TODAY = "2026-06-29"

RICH_COLUMNS = ["one_man_show", "one_man_show_url", "imdb_url", "filmography", "fun_fact", "press"]

ENRICHMENTS = {
    "guillaume-fosko": {
        "bio": "Guillaume Fosko is a French stand-up comedian associated with Paname Art Café, Le Point Virgule and Café Oscar. Source pages describe his comedy around family life, parenting and self-deprecation.",
        "one_man_show": "Daron Fragile",
        "one_man_show_url": "https://www.lepointvirgule.com/event-pro/guillaumefosko/",
        "imdb_url": "https://www.imdb.com/name/nm15145226/",
        "filmography": "Génération Paname; TV appearances noted by Le Point Virgule include Canal+, France 2 and NRJ12.",
        "fun_fact": "Le Point Virgule says he won the audience prize at the Brides-les-Bains comedy festival in 2019.",
        "press": "Le Point Virgule presents him as a Paname Art Café and Café Oscar resident comic, radio columnist and online-video creator.",
        "sources": [
            {"label": "Paname Art Café", "url": "https://www.panameartcafe.com/artiste/guillaume-fosko"},
            {"label": "Théâtre Le Point Virgule", "url": "https://www.lepointvirgule.com/event-pro/guillaumefosko/"},
            {"label": "IMDb", "url": "https://www.imdb.com/name/nm15145226/"},
        ],
    },
    "gad-elmaleh": {
        "bio": "Gad Elmaleh is a Moroccan-Canadian stand-up comedian and actor with a major French-language career and international screen credits.",
        "one_man_show": "Lui-même",
        "one_man_show_url": "https://www.gadelmaleh.com/",
        "imdb_url": "https://www.imdb.com/name/nm0255362/",
        "filmography": "IMDb lists Gad Elmaleh as known for Priceless, Midnight in Paris and Jack and Jill; his own site links his official channels and current news.",
        "fun_fact": "IMDb's biography notes that his first one-man show, Décalages, drew on his experiences in Montreal and Paris.",
        "press": "His official site foregrounds a very large social audience, including Instagram, Facebook and X/Twitter links.",
        "sources": [
            {"label": "Official site", "url": "https://www.gadelmaleh.com/"},
            {"label": "IMDb", "url": "https://www.imdb.com/name/nm0255362/"},
            {"label": "IMDb biography", "url": "https://www.imdb.com/name/nm0255362/bio/"},
        ],
    },
    "sebastian-marx": {
        "bio": "Sebastian Marx is an American stand-up comedian living in Paris. His official site describes him as an American humorist in France, currently in Paris and on tour.",
        "one_man_show": "On est bien là",
        "one_man_show_url": "https://www.sebmarx.com/en/",
        "imdb_url": "https://www.imdb.com/name/nm5717536/",
        "filmography": "IMDb lists All About Yves, What's Up France? and Expats: Paris among his credits.",
        "fun_fact": "His official site jokes that after 15 years in France, being a foreigner is no longer an excuse.",
        "press": "His official site lists 2026-2027 tour dates, including a Paris date at La Scala.",
        "sources": [
            {"label": "Official site", "url": "https://www.sebmarx.com/en/"},
            {"label": "IMDb", "url": "https://www.imdb.com/name/nm5717536/"},
        ],
    },
    "redouane-bougheraba": {
        "bio": "Redouane Bougheraba is a Marseille comedian and actor. His official site presents him as a Jamel Comedy Club representative from the South of France.",
        "one_man_show": "À jamais",
        "one_man_show_url": "https://redouanebougheraba.fr/",
        "imdb_url": "https://www.imdb.com/name/nm8296813/",
        "filmography": "IMDb lists Sous écrous, Taxi 5 and Délocalisés among his acting credits.",
        "fun_fact": "His official site calls À jamais his first show and describes national touring around France.",
        "press": "AlloCiné maintains a dedicated filmography page for his cinema and TV work.",
        "sources": [
            {"label": "Official site", "url": "https://redouanebougheraba.fr/"},
            {"label": "IMDb", "url": "https://www.imdb.com/name/nm8296813/"},
            {"label": "AlloCiné filmography", "url": "https://www.allocine.fr/personne/fichepersonne-879239/filmographie/"},
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
                "UPDATE comics SET bio=?, one_man_show=?, one_man_show_url=?, imdb_url=?, filmography=?, fun_fact=?, press=? WHERE slug=?",
                (fields["bio"], fields["one_man_show"], fields["one_man_show_url"], fields["imdb_url"], fields["filmography"], fields["fun_fact"], fields["press"], slug),
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
        # Keep language fields binary only.
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
<meta name="description" content="{esc(name)} profile: source-cited bio, show links, screen credits, press notes and Paris comedy context.">
<link rel="canonical" href="https://pariscomedy.com/c/{esc(slug)}.html">
<meta property="og:title" content="{esc(name)} — Paris Comedy"><meta property="og:type" content="profile"><meta property="og:image" content="{esc(photo)}">
<script type="application/ld+json">{json.dumps(person, ensure_ascii=False)}</script>
<style>*{{box-sizing:border-box}}body{{margin:0;background:#0a0a0a;color:#f0f0f0;font:15px/1.55 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}a{{color:#b794f6}}.topnav{{display:flex;justify-content:space-between;gap:16px;align-items:center;padding:14px 24px;border-bottom:1px solid #222;position:sticky;top:0;background:#0a0a0a}}.brand{{font-weight:800;color:#fff;text-decoration:none}}.brand span{{color:#f5c518}}.links{{display:flex;gap:14px;flex-wrap:wrap;font-size:13px}}.links a{{color:#aaa;text-decoration:none}}main{{max-width:980px;margin:auto;padding:32px 24px 80px}}.hero{{display:grid;grid-template-columns:240px 1fr;gap:28px}}@media(max-width:720px){{.hero{{grid-template-columns:1fr}}}}img{{width:240px;height:240px;object-fit:cover;border-radius:14px;background:#222}}h1{{font-size:clamp(30px,5vw,44px);margin:.1em 0}}.badge{{display:inline-block;padding:3px 9px;border-radius:999px;background:#1a3a5c;color:#7ab3e0;font-size:11px;font-weight:800;text-transform:uppercase;margin-right:5px}}.badge-fr{{background:#3a2a1a;color:#e0a07a}}.btn{{display:inline-block;margin:6px 8px 6px 0;padding:10px 14px;border-radius:8px;background:#181818;border:1px solid #2a2a2a;color:#fff;text-decoration:none;font-weight:700}}.primary{{background:#7c3aed;border-color:#7c3aed}}.block{{margin-top:20px;padding:22px;border:1px solid #222;border-radius:12px;background:#111}}.muted{{color:#aaa}}li{{margin:6px 0}}</style></head>
<body><nav class="topnav"><a href="/" class="brand">Paris<span>Comedy</span></a><div class="links"><a href="/shows.html">Shows</a><a href="/venues.html">Venues</a><a href="/comedians.html">Comedians</a><a href="/connect.html">Connect</a></div></nav>
<main><section class="hero"><img src="{esc(photo)}" alt="{esc(name)}" loading="lazy" decoding="async"><div><h1>{esc(name)}</h1><p>{badges}</p><p>{esc(fields['bio'])}</p><p class="muted">{esc(c.get('actuality',''))}</p><p>{''.join(links)}</p></div></section>
<section class="block"><h2>One-person show</h2>{('<p><strong>'+esc(fields['one_man_show'])+'</strong></p><p><a class="btn primary" href="'+esc(fields['one_man_show_url'])+'" target="_blank" rel="noopener">Official tickets / info ↗</a></p>') if fields.get('one_man_show') else '<p class="muted">No verified solo-show link yet.</p>'}</section>
<section class="block"><h2>Screen / stage credits</h2><p>{esc(fields.get('filmography',''))}</p></section>
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
    p = ROOT / "blog" / "whats-on-paris-comedy-this-week-2026-06-29.html"
    p.parent.mkdir(exist_ok=True)
    items = [
        ("Guillaume Fosko", "Daron Fragile: a source-cited spotlight with official Point Virgule ticket link."),
        ("Gad Elmaleh", "Major screen credits plus official-site links and a refreshed Paris Comedy profile."),
        ("Sebastian Marx", "American comic in Paris with official tour notes and IMDb credits."),
    ]
    item_list = {"@context":"https://schema.org","@type":"ItemList","name":"Paris comedy spotlight week of 29 June 2026","itemListElement":[{"@type":"ListItem","position":i+1,"url":f"https://pariscomedy.com/c/{slug}.html","name":name} for i,(slug,name) in enumerate([(s, (load_comics_by_slug().get(s) or {}).get('name', s)) for s in touched[:3]])]}
    cards = "".join(f'<div class="card"><h2><a href="/c/{esc(slug)}.html">{esc(name)}</a></h2><p>{esc(copy)}</p></div>' for (slug, name), (_, copy) in zip([(s, (load_comics_by_slug().get(s) or {}).get('name', s)) for s in touched[:3]], items))
    p.write_text(f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>What's on in Paris comedy this week — Paris Comedy</title><meta name="description" content="This week's Paris comedy spotlight: source-cited comedian profiles and ticket links."><link rel="canonical" href="https://pariscomedy.com/blog/whats-on-paris-comedy-this-week-2026-06-29.html"><script type="application/ld+json">{json.dumps(item_list, ensure_ascii=False)}</script><style>body{{margin:0;background:#0a0a0a;color:#f0f0f0;font:16px/1.6 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}main{{max-width:820px;margin:auto;padding:40px 24px}}a{{color:#b794f6}}.card{{border:1px solid #222;background:#111;border-radius:12px;padding:20px;margin:16px 0}}</style></head><body><main><p><a href="/">← Paris Comedy</a></p><h1>What's on in Paris comedy this week</h1><p>Fresh source-cited picks for the week of 29 June 2026. Today's update focuses on verified comedian profiles and official links; no unsourced listings were added.</p>{cards}</main></body></html>''')
    return p.relative_to(ROOT).as_posix()


def load_comics_by_slug():
    return {c.get("slug"): c for c in json.loads(COMICS.read_text())}


def update_sitemap_robots(touched, blog_path):
    existing = []
    sitemap = ROOT / "sitemap.xml"
    if sitemap.exists():
        import re
        existing = re.findall(r"<loc>(.*?)</loc>", sitemap.read_text())
    urls = set(existing)
    urls.update({"https://pariscomedy.com/", "https://pariscomedy.com/shows.html", "https://pariscomedy.com/venues.html", "https://pariscomedy.com/comedians.html"})
    urls.update(f"https://pariscomedy.com/c/{s}.html" for s in touched)
    urls.add(f"https://pariscomedy.com/{blog_path}")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in sorted(urls):
        xml += f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n"
    xml += "</urlset>\n"
    sitemap.write_text(xml)
    (ROOT / "robots.txt").write_text("User-agent: *\nAllow: /\nDisallow: /admin\nDisallow: /owner\nSitemap: https://pariscomedy.com/sitemap.xml\n")


def fix_binary_language_copy():
    # Guardrail cleanup: public copy must not advertise a third language mode.
    p = ROOT / "comedians.html"
    if p.exists():
        text = p.read_text()
        text = text.replace("Comedians performing English and bilingual stand-up comedy in Paris", "Comedians performing English and French stand-up comedy in Paris")
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
        "title": "Comic spotlight: Gad Elmaleh",
        "language": "en",
        "url": "https://pariscomedy.com/c/gad-elmaleh.html",
        "copy": "Comic spotlight: Gad Elmaleh's Paris Comedy profile now has source-cited screen credits, official links and a clean route to his current show information.",
        "sources": ENRICHMENTS["gad-elmaleh"]["sources"],
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
