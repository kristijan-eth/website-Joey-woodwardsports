#!/usr/bin/env python3
"""Builds index.html from data/content.json (Woodward Sports Network preview site).

Usage:  python3 tools/build.py
Content facts live in data/content.json; images in img/. Standard library only.
"""
import json, html, os, re, math, time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, 'data', 'content.json')))
E = lambda s: html.escape(str(s), quote=True)
VER = time.strftime('%Y%m%d%H%M')

SITE = D['site']
TEAMS = D['teams']
SHOWS = D['shows']


def team_of(post):
    keys = []
    blob = ' '.join(post['cats'])
    for t in TEAMS:
        if any(c in post['cats'] for c in t['cats']):
            keys.append(t['key'])
    if not keys:
        for t in TEAMS:
            if any(k.lower() in post['title'].lower() for k in t.get('title_hint', [])):
                keys.append(t['key'])
                break
    if 'Pop Culture' in blob and not keys:
        keys.append('culture')
    return keys


def mins(post):
    return max(1, math.ceil(post['words'] / 230))


def nice_date(s):
    return datetime.fromisoformat(s).strftime('%b %-d')


posts = [p for p in D['posts'] if p['id'] not in D['story_skip'] and os.path.exists(os.path.join(ROOT, f"img/news/{p['id']}-600.webp"))]
for p in posts:
    p['teams'] = team_of(p)
stories = posts[:16]

# ---------- fragments ----------

def icon(name, cls='i'):
    return f'<svg class="{cls}" aria-hidden="true"><use href="#i-{name}"/></svg>'


def hero_wall():
    imgs = [f"img/yt/{v}-max.webp" for v in D['long_videos']] + [f"img/news/{p['id']}-600.webp" for p in posts[:12]]
    cols = [[], [], [], [], []]
    for i, src in enumerate(imgs):
        cols[i % 5].append(src)
    out = []
    for ci, col in enumerate(cols):
        tiles = ''.join(f'<img src="{E(s)}" alt="" loading="{"eager" if ci < 3 and j < 2 else "lazy"}" decoding="async">' for j, s in enumerate(col))
        out.append(f'<div class="wall__col" style="--d:{ci}"><div class="wall__track">{tiles}{tiles}</div></div>')
    return '<div class="wall" aria-hidden="true"><div class="wall__plane">' + ''.join(out) + '</div></div>'


def ticker():
    items = [re.split(r'\s*\|\s*', v['title'])[0] for v in D['videos']][:12]
    row = ''.join(f'<li>{E(t)}</li>' for t in items)
    return f'<div class="ticker" aria-label="Latest from the WSN channel"><div class="ticker__tag"><span class="dot"></span>Latest</div><div class="ticker__viewport"><ul class="ticker__row">{row}</ul><ul class="ticker__row" aria-hidden="true">{row}</ul></div></div>'


def team_tiles():
    out = []
    for i, t in enumerate(TEAMS):
        tp = [p for p in posts if t['key'] in p['teams']]
        latest = tp[0]['title'] if tp else ''
        count = len([p for p in stories if t['key'] in p['teams']])
        out.append(f'''<a class="team rv" href="#stories" data-filter="{t['key']}" style="--c1:{t['c1']};--c2:{t['c2']};--i:{i}">
  <span class="team__league">{E(t['league'])}</span>
  <span class="team__name"><span class="team__city">{E(t['city'])}</span>{E(t['name'])}</span>
  <span class="team__latest">{E(latest)}</span>
  <span class="team__go">{count} {'story' if count == 1 else 'stories'} {icon('arrow')}</span>
  <span class="team__ghost" aria-hidden="true">{E(t['name'])}</span>
</a>''')
    return ''.join(out)


def show_cards():
    out = []
    for i, s in enumerate(SHOWS):
        btns = [f'<a class="btn btn--live" href="{E(SITE["live_url"])}" target="_blank" rel="noopener">{icon("play")}Watch</a>',
                f'<a class="btn btn--ghost" href="{E(s["apple"])}" target="_blank" rel="noopener">{icon("apple")}Apple</a>']
        if s.get('spotify'):
            btns.append(f'<a class="btn btn--ghost" href="{E(s["spotify"])}" target="_blank" rel="noopener">{icon("spotify")}Spotify</a>')
        out.append(f'''<article class="show rv" id="show-{s['slug']}" data-show="{s['slug']}" style="--i:{i}">
  <div class="show__art"><img src="img/shows/{s['slug']}.webp" alt="{E(s['name'])} show art" width="720" height="720" loading="lazy" decoding="async"><span class="show__state" data-state>Mon–Fri</span></div>
  <div class="show__body">
    <p class="show__time">{E(s['time'])} ET<span class="hide-sm"> · Mon–Fri</span></p>
    <h3 class="show__name">{E(s['name'])}</h3>
    <p class="show__hosts">{E(s['hosts'])}</p>
    <p class="show__desc">{E(s['desc'])}</p>
    <div class="show__btns">{''.join(btns)}</div>
    <a class="show__sponsor" href="#advertise"><span>Presented by</span><b>Your brand here</b></a>
  </div>
</article>''')
    return ''.join(out)


