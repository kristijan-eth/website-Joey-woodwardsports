# Woodward Sports Network: website preview

A mobile-first preview of a new home for **Woodward Sports Network** (woodwardsports.com): the Woodward 2.0 Digital Hub. One page brings together the live shows, teams, stories, YouTube, podcasts, watch parties, merch, the app and partnerships.

- Preview: https://kristijan-eth.github.io/website-Joey-woodwardsports/
- Client's live site (not replaced): https://woodwardsports.com/
- Plain HTML, CSS and JavaScript. No framework, no build step to deploy, no tracking. YouTube loads only when a visitor presses play.

## What's on the page

| Section | Content and source |
|---|---|
| Hero | Live ON AIR / UP NEXT card with a countdown in Detroit time (`America/Detroit`), Watch live / Listen, channel stats |
| Teams | Lions, Pistons, Tigers, Red Wings, Michigan, Michigan State. A tap filters the stories |
| Lineup | Weekday timeline 8 AM–7 PM ET with a "now" marker, 4 show cards (hosts, Watch, Apple, Spotify) and a "Presented by" sponsor slot |
| Watch | Latest episodes and Shorts from the YouTube channel feed, played in a pop-up player |
| Stories | 16 newest posts from the WordPress REST API, filterable by team; each opens on woodwardsports.com |
| Listen | 6 WSN podcasts (Apple Podcasts lookup, Spotify, RSS) |
| Watch parties | Detroit vs. Buffalo, Downtown Royal Oak fan vote (from woodwardsports.com/woodwardwatchparty) |
| Shop | 10 products from shop.woodwardsports.com (Shopify products.json) |
| App | WSN Live! for iPhone (App Store lookup) |
| Advertise | Audience proof and partnership formats; the contact goes to Instagram / Facebook DMs until a business email is provided |

Weekday schedule (ET): Big D Energy 8–10 AM, Crunch Time 11 AM–1 PM, The Braylon Edwards Show 2–4 PM, Woodward Heavyweights 5–7 PM. Change it in `data/content.json` → `shows[].start` / `end`.

## Files

```
index.html           generated page (content is in the HTML; works without JS)
css/style.css        design tokens, layout, animation
js/main.js           live schedule, reveals, menu, team filter, video player, rails
fonts/               Archivo (variable width + weight) and Instrument Serif Italic, self-hosted
img/                 logo, show art, story photos, YouTube thumbnails, podcast covers, merch, og-image
data/content.json    every fact on the page
tools/build.py       rebuilds index.html from tools/template.html + data/content.json (Python 3, stdlib)
```

Edit `data/content.json` or `tools/template.html`, then run `python3 tools/build.py`. The build stamps a new `?v=` on the CSS and JS so Safari doesn't keep old files.

## Search engines

The page ships with `<meta name="robots" content="noindex, follow">` so it doesn't compete with the live woodwardsports.com. Remove that line when this becomes the real site.
