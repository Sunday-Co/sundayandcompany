# Sunday & Company Website

## Current production setup

This repository is the source of truth for `https://sundayandcompany.co`.

- Production branch: `main`
- Hosting: Netlify, connected to this GitHub repository
- Publish directory: repository root (`.`)
- Domain: `sundayandcompany.co`
- `www` and HTTP redirect to the HTTPS bare domain through `netlify.toml`

Do **not** drag a folder into Netlify for normal updates. Do **not** recreate the Netlify site or reconnect the domain.

## Safe editing workflow

1. Start from the current `main` branch.
2. Make changes on a temporary/no-deploy branch when the change affects layout, forms, motion, Safari rendering, or shared components.
3. Test mobile and desktop before production. For Safari-sensitive work, include WebKit/browser capture checks.
4. Keep temporary QA scripts and workflows off `main`.
5. Promote one clean production commit to `main` only after the candidate is verified.
6. If CSS or JavaScript behavior changes, bump the asset query version used by the HTML so Safari does not reuse a stale cached file.

## Files that should not be changed casually

### `netlify.toml`

The current file already handles the production publish root, cache rules, and domain redirects. Visual/UI corrections normally do **not** require a `netlify.toml` change.

### Shared site assets

- `assets/site.css` contains the shared typography, responsive, modal, footer, Safari/capture, and accessibility-related production rules.
- `assets/site.js` contains only shared runtime behavior that truly needs JavaScript.
- `assets/rendered-corrections.css` is a production compatibility layer. Avoid stacking new one-off overrides when a source/component correction is possible.

### Shared components

The root `Site Header.dc.html`, `Site Footer.dc.html`, `Inquiry Form.dc.html`, and `Program Cards.dc.html` are the canonical shared component sources. Keep generated/duplicate copies aligned when they are intentionally retained in the repository.

## Forms

Forms submit through the existing Web3Forms integration. Do not replace the keys or form transport during visual changes. After a form-related production update, test a real submission and confirm delivery to `hello@sundayandcompany.co`.

## Accessibility

Safari **Reader** is a browser reading view, not the site's screen-reader implementation. It intentionally removes navigation, controls, and other non-article material and cannot be used as the requirement that every visual element appear in Reader.

The accessibility target for this site is semantic HTML, keyboard access, visible focus, meaningful image alt text, labelled controls, reduced-motion support, and compatibility with assistive technology such as Apple VoiceOver.

## If production looks wrong

First confirm that the live HTML is serving the newest asset query version. If it is still serving the previous version, do not create another visual patch just to force a redeploy. Wait for or diagnose the current Netlify deploy/cache state.

For a real regression, roll back to the last known-good GitHub/Netlify deploy, correct the source on a branch, retest, and then publish one clean commit.
