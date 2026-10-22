"""Inline report images as base64 data URIs so the HTML is fully self-contained.

Rewrites working_db/reports/comic_model_compare_report.html in place:
- every <img src="../generated_assets/..."> becomes an embedded JPEG data URI
- <a href="..."> wrappers around _raw/ panels are unwrapped (raw files are gitignored)
"""
import base64
import io
import re
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
REPORT = HERE.parent.parent / "reports" / "comic_model_compare_report.html"

PAGE_W, PANEL_W = 860, 760
JPEG_Q = 85


def to_data_uri(path: Path, target_w: int) -> str:
    im = Image.open(path).convert("RGB")
    if im.width > target_w:
        im = im.resize((target_w, round(im.height * target_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=JPEG_Q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def main() -> None:
    html = REPORT.read_text(encoding="utf-8")

    def repl_img(m: "re.Match[str]") -> str:
        attrs, rel = m.group(1), m.group(2)
        path = (REPORT.parent / rel).resolve()
        if not path.exists():
            sys.exit(f"missing image: {path}")
        width = PAGE_W if "_page" in path.name else PANEL_W
        return f'<img {attrs}src="{to_data_uri(path, width)}"'

    html2, n_img = re.subn(r'<img ([^>]*?)src="(\.\./generated_assets/[^"]+)"', repl_img, html)
    html2, n_unwrap = re.subn(
        r'<a href="\.\./generated_assets/comics/_raw/[^"]+">(<img [^>]*?src="data:image/[^"]+"[^>]*>)</a>',
        r"\1",
        html2,
    )
    REPORT.write_text(html2, encoding="utf-8")
    print(f"inlined {n_img} images, unwrapped {n_unwrap} raw links -> {REPORT} ({REPORT.stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
