# Heaven Essence Ice Creams — multi-page site

A self-contained local recreation of the Heaven Essence Ice Creams website,
built from the reference at
<https://project-leader-overview-703620.onhercules.app>.

## Pages

| Route | What it is |
| --- | --- |
| `/` | Home — copied from the reference build |
| `/flavours` | Full flavour menu — copied from the reference build (filters, prices, WhatsApp ordering) |
| `/our-story` | Custom-designed story page: kitchen photo, timeline, values and stats |
| `/events` | Custom-designed events & catering page: occasion cards, packages and booking flow |
| `/gallery` | Custom-designed masonry gallery with category filters and a lightbox |
| `/visit` | Custom-designed visit/contact page with an illustrated area map and info cards |
| `/faq` | Custom-designed FAQ with an animated accordion |

All pages share the site's original fonts, colours and header/footer, default
to **light mode**, and have no third-party badge.

## Run it

```bash
node server.js
```

Then open <http://localhost:4173>. The server gzips text assets and serves the
directories as clean routes.

## Assets

- `assets/` — original styles, JS bundles, local font CSS and `custom.css`
  (utilities used by the custom pages)
- `images/` — all flavour, hero and kitchen images
- `_hercules/font/` — Fraunces, Outfit and Caveat webfonts
