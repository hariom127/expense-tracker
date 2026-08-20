---
name: web-design
description: Build complete, standalone HTML/CSS web pages that look intentionally designed rather than templated. Use this whenever the user wants a web page, landing page, marketing or product page, portfolio, personal site, coming-soon or event page, or asks to "make me a website / webpage / site for X" — even if they don't mention HTML or design explicitly. Also use when redesigning or restyling an existing HTML page, or turning a brief, some copy, or a rough idea into a finished page. This skill is for standalone HTML/CSS deliverables (a single .html file that opens in a browser), not React/component apps or backend work.
---

# Web Design

You are producing a **complete, standalone web page** — a single `.html` file someone can open in a browser and immediately feel is *designed*, not assembled from defaults. The bar is a page that a small, well-regarded studio would be proud to ship: a clear point of view, executed cleanly, that could not be mistaken for a template.

The failure mode to fight is "AI slop": a page that is technically fine but generic — the same hero, the same fonts, the same three-column feature grid, the same rounded cards you'd get for any prompt. Genericness is the enemy. Everything below exists to help you make *specific* choices for *this* page.

## 1. Ground the design in the subject

Before touching CSS, know what you're building and for whom. If the brief names the subject (a coffee roaster, a dev tool, a wedding, a law firm), design *from that subject's world* — its materials, vocabulary, textures, and references. A page for an analog synth brand should feel different from a page for a tax service, in palette, type, rhythm, and voice.

If the brief is vague ("make a landing page"), pin it down yourself and say so: name a concrete subject, its audience, and the page's single job (sign up? book a call? read the manifesto?). One honest, specific choice beats a page that tries to work for everyone and delights no one. If you have any memory of the user's actual project or preferences, use it.

## 2. Make a quick design plan before you build

Spend a moment — mostly in your head — deciding the four things that give a page identity. Don't skip to code; a page built without a plan drifts toward the defaults.

- **Palette**: 4–6 named hex values with defined roles (background, surface, ink, accent, muted). Derive them from the subject. Avoid the reflexive "cream + warm serif + terracotta" combo (see §3).
- **Type**: pick a *characterful* display face and a comfortable body face that actually pair — not Inter/Roboto/Arial by reflex. The type is the single biggest lever on how designed a page feels. See §4 for how to load real fonts and some pairings worth reaching for.
- **Layout**: one sentence describing the structure and where the eye goes first. Sketch it as a quick ASCII wireframe if it helps you compare options. Modern CSS (grid/flex) — not a stack of identical centered sections.
- **Signature**: the one thing this page will be remembered by — a distinctive hero treatment, a typographic move, an interaction, a background system. Spend your boldness *here* and keep everything else quiet around it.

Then look at the plan with fresh eyes: *if I got this same brief tomorrow, would I land in the same place?* If yes, some part is a default, not a choice — change it and know why.

## 3. Avoid the current AI-design clichés

Right now, AI-generated pages cluster hard around three looks. All are legitimate for *some* brief, but they show up regardless of subject, which is the tell. If the brief doesn't specifically call for one, don't spend your freedom on:

