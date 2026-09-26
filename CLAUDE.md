## Screen size rules (always follow)

- One switch point: 900px. At 900px wide and below (iPhone, iPad mini, iPad portrait), every page, header, footer and component uses the phone version. Above 900px (iPad landscape, narrow laptop windows, laptops) everything uses the laptop version.
- Never add a phone or tablet breakpoint other than 900px. Header and footer switch at the same 900px. The header shows the Menu button up to 1240px; that's the only other width.
- Exception: `min-width: 601px` may be used only to adjust text sizes on iPad mini and iPad portrait (601–900px). It must never change layout, which still switches only at 900px.
- Phone version: cards and side-by-side sections stack one per row. Text uses the phone readability sizes in assets/site.css. Form inputs are 16px or larger so iPhone doesn't zoom.
- Laptop version: cards sit side by side. A row of three cards must never split into two plus one. If a row doesn't fit, it stacks instead.
- Where a heading has a side note and the width is 901–1240px, the note goes under the heading.
- Phones lay out at 75% scale through the viewport script in each page's head. Don't block pinch-to-zoom.
- Before pushing a layout change, check it at 390, 744, 820, 1000, 1024 and 1280px wide.
