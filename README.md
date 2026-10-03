# Godown Bar — menu

A static, single-page restaurant menu. No build step, no framework, no bundler.
`index.html` is the entire site; the only external request is one Google Font.

**Live:** https://lucent-blini-475f77.netlify.app/

## Files

| Path | What it is |
| --- | --- |
| `index.html` | The menu. All 36 items, prices and descriptions. |
| `Godown.jpeg` | Logo — white line art on solid black. Also the favicon. |
| `generate_qr.py` | Generates the QR codes into `output/`. |
| `output/menu-qr.svg` | Vector QR for print, sized 55 mm. |
| `output/menu-qr.png` | 1200 px+ QR for WhatsApp. |
| `output/menu-qr-logo.png` | QR with the logo in the centre. |

`output/` is generated — don't hand-edit those files.

## Regenerating the QR codes

A QR code encodes whatever URL you hand it, so **regenerate whenever the menu
URL changes**. The old codes will keep pointing at the old address and nothing
will warn you.

```bash
pip install segno pillow opencv-python
python generate_qr.py https://lucent-blini-475f77.netlify.app/ --logo Godown.jpeg
```

The script decodes each PNG it writes and prints `PASS`/`FAIL`, so a silent
break isn't possible. If the logo version ever fails, lower `LOGO_RATIO` from
`0.18` to `0.15`.

Test-scan the printed version on two or three phones before handing it over —
and on mobile data rather than wifi.

## Editing the menu

Sections are fenced by banner comments, so you can find them by searching:

```html
<!-- ========================= STARTERS ========================= -->
```

Each item is a plain `<li class="item">`:

```html
  <li class="item">
    <p class="item__row">
      <span class="item__mid">
        <i class="dot dot--veg" role="img" aria-label="Veg"></i>
        <span class="item__name">Paneer Tikka</span>
        <span class="item__leader" aria-hidden="true"></span>
      </span>
      <span class="item__price">&#8377;340</span>
    </p>
    <p class="item__desc">Char-grilled cottage cheese, hung curd &amp; kasuri methi</p>
  </li>
```

- **Veg / non-veg** — `dot--veg` or `dot--nonveg`.
- **Description** — optional; delete the whole `item__desc` line.
- **Section numbering** (`01`–`07`) comes from a CSS counter, so adding or
  removing a section needs no manual renumbering.

Spots needing a human decision are marked `<!-- EDIT: ... -->`. There are four:
the tagline, the "exclusive" wording, the address, and the GST note.

## Theming

Every colour is a custom property at the top of the file: `--bg`, `--ink`,
`--ink-2`, `--line`, `--leader`, `--veg`, `--nonveg`. The screen palette is
monochrome on black; `@media print` overrides the same variables back to
black-on-white so a printed menu isn't an inked black rectangle.

Contrast is measured, not eyeballed: 19.25:1 for body text and 7.45:1 for
secondary text on black, 21:1 and 9.74:1 in print. Please keep it that way if
you change colours — WCAG AA needs 4.5:1 for body text.

## Deployment

Netlify publishes `main` automatically. Nothing to configure; there is nothing
to build.

## Before this goes on a table

The phone number and address in the footer are **placeholders**. Replace them
in `index.html` before printing anything, then confirm the live page shows the
real details.