def timeline():
    blocks = []
    for s in SHOWS:
        a, b = s['start'], s['end']
        blocks.append(f'<a class="tl__block" href="#show-{s["slug"]}" data-show="{s["slug"]}" style="--a:{a - 8};--b:{b - 8}"><b>{E(s["short"])}</b><span>{E(s["time"])}</span></a>')
    hours = ''.join(f'<span style="--h:{h - 8}">{(h - 1) % 12 + 1}{"a" if h < 12 else "p"}</span>' for h in range(8, 20))
    return f'<div class="tl rv" aria-label="Weekday schedule, Eastern Time" data-tl><div class="tl__in"><div class="tl__hours">{hours}</div><div class="tl__track">{"".join(blocks)}<i class="tl__now" hidden></i></div></div></div>'


def video_title(v):
    return re.split(r'\s*\|\s*', v['title'])[0]


def watch_section():
    vids = {v['id']: v for v in D['videos']}
    long = [vids[i] for i in D['long_videos'] if i in vids]
    feat = long[0]
    rest = long[1:]
    def tag(v):
        parts = re.split(r'\s*\|\s*', v['title'])
        return parts[1] if len(parts) > 1 else 'WSN'
    rail = ''.join(f'''<button class="vid rv" data-yt="{v['id']}" data-title="{E(video_title(v))}" style="--i:{i}">
  <span class="vid__thumb"><img src="img/yt/{v['id']}.webp" alt="" width="480" height="360" loading="lazy" decoding="async"><span class="vid__play">{icon('play')}</span></span>
  <span class="vid__tag">{E(tag(v))}</span>
  <span class="vid__title">{E(video_title(v))}</span>
  <span class="vid__meta">{v['views']:,} views · {datetime.fromisoformat(v['published']).strftime('%b %-d')}</span>
</button>''' for i, v in enumerate(rest))
    shorts = ''.join(f'''<a class="short rv" href="https://www.youtube.com/shorts/{v}" target="_blank" rel="noopener" style="--i:{i}">
  <img src="img/yt/{v}-v.webp" alt="" width="360" height="640" loading="lazy" decoding="async">
  <span class="short__title">{E(video_title(vids[v]))}</span>
</a>''' for i, v in enumerate(D['shorts']) if v in vids)
    return f'''<div class="feature rv">
  <button class="feature__player" data-yt="{feat['id']}" data-title="{E(video_title(feat))}" aria-label="Play: {E(video_title(feat))}">
    <img src="img/yt/{feat['id']}-max.webp" alt="" width="1280" height="720" loading="lazy" decoding="async">
    <span class="feature__play">{icon('play')}</span>
  </button>
  <div class="feature__info">
    <span class="kick kick--live"><span class="dot"></span>Latest episode · {E(tag(feat))}</span>
    <h3>{E(video_title(feat))}</h3>
    <p>{feat['views']:,} views · {datetime.fromisoformat(feat['published']).strftime('%A, %B %-d')}</p>
    <div class="row"><a class="btn btn--live" href="{E(SITE['live_url'])}" target="_blank" rel="noopener">{icon('live')}Watch live</a><a class="btn btn--ghost" href="{E(SITE['youtube'])}?sub_confirmation=1" target="_blank" rel="noopener">{icon('youtube')}Subscribe</a></div>
  </div>
</div>
<div class="rail" data-rail><div class="rail__track">{rail}</div></div>
<div class="shorts-head rv"><h3 class="h3">Shorts</h3><a class="link" href="{E(SITE['youtube'])}/shorts" target="_blank" rel="noopener">All Shorts {icon('arrow')}</a></div>
<div class="rail rail--shorts" data-rail><div class="rail__track">{shorts}</div></div>'''


