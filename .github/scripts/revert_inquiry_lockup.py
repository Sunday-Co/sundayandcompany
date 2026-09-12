from pathlib import Path

path = Path('assets/rendered-corrections.css')
text = path.read_text(encoding='utf-8')

start = text.index('[aria-label="Project inquiry"] [data-inquiry-kicker],\n#inquiry [data-inquiry-kicker] {', text.index('SUNDAY FINAL POLISH'))
end = text.index('@media (min-width:900px)', start)
replacement = '''/* Inquiry headline relationship restored to the approved version:\n   rose Pinyon lead, espresso Playfair response. */\n[aria-label="Project inquiry"] [data-inquiry-kicker],\n#inquiry [data-inquiry-kicker] {\n  color:var(--sc-rose) !important;\n  font-family:var(--sc-script) !important;\n  font-size:40px !important;\n  font-style:normal !important;\n  font-weight:400 !important;\n  letter-spacing:-.02em !important;\n  line-height:.94 !important;\n  margin:0 0 10px !important;\n}\n[aria-label="Project inquiry"] [data-inquiry-kicker] + h2,\n#inquiry [data-inquiry-kicker] + h2 {\n  color:var(--sc-espresso) !important;\n  font-family:var(--sc-serif) !important;\n  font-size:clamp(28px,2.55vw,36px) !important;\n  font-style:normal !important;\n  font-weight:400 !important;\n  letter-spacing:-.045em !important;\n  line-height:.98 !important;\n  margin:0 0 8px !important;\n  max-width:100% !important;\n}\n[aria-label="Project inquiry"] [data-inquiry-support],\n#inquiry [data-inquiry-support] {\n  margin-top:9px !important;\n}\n@media (max-width:700px) {\n  [aria-label="Project inquiry"] [data-inquiry-kicker],\n  #inquiry [data-inquiry-kicker] {\n    font-size:42px !important;\n    line-height:.92 !important;\n    margin-bottom:10px !important;\n  }\n  [aria-label="Project inquiry"] [data-inquiry-kicker] + h2,\n  #inquiry [data-inquiry-kicker] + h2 {\n    font-size:27px !important;\n    line-height:1 !important;\n    margin:0 0 8px !important;\n  }\n}\n\n'''
text = text[:start] + replacement + text[end:]

# Give the desktop Bill of Work receipt more presence without squeezing tablet layouts.
text = text.replace('@media (min-width:900px) {\n  [data-screen-label^="Our Work"] #top > div {\n    grid-template-columns:minmax(0,1.18fr) minmax(390px,.82fr) !important;\n  }', '@media (min-width:1100px) {\n  [data-screen-label^="Our Work"] #top > div {\n    grid-template-columns:minmax(0,1.08fr) minmax(440px,.92fr) !important;\n  }', 1)
text = text.replace('max-width:470px !important;\n    min-width:390px !important;', 'max-width:520px !important;\n    min-width:440px !important;', 1)

if 'max-width:520px !important;' not in text or 'min-width:440px !important;' not in text:
    raise SystemExit('Desktop Our Work receipt enlargement did not apply')

path.write_text(text, encoding='utf-8')
