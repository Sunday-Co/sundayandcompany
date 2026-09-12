# Sunday & Company Final Correction Checklist

Working branch: `full-correction-audit-2026-09-11`

This file is temporary and will be removed before merging to `main`. It exists so every approved correction can be checked off deliberately.

## Batch 0 — Repository Safety / Source Of Truth
- [x] Work on a separate correction branch, not directly on `main`.
- [x] Keep `netlify.toml` deploy-only. No build-time HTML/font/CSS rewriting.
- [x] Remove the abandoned temporary correction workflow/script/marker before new work.
- [ ] Confirm shared component copies are synchronized before merge.
- [ ] Remove this checklist before merge.

## Batch 1 — Global Typography System
- [ ] Keep Inter Tight as the secondary font.
- [ ] Use Inter Tight 300 for larger supporting/editorial sans copy.
- [ ] Use Inter Tight 400 for small functional UI and receipt metadata where 300 is too faint.
- [ ] Normalize excessive letter-spacing on small uppercase UI.
- [ ] Audit all remaining functional text below roughly 11px and decide intentionally whether it is functional, decorative receipt metadata, or true fine print.
- [ ] Keep input/textarea/select text at 16px on mobile to prevent iOS focus zoom.
- [ ] Standardize all Playfair editorial headings to the same numeric weight across split treatments.
- [ ] Brown regular Playfair + rose italic Playfair within the same heading must use the same weight.
- [ ] Preserve approved Our Vision Title Case treatment, italic Playfair, rose quotation marks, and equal paragraph weights.

## Batch 2 — All Forms / Form States Typography Audit
- [ ] Inventory every live form and every confirmation/state across the production site.
- [ ] Sunday Reservation popup signup state audited on desktop and mobile.
- [ ] Sunday Reservation popup confirmation state audited on desktop and mobile.
- [ ] Footer newsletter form audited on desktop and mobile.
- [ ] Footer newsletter confirmation/state audited if present.
- [ ] Project Inquiry popup steps 1/2/3 audited on desktop and mobile.
- [ ] Project Inquiry confirmation state audited on desktop and mobile.
- [ ] Services-page embedded Project Inquiry audited on desktop and mobile.
- [ ] Contact form audited on desktop and mobile.
- [ ] Contact form confirmation state audited on desktop and mobile.
- [ ] Sunday School signup/waitlist form audited on desktop and mobile.
- [ ] Any additional form discovered in repository audit is added here and reviewed.
- [ ] Functional labels are readable without becoming visually heavy.
- [ ] Entered text/placeholders/dropdowns/checks/errors/buttons have an intentional functional scale.
- [ ] Decorative receipt metadata has its own smaller scale, using 400 when needed for clarity.
- [ ] Fine print has its own quieter scale and is not accidentally enlarged with functional copy.
- [ ] `Unsubscribe anytime. Privacy Policy.` is reduced on mobile without shrinking the whole newsletter receipt.

## Batch 3 — Project Inquiry Receipt
- [ ] Both desktop and mobile receipts are truly centered.
- [ ] Desktop receipt is compact rather than oversized.
- [ ] Mobile receipt is content-driven, not forced into a giant near-full-screen sheet.
- [ ] Add only a restrained amount of bottom cream breathing room after the ledger.
- [ ] `A Seat At Our Table` is slightly larger on mobile.
- [ ] `Share the essentials. We’ll take it from there.` uses Inter Tight as supporting copy.
- [ ] Field labels are reduced only a smidgen and tracking tightened.
- [ ] Receipt metadata (`Sunday & Company`, receipt no., status, etc.) is slightly larger and clearer on desktop/mobile.
- [ ] `Next`, `Back`, `Send` and related actions use tighter tracking and appropriate weight.
- [ ] Mobile step navigation clearly communicates `01 Project Basics`, `02 Timing & Budget`, `03 Project Scope` and current state.
- [ ] Services-page inquiry uses the same shared form behavior and typography.

## Batch 4 — Sunday Reservation Popup
- [ ] Desktop popup remains somewhat larger than the earlier too-small version.
- [ ] Desktop image is fully full-bleed across the left side with no white strip/inset.
- [ ] Mobile popup keeps the approved stacked image-first composition.
- [ ] Mobile unsubscribe/privacy line is visually quieter and smaller.
- [ ] Signup and confirmation states use the same typography hierarchy.
- [ ] Popup remains centered and stable in Safari.