def story_cards():
    chips = [('all', 'All')] + [(t['key'], t['name']) for t in TEAMS] + [('culture', 'Pop Culture')]
    chip_html = ''.join(f'<button class="chip{" is-on" if k == "all" else ""}" data-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}">{E(n)}</button>' for k, n in chips)
    cards = []
    for i, p in enumerate(stories):
        tnames = [t['name'] for t in TEAMS if t['key'] in p['teams']] or (['Pop Culture'] if 'culture' in p['teams'] else ['Detroit Sports'])
        size = ' story--lead' if i == 0 else ''
        img = f"img/news/{p['id']}.webp" if i == 0 else f"img/news/{p['id']}-600.webp"
        excerpt = re.sub(r'\s*Read More.*$', '', p['excerpt'])
        excerpt = (excerpt[:170].rsplit(' ', 1)[0] + '…') if len(excerpt) > 170 else excerpt
        cards.append(f'''<a class="story rv{size}" href="{E(p['link'])}" target="_blank" rel="noopener" data-teams="{' '.join(p['teams']) or 'none'}" style="--i:{i % 4}">
  <span class="story__img"><img src="{img}" alt="" loading="lazy" decoding="async"></span>
  <span class="story__body">
    <span class="story__tag">{E(tnames[0])}</span>
    <span class="story__title">{E(p['title'])}</span>
    {'<span class="story__ex">' + E(excerpt) + '</span>' if i == 0 else ''}
    <span class="story__meta">{E(p['author'])} · {nice_date(p['date'])} · {mins(p)} min read</span>
  </span>
</a>''')
    return f'<div class="chips rv" role="toolbar" aria-label="Filter stories by team">{chip_html}</div><div class="stories" data-stories>{"".join(cards)}</div><p class="stories__empty" hidden>No recent stories for this team. <a href="{E(SITE["news"])}" target="_blank" rel="noopener">Browse all news</a></p>'


def podcasts():
    out = []
    for i, p in enumerate(D['podcasts']):
        eps = f"{p['episodes']:,}+" if p['episodes'] >= 1000 else f"{p['episodes']:,}"
        sp = f'<a href="{E(p["spotify"])}" target="_blank" rel="noopener" aria-label="{E(p["name"])} on Spotify">{icon("spotify")}</a>' if p.get('spotify') else ''
        out.append(f'''<div class="pod rv" style="--i:{i}">
  <img src="img/pods/{p['id']}.webp" alt="{E(p['name'])} cover" width="480" height="480" loading="lazy" decoding="async">
  <div class="pod__body"><b>{E(p['name'])}</b><span>{eps} episodes</span></div>
  <div class="pod__links"><a href="{E(p['apple'])}" target="_blank" rel="noopener" aria-label="{E(p['name'])} on Apple Podcasts">{icon('apple')}</a>{sp}<a href="{E(p['rss'])}" target="_blank" rel="noopener" aria-label="{E(p['name'])} RSS feed">{icon('rss')}</a></div>
</div>''')
    return ''.join(out)


def shop():
    out = []
    for i, s in enumerate(D['shop_pick']):
        out.append(f'''<a class="prod rv" href="https://shop.woodwardsports.com/products/{E(s['handle'])}" target="_blank" rel="noopener" style="--i:{i}">
  <span class="prod__img"><img src="img/shop/{E(s['handle'])}.webp" alt="{E(s['name'])}" loading="lazy" decoding="async"></span>
  <span class="prod__name">{E(s['name'])}</span>
  <span class="prod__price">${E(s['price'])}</span>
</a>''')
    return ''.join(out)


def venues():
    return ''.join(f'<li class="{E(v["role_key"])}"><b>{E(v["name"])}</b><span>{E(v["role"])}</span></li>' for v in D['watch_party']['venues'])


schedule_json = json.dumps([{'slug': s['slug'], 'name': s['name'], 'short': s['short'], 'start': s['start'], 'end': s['end'], 'hosts': s['hosts']} for s in SHOWS])

tpl = open(os.path.join(ROOT, 'tools', 'template.html')).read()
repl = {
    'VER': VER,
    'HERO_WALL': hero_wall(),
    'TICKER': ticker(),
    'TEAMS': team_tiles(),
    'TIMELINE': timeline(),
    'SHOWS': show_cards(),
    'WATCH': watch_section(),
    'STORIES': story_cards(),
    'PODS': podcasts(),
    'SHOP': shop(),
    'VENUES': venues(),
    'SCHEDULE_JSON': schedule_json,
    'STORY_COUNT': str(len(stories)),
}
for k, v in repl.items():
    tpl = tpl.replace('{{' + k + '}}', v)
for k, v in SITE.items():
    tpl = tpl.replace('{{site.' + k + '}}', E(v))
left = re.findall(r'\{\{[^}]+\}\}', tpl)
assert not left, left
open(os.path.join(ROOT, 'index.html'), 'w').write(tpl)
print('index.html written,', len(tpl) // 1024, 'KB,', len(stories), 'stories')
