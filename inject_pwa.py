#!/usr/bin/env python3
"""
inject_pwa.py
-------------
既存の food_safety_exam_volN.html（N=1..5）の <head> に
PWA に必要な <link>/<meta>/<script> タグを自動で挿入するスクリプト。

使い方:
  1) このスクリプトを vol1〜5 の HTML ファイルと同じフォルダに置く
  2) ターミナルで:
        python3 inject_pwa.py
  3) 元ファイルは food_safety_exam_volN.html.bak としてバックアップされ、
     vol1〜5 の <head> に PWA タグが追加されます。

* すでにスニペットが入っている場合（マーカー "PWA-INJECT-START" を検出）は
  スキップします。
"""
from pathlib import Path
import re
import sys
import shutil

PWA_BLOCK = """\
<!-- PWA-INJECT-START -->
<link rel="manifest" href="./manifest.json" />
<meta name="theme-color" content="#E31837" />
<meta name="application-name" content="FoodSafety模試" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
<meta name="apple-mobile-web-app-title" content="FoodSafety模試" />
<link rel="apple-touch-icon" href="./icons/icon-180.png" />
<link rel="icon" type="image/png" sizes="192x192" href="./icons/icon-192.png" />
<link rel="icon" type="image/png" sizes="512x512" href="./icons/icon-512.png" />
<link rel="shortcut icon" href="./icons/icon-64.png" />
<script>
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('./sw.js').catch(function (e) {
        console.warn('SW register failed:', e);
      });
    });
  }
</script>
<!-- PWA-INJECT-END -->
"""

TARGETS = [f"food_safety_exam_vol{i}.html" for i in (1, 2, 3, 4, 5)]


def inject(path: Path) -> str:
    """Return status string after attempting injection."""
    if not path.exists():
        return f"  [SKIP] {path.name} not found"

    text = path.read_text(encoding="utf-8")

    if "PWA-INJECT-START" in text:
        return f"  [OK]   {path.name} already injected — skipped"

    # Find </head> case-insensitively
    m = re.search(r"</head\s*>", text, flags=re.IGNORECASE)
    if not m:
        return f"  [WARN] {path.name} has no </head>; nothing changed"

    backup = path.with_suffix(path.suffix + ".bak")
    if not backup.exists():
        shutil.copy2(path, backup)

    new_text = text[: m.start()] + PWA_BLOCK + text[m.start():]
    path.write_text(new_text, encoding="utf-8")
    return f"  [OK]   {path.name} injected ({len(PWA_BLOCK)} chars added; backup: {backup.name})"


def main():
    here = Path(__file__).parent.resolve()
    print(f"inject_pwa.py — working in: {here}\n")
    for name in TARGETS:
        print(inject(here / name))
    print("\nDone. Now commit & push the *.html files to GitHub.")
    print("To undo: restore from the .bak files.")


if __name__ == "__main__":
    sys.exit(main())
