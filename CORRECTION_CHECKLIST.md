# Sunday & Company Final Correction Checklist

Working branch: `full-correction-audit-2026-09-11`

This file is temporary and will be removed before merging to `main`. It exists so every approved correction can be checked off deliberately.

## Batch 0 — Repository Safety / Source Of Truth
- [x] Work on a separate correction branch, not directly on `main`.
- [x] Keep `netlify.toml` deploy-only. No build-time HTML/font/CSS rewriting.
- [x] Remove the abandoned temporary correction workflow/script/marker before new work.
- [x] Synchronize all copied shared components from the audited root source.
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
- [x] Sunday Reservation popup signup state source audited for desktop/mobile hierarchy.
- [x] Sunday Reservation popup confirmation state source audited for desktop/mobile hierarchy.
- [x] Footer newsletter form source audited for desktop/mobile hierarchy.
- [x] Footer newsletter confirmation state source audited.
- [x] Project Inquiry popup steps 1/2/3 source audited for desktop/mobile hierarchy.
- [x] Project Inquiry confirmation state source audited for desktop/mobile hierarchy.
- [x] Services-page embedded Project Inquiry is synchronized to the same shared form source.
- [x] Contact form source audited for desktop/mobile hierarchy.
- [x] Contact form confirmation state source audited.
- [x] Sunday School signup/waitlist form source audited for desktop/mobile hierarchy.
- [x] Sunday School signup/waitlist confirmation state source audited.
- [x] Join Our Team `Save Your Interest` form source audited for desktop/mobile hierarchy.
- [x] Join Our Team interest confirmation state source audited.
- [x] No additional standalone form types were found in the production page inventory beyond the shared/global forms and page-specific forms listed above.
- [x] Functional labels have a dedicated readable Light-weight scale instead of receipt-metadata sizing.
- [x] Typed text/placeholders/custom selects/date controls/errors/submit actions have intentional functional sizing rather than one blanket button rule.
- [x] Decorative receipt metadata has its own smaller 400-weight scale.
- [x] Fine print has its own quieter scale and is not enlarged with functional copy.
- [x] `Unsubscribe anytime. Privacy Policy.` has a dedicated reduced mobile treatment without shrinking the whole newsletter receipt.
- [ ] Final visual verification of every form/state after preview/live rendering.

## Batch 3 — Project Inquiry Receipt
- [x] Shared overlay/source explicitly centers the receipt on desktop and mobile.
- [x] Desktop receipt max-width reduced to a compact 880px treatment in shared styles.
- [x] Mobile forced minimum height reduced from the oversized 700px treatment to a restrained content-driven target.
- [x] Add only a restrained amount of bottom cream breathing room after the ledger.
- [x] `A Seat At Our Table` is slightly larger on mobile.
- [x] `Share the essentials. We’ll take it from there.` uses Inter Tight as supporting copy.
- [x] Field labels are reduced only a smidgen and tracking tightened in the shared form type system.
- [x] Receipt metadata (`Sunday & Company`, receipt no., status, etc.) has a dedicated larger/clearer small-text treatment.
- [x] `Next`, `Back`, `Send` and related actions use tighter tracking and Regular weight in shared styles.
- [x] Step navigation now explicitly shows `01 Project Basics`, `02 Timing & Budget`, `03 Project Scope` with the active stage highlighted.
- [x] Services-page inquiry uses the synchronized shared form source and typography.
- [ ] Final visual verification of all three steps and confirmation state.

## Batch 4 — Sunday Reservation Popup
- [x] Desktop popup remains somewhat larger than the earlier too-small version while staying controlled.
- [x] Desktop image is fully full-bleed across the left side with no white strip/inset.
- [x] Mobile popup keeps the approved stacked image-first composition.
- [x] Mobile unsubscribe/privacy line has a dedicated quieter 8px fine-print treatment.
- [x] Signup and confirmation source states share the same receipt/functional typography system.
- [ ] Popup centered/stable behavior visually verified in Safari.

## Batch 5 — Footer / Menu / Small CTAs
- [x] Footer functional typography is one Inter Tight system.
- [x] Explore links, email, location and social handle share the same Light 300 optical weight.
- [x] Rose footer section labels remain slightly stronger at functional Regular weight rather than a separate heavy treatment.
- [x] SC monogram and `A Seat At Our Table` signature remain special brand treatments.
- [x] About `Apply To Join Our Team` CTA copy has a dedicated small readability increase.
- [x] Mobile menu `Reserve Your Seat` and `Contact` labels have a dedicated small readability increase and tighter tracking.
- [x] Mobile CTA touch targets are approximately 44px where targeted.
- [ ] Final mobile footer/menu visual verification.

## Batch 6 — Services Microtype
- [x] `01 / 02 / 03` service numbers have a dedicated mobile readability increase.
- [x] `Starting At…` has a dedicated mobile readability increase.
- [x] `One-Time Project / Ongoing Service` has a dedicated mobile readability increase.
- [x] `What Is Included` has a dedicated mobile readability increase.
- [x] Included-service rows have a dedicated mobile readability increase.
- [x] Excessive uppercase tracking is reduced in the targeted Services microtype rules.
- [x] Large Playfair service names and body copy were not altered by the microtype selectors.
- [ ] Final collapsed/expanded visual verification.

## Batch 7 — Join Our Team Program Cards
- [x] On mobile, full program details are moved into normal page flow instead of a fixed second modal.
- [x] Mobile detail view removes its nested scroll/max-height behavior.
- [x] Desktop keeps the original centered fixed-dialog treatment.
- [ ] Final mobile/desktop visual verification of each program.

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
- [ ] Every form state and confirmation reviewed visually.
- [ ] Every Project Inquiry step reviewed visually.
- [ ] Remaining sub-11px functional UI text reviewed intentionally.
- [ ] Heading weights checked sitewide, including split brown/rose italic headlines.
- [ ] Font flash/layout shift checked.
- [ ] Touch targets checked.
- [ ] Safari Screen + Full Page capture checked.
- [ ] `git diff --check` / syntax validation / Netlify config validation completed.
- [ ] Correction branch merged only after all applicable items above are checked.
