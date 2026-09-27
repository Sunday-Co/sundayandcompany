## Sunday & Company responsive rules

- Two page layouts only: <=900px mobile, >=901px desktop.
- Compact Menu through 1240px; full navigation at 1241px+.
- Never fake responsiveness with document zoom, a forced 1280px viewport, or matchMedia rewriting.
- Phones below 600px currently use the existing 0.84 viewport baseline.
- Keep one consolidated mobile override block at the end of assets/site.css.
- Project Inquiry and Sunday Reservation auto-size on normal phones and should not have an internal scrollbar in the normal/default state.
- Editable mobile fields stay at 16px or larger.
- Do not retain the modal entrance transform after animation.
- iOS modal width comes from the padded fixed overlay: width:100% inside the overlay, not another 100vw calculation.
- Services inline inquiry: decorative kicker is display:none; keep a real 26px gap after the intro; support copy must not touch the dashed step navigation.
- Services inline footer is always "Next Step" / "Review And Reply".
- Sunday Reservation intro is uppercase.
- Mobile drawer stays skinny; number and label columns stay separately left aligned.
- Footer/menu/support copy should be readable but secondary.
- Above 900px, desktop grids stay fluid at arbitrary widths; 901–1120 may reduce gaps/gutters without creating a third layout.
- Review 390, 744, 820, 901, 1000, 1024, 1120, 1240 and 1280px before pushing responsive work.