## Batch 5 — Footer / Menu / Small CTAs
- [ ] Mobile footer is one coherent secondary-font system.
- [ ] Explore links, email, location, social handle and comparable information share the same optical weight.
- [ ] Rose footer section labels may be slightly stronger but not visually disconnected.
- [ ] SC monogram and `A Seat At Our Table` signature remain special brand treatments.
- [ ] About `Apply To Join Our Team` CTA copy gets only a small readability increase.
- [ ] Mobile menu `Reserve Your Seat` and `Contact` labels get a small readability increase and tighter tracking.
- [ ] Mobile touch targets are approximately 44px where appropriate.

## Batch 6 — Services Microtype
- [ ] `01 / 02 / 03` service numbers receive a small readability increase.
- [ ] `Starting At…` receives a small readability increase.
- [ ] `One-Time Project / Ongoing Service` receives a small readability increase.
- [ ] `What Is Included` receives a small readability increase.
- [ ] Included-service rows receive a small readability increase.
- [ ] Excessive uppercase tracking is reduced where needed.
- [ ] Large Playfair service names and body copy remain visually unchanged unless a genuine readability issue is found.

## Batch 7 — Join Our Team Program Cards
- [ ] On mobile, full program details expand inside the page rather than opening a second fixed scrolling modal.
- [ ] Expanded details do not introduce a nested scroll area.
- [ ] Desktop behavior remains intentional and usable.

## Batch 8 — Safari / Hero Rendering
- [ ] Audit every page hero that relies on viewport height, absolute image layers or compositing.
- [ ] Homepage Safari normal screenshot renders correctly.
- [ ] Homepage Safari Full Page capture renders the actual hero instead of a brown/dark field.
- [ ] Other page heroes are document-render safe for Full Page capture.
- [ ] Remove remaining viewport rules that cause visible resizing/jumping as Safari browser chrome changes.
- [ ] No horizontal overflow or accidental browser zoom on mobile.

## Batch 9 — Motion Language
- [ ] Keep motion restrained and specific to Sunday & Co.
- [ ] Section reveals use small upward drift + fade where appropriate.
- [ ] Pinyon accents can reveal slightly after Playfair headings.
- [ ] Receipt modals use a subtle paper-lift entrance.
- [ ] Project Inquiry step transitions are subtle rather than abrupt.
- [ ] Service accordion arrows rotate and content fades cleanly.
- [ ] Image/editorial blocks use restrained reveal behavior only where it adds value.
- [ ] CTA arrows move only a few pixels on hover/focus.
- [ ] Mobile menu can use a subtle row stagger.
- [ ] Client Love Letters motion feels like paper/notes rather than generic app animation.
- [ ] No bouncing, aggressive parallax, scroll hijacking or random motion.
- [ ] `prefers-reduced-motion` is respected everywhere.

## Batch 10 — Final QA Before Merge
- [ ] Home reviewed desktop/mobile.
- [ ] About reviewed desktop/mobile.
- [ ] Services reviewed collapsed/expanded desktop/mobile.
- [ ] Our Work reviewed desktop/mobile.
- [ ] All case-study/project pages reviewed desktop/mobile.
- [ ] Contact reviewed desktop/mobile.
- [ ] Join Our Team reviewed desktop/mobile.
- [ ] Sunday School reviewed desktop/mobile.
- [ ] Privacy / Terms / Cookie / Accessibility / 404 reviewed.
- [ ] Header and desktop navigation reviewed.
- [ ] Mobile menu reviewed.
- [ ] Footer reviewed.
- [ ] Every form state and confirmation reviewed.
- [ ] Every Project Inquiry step reviewed.
- [ ] Remaining sub-11px functional UI text reviewed intentionally.
- [ ] Heading weights checked sitewide, including split brown/rose italic headlines.
- [ ] Font flash/layout shift checked.
- [ ] Touch targets checked.
- [ ] Safari Screen + Full Page capture checked.
- [ ] `git diff --check` / syntax validation / Netlify config validation completed.
- [ ] Correction branch merged only after all applicable items above are checked.