1. **Cream/off-white background (~#F4F1EA) + high-contrast serif + terracotta accent (~#D97757).** This one especially reads as "an AI made this."
2. **Near-black background + one acid-green or vermilion accent.**
3. **Broadsheet/newspaper look**: hairline rules, zero border-radius, dense justified columns — when the content isn't actually editorial.

When the brief *does* pin a direction (including one of these), follow it exactly — the brief always wins. It's the *unrequested* default that's the problem.

## 4. Fonts: the highest-leverage choice

Default fonts are the fastest way to look templated. Load real typefaces from Google Fonts with a `<link>` in the head, and pair with intent — a display face with personality for headings, a clean face for body. A few directions worth reaching for (not an exhaustive list — choose for the subject):

- Editorial / literary: *Fraunces* or *Newsreader* display + *Source Serif* or *Inter* body
- Modern / technical: *Space Grotesk* or *Archivo* + *IBM Plex Sans* or *Geist*
- Warm / friendly: *Bricolage Grotesque* or *Hanken Grotesk* + *Figtree*
- Bold / expressive: *Clash Display*-style, *Syne*, or *Unbounded* for display
- Elegant / refined: *Libre Caslon* or *Cormorant* display + *Mier*/*Inter* body

Set a real type scale with `clamp()` so headings are fluid and dramatic, e.g. `font-size: clamp(2.5rem, 6vw, 5rem)`. Give the display face intentional weight, letter-spacing, and line-height — the type treatment should itself be memorable, not a neutral delivery vehicle.

## 5. Build mechanics for a standalone page

Deliver a **single self-contained `.html` file** with the CSS in a `<style>` block in the `<head>` (and any JS in a `<script>` at the end of `<body>`). Single-file means it opens and previews anywhere with no build step — the right default for this kind of deliverable.

- **Tokens in `:root`.** Put palette, type scale, spacing, and radii in CSS custom properties and reference them everywhere. It keeps the page coherent and makes restyling trivial.
- **Layout with grid and flexbox**, not floats or a pile of centered `<div>`s. Constrain content width (`max-width` ~1100–1200px with padding) so lines don't run edge-to-edge on wide screens.
- **Responsive, checked at 375px.** Design so it collapses gracefully on mobile — stack columns, scale type down via `clamp()`, keep tap targets comfortable. Don't ship a page that only works at desktop width.
- **Images without broken links.** Standalone pages often lack real assets. Prefer CSS gradients, SVG, and CSS-drawn shapes/patterns for atmosphere; use an emoji or inline SVG for icons. If you truly need a photo, use a documented placeholder service (e.g. `https://picsum.photos/1200/800`) rather than inventing a URL that will 404. Never reference a local image file that doesn't exist.
- **Quality floor, built in quietly:** semantic HTML (`<header> <main> <section> <nav> <footer>`), visible keyboard focus states, `alt` text on meaningful images, sufficient color contrast, and `@media (prefers-reduced-motion: reduce)` honored for any animation.
- **Watch CSS specificity.** It's easy to write selectors that quietly cancel each other — a type selector like `.section` and an element rule fighting over the same padding/margin. Keep selectors flat and predictable, especially for spacing between sections.

## 6. Motion, used with restraint

A little motion makes a page feel alive; too much makes it feel like a demo reel and, ironically, more AI-generated. Choose one or two deliberate moments — a load-in sequence, a scroll-triggered reveal, a hover micro-interaction on the primary CTA — rather than animating everything. Always wrap motion in `prefers-reduced-motion`.

## 7. Render it and critique before delivering

Don't ship the first draft blind. If the environment allows, open the file in a headless browser and screenshot it at desktop (1440px) *and* mobile (375px) widths, then actually look at the result and fix what's off — cramped spacing, weak hierarchy, a hero that doesn't land, type that's too timid. A screenshot catches in seconds what reading the code won't.

A quick way to render and capture, if a browser tool is available:

```bash
pip install playwright --break-system-packages -q && playwright install chromium -q
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, w in [("desktop", 1440), ("mobile", 375)]:
        pg = b.new_page(viewport={"width": w, "height": 900})
        pg.goto("file:///home/claude/web-design/page.html")
        pg.screenshot(path=f"/home/claude/{name}.png", full_page=True)
    b.close()
PY
```

Then `view` the screenshots and revise. Before calling it done, run Chanel's test — look at the page and remove one thing that isn't earning its place. Restraint reads as confidence.

## 8. Copy is design material

If the brief doesn't supply text, you're writing it — and generic copy makes a page feel as templated as generic design. Write from the reader's side of the screen: name things by what people recognize, describe what things do in plain terms, use active voice, keep it in sentence case with no filler. A button says exactly what happens ("Start the trial," not "Submit"), and keeps that name through the flow. Specific always beats clever. Empty states and errors are direction, not mood — say what happened and what to do next.

## 9. Deliver

Save the finished page to `/mnt/user-data/outputs/` (e.g. `page.html` or a descriptive name) and present it to the user so they can open it. If you built screenshots, they're a nice supplement, but the `.html` is the deliverable.
