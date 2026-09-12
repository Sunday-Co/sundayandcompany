from pathlib import Path
from PIL import Image, ImageOps

src = Path('assets/gallery-capitol.jpeg')
out = Path('assets/opt/gallery-capitol.jpg')
out.parent.mkdir(parents=True, exist_ok=True)

with Image.open(src) as im:
    im = ImageOps.exif_transpose(im).convert('RGB')
    max_width = 1440
    if im.width > max_width:
        h = round(im.height * (max_width / im.width))
        im = im.resize((max_width, h), Image.Resampling.LANCZOS)
    im.save(out, 'JPEG', quality=88, optimize=True, progressive=True)

with Image.open(out) as check:
    pixels = check.width * check.height
    if check.width > 1600 or pixels > 4_500_000:
        raise SystemExit(f'Capture image still too large: {check.width}x{check.height} ({pixels} pixels)')
    print(f'Built {out}: {check.width}x{check.height}, {out.stat().st_size} bytes')
