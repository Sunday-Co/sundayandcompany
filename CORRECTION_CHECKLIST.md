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
- [x] Keep Inter Tight as the secondary font.
- [x] Use Inter Tight 300 for larger supporting/editorial sans copy.
- [x] Use Inter Tight 400 for small functional UI and receipt metadata where 300 is too faint.
- [ ] Normalize excessive letter-spacing on all remaining small uppercase UI.
- [ ] Audit all remaining functional text below roughly 11px and decide intentionally whether it is functional, decorative receipt metadata, or true fine print.
- [x] Keep input/textarea/select text at 16px on mobile to prevent iOS focus zoom.
- [x] Standardize Playfair editorial headings to the same numeric weight across split treatments.
- [x] Brown regular Playfair + rose italic Playfair within the same heading use the same weight.
- [x] Preserve approved Our Vision Title Case treatment, italic Playfair, rose quotation marks, and equal paragraph weights.

## Batch 2 — All Forms / Form States Typography Audit
- [x] Inventory every live form and every confirmation/state across the production site.
- [ ] Sunday Reservation popup signup state audited on desktop and mobile.
- [ ] Sunday Reservation popup confirmation state audited on desktop and mobile.
- [ ] Footer newsletter form audited on desktop and mobile.
- [ ] Footer newsletter confirmation state audited.
- [ ] Project Inquiry popup steps 1/2/3 audited on desktop and mobile.
- [ ] Project Inquiry confirmation state audited on desktop and mobile.
- [ ] Services-page embedded Project Inquiry audited on desktop and mobile.
- [ ] Contact form audited on desktop and mobile.
- [ ] Contact form confirmation state audited on desktop and mobile.
- [ ] Sunday School signup/waitlist form audited on desktop and mobile.
- [ ] Sunday School signup/waitlist confirmation state audited.
- [ ] Join Our Team `Save Your Interest` form audited on desktop and mobile.
- [ ] Join Our Team interest confirmation state audited.
- [x] No additional standalone form types were found in the production page inventory beyond the shared/global forms and page-specific forms listed above.
- [ ] Functional labels are readable without becoming visually heavy.
- [ ] Entered text/placeholders/dropdowns/checks/errors/buttons have an intentional functional scale.
- [ ] Decorative receipt metadata has its own smaller scale, using 400 when needed for clarity.
- [ ] Fine print has its own quieter scale and is not accidentally enlarged with functional copy.
- [ ] `Unsubscribe anytime. Privacy Policy.` is reduced on mobile without shrinking the whole newsletter receipt.

## Batch 3 — Project Inquiry Receipt
- [ ] Both desktop and mobile receipts are truly centered.
- [x] Desktop receipt max-width reduced to a compact 880px treatment in shared styles.
- [x] Mobile forced minimum height reduced from the oversized 700px treatment to a restrained content-driven target.
- [x] Add only a restrained amount of bottom cream breathing room after the ledger.
- [x] `A Seat At Our Table` is slightly larger on mobile.
- [x] `Share the essentials. We’ll take it from there.` uses Inter Tight as supporting copy.
- [x] Field labels are reduced only a smidgen and tracking tightened in the shared form type system.
- [x] Receipt metadata (`Sunday & Company`, receipt no., status, etc.) has a dedicated larger/clearer small-text treatment.
- [x] `Next`, `Back`, `Send` and related actions use tighter tracking and Regular weight in shared styles.
- [ ] Mobile step navigation clearly communicates `01 Project Basics`, `02 Timing & Budget`, `03 Project Scope` and current state.
- [ ] Services-page inquiry uses the same synchronized shared form source and typography.

## Batch 4 — Sunday Reservation Popup
- [x] Desktop popup remains somewhat larger than the earlier too-small version while staying controlled.
- [x] Desktop image is fully full-bleed across the left side with no white strip/inset.
- [x] Mobile popup keeps the approved stacked image-first composition.
- [x] Mobile unsubscribe/privacy line has a dedicated quieter 8px fine-print treatment.
- [ ] Signup and confirmation states visually verified to use the same typography hierarchy.
- [ ] Popup remains centered and stable in Safari after live/preview QA.

## Batch 5 — Footer / Menu / Small CTAs
- [ ] Mobile footer is one coherent secondary-font system.
- [ ] Explore links, email, location, social handle and comparable information share the same optical weight.
- [ ] Rose footer section labels may be slightly stronger but not visually disconnected.
- [ ] SC monogram and `A Seat At Our Table` signature remain special brand treatments.
- [x] About `Apply To Join Our Team` CTA copy has a dedicated small readability increase.
- [x] Mobile menu `Reserve Your Seat` and `Contact` labels have a dedicated small readability increase and tighter tracking.
- [x] Mobile CTA touch targets are approximately 44px where targeted.

## Batch 6 — Services Microtype
- [x] `01 / 02 / 03` service numbers have a dedicated mobile readability increase.
- [x] `Starting At…` has a dedicated mobile readability increase.
- [x] `One-Time Project / Ongoing Service` has a dedicated mobile readability increase.
- [x] `What Is Included` has a dedicated mobile readability increase.
- [x] Included-service rows have a dedicated mobile readability increase.
- [x] Excessive uppercase tracking is reduced in the targeted Services microtype rules.
- [ ] Large Playfair service names and body copy visually verified unchanged unless a genuine readability issue is found.

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
- [x] Receipt modals use a subtle paper-lift entrance.
- [ ] Project Inquiry step transitions are subtle rather than abrupt.
- [ ] Service accordion arrows rotate and content fades cleanly.
- [ ] Image/editorial blocks use restrained reveal behavior only where it adds value.
- [x] Targeted CTA arrows move only a few pixels on hover/focus.
- [ ] Mobile menu uses a subtle row stagger if it remains clean in QA.
- [ ] Client Love Letters motion feels like paper/notes rather than generic app animation.
- [x] No bouncing, aggressive parallax, scroll hijacking or random motion is introduced by shared motion styles.
- [x] `prefers-reduced-motion` is respected by the shared motion layer.

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
