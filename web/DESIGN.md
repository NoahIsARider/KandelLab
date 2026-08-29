# DESIGN.md — KandelLab Visual Specification

## Character & Imagery
A manuscript from a medieval monastery library. Academic text written in iron-gall ink on
parchment, engraved with the precision of copperplate. An anatomist's notebook opened in the
morning light — rigorous, quiet, timeless.

## Visual Strategy
- No SVG, no JS charting: every visualization is built from CSS layout + HTML elements
- Background uses CSS gradients to simulate parchment texture
- Decorative elements are Unicode characters only (❧ ☙ ※ ⁂ ◆ ◇ ▪ ▫ — ‖)
- Data charts use CSS Grid + div width/height to encode values

## Color Palette
| Purpose | Value | Imagery |
|---------|-------|---------|
| Primary background | #f5e6c8 | Aged parchment |
| Secondary background | #efe0c6 | Slightly lighter page |
| Body text | #3d2b1f | Iron-gall ink |
| Headings | #6b3a2a | Ochre red-brown |
| Accent | #8b4513 | Saddle brown |
| Borders | #c4a882 | Old paper edge |
| Data highlight | #2d5016 | Verdigris green |
| Warning / inhibition | #7c2d12 | Rust red |
| Muted text | #78716c | Faded ink |

## Typography
- Headings / ornaments: `Crimson Pro` (Google Fonts, serif, scholarly)
- Body: `Crimson Text` (Google Fonts, highly readable serif)
- Data / formulas: `JetBrains Mono` (monospace, precise)
- CJK fallback: Noto Serif SC

## Layout & Responsiveness
- Max width 960px, centered (manuscript page feel)
- Generous side margins (simulated page margins)
- Double-line borders separate sections
- Responsive: reduced margins on mobile, readability preserved

## Interaction & State
- Minimal motion: opacity fade only
- Hover: slight text-color shift + thin underline
- No bounce, no scale, no floating shadows

## Design Prohibitions
- No SVG elements or JS-bound charting libraries
- No modern UI styling (rounded cards, gradient buttons, glassmorphism)
- No emoji as decoration
- No bright blue/purple/pink tones
- No box-shadow to create modern elevation
- No more than 2 font-weight contrasts
