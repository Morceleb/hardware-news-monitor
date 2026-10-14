# -*- coding: utf-8 -*-
"""把采集到的新闻生成静态站点。

读取 data/news.json，渲染一个简单的 index.html 到 site/ 目录。
配合 GitHub Pages：workflow 跑完采集后执行本脚本，再发布 site/。

用法：
    python scripts/build_site.py
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "news.json"
SITE_DIR = ROOT / "site"


def main() -> int:
    if not DATA_FILE.exists():
        print(f"数据文件不存在：{DATA_FILE}，请先运行 collect.py")
        return 1

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    items = data.get("items", [])
    updated = data.get("updated_at", "")

    rows = []
    for it in items:
        title = html.escape(it["title"])
        link = html.escape(it["link"])
        pub = html.escape(it.get("published", ""))
        summary = html.escape(it.get("summary", ""))
        rows.append(
            f"""
        <li class="item">
          <a href="{link}" target="_blank" rel="noopener">{title}</a>
          <div class="meta">{pub}</div>
          <div class="summary">{summary}</div>
        </li>"""
        )

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DIY 硬件新闻</title>
  <style>
    body {{ font-family: -apple-system, "Segoe UI", "PingFang SC", sans-serif;
           max-width: 720px; margin: 2rem auto; padding: 0 1rem; color: #222; }}
    h1 {{ font-size: 1.6rem; }}
    .updated {{ color: #888; font-size: .85rem; }}
    ul {{ list-style: none; padding: 0; }}
    .item {{ padding: .9rem 0; border-bottom: 1px solid #eee; }}
    .item a {{ font-size: 1.05rem; color: #0b6bcb; text-decoration: none; }}
    .item a:hover {{ text-decoration: underline; }}
    .meta {{ color: #999; font-size: .78rem; margin-top: .2rem; }}
    .summary {{ color: #555; font-size: .9rem; margin-top: .3rem; }}
  </style>
</head>
<body>
  <h1>🖥 DIY 硬件新闻</h1>
  <p class="updated">更新于 {html.escape(updated)} · 共 {len(items)} 条</p>
  <ul>{''.join(rows)}
  </ul>
</body>
</html>"""

    SITE_DIR.mkdir(parents=True, exist_ok=True)
    out = SITE_DIR / "index.html"
    out.write_text(page, encoding="utf-8")
    print(f"站点已生成：{out}（{len(items)} 条新闻）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
