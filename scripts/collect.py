# -*- coding: utf-8 -*-
"""采集 DIY 硬件新闻。

从 IT之家 / cnbeta 的 RSS 抓取，按关键词过滤出硬件相关条目，
结果写入 data/news.json（覆盖式，保留最新一轮）。

用法：
    python scripts/collect.py
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

import requests

# 数据源（RSS）
RSS_SOURCES = [
    "https://www.ithome.com/rss/",
    "https://www.cnbeta.com.tw/backend.php",
]

# 硬件关键词：命中任一即算「硬件新闻」
KEYWORDS = [
    "显卡", "GPU", "CPU", "处理器", "内存", "主板", "硬盘", "SSD",
    "固态", "装机", "DIY", "电源", "散热", "机箱", "锐龙", "酷睿",
    "RTX", "GTX", "RX", "GeForce", "Radeon", "英特尔", "AMD", "英伟达",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
}

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def strip_html(text: str) -> str:
    """去掉 HTML 标签，压缩空白。"""
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"&nbsp;|&amp;|&#\d+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def is_hardware(title: str, summary: str) -> bool:
    blob = f"{title} {summary}"
    return any(k.lower() in blob.lower() for k in KEYWORDS)


def fetch_rss(url: str) -> list[dict]:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    # 修正可能的编码声明
    content = resp.content
    root = ET.fromstring(content)

    items = []
    for item in root.iter("item"):
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        summary = strip_html(item.findtext("description") or "")
        pub = item.findtext("pubDate") or ""
        items.append(
            {
                "title": strip_html(title),
                "link": link.strip(),
                "summary": summary[:200],
                "published": pub.strip(),
            }
        )
    return items


def main() -> int:
    all_items: list[dict] = []
    for url in RSS_SOURCES:
        try:
            items = fetch_rss(url)
            print(f"[{url}] 抓到 {len(items)} 条")
            all_items.extend(items)
        except Exception as exc:  # noqa: BLE001
            print(f"[{url}] 失败: {exc!r}", file=sys.stderr)

    hardware_items = [
        it for it in all_items if is_hardware(it["title"], it["summary"])
    ]

    # 去重（按 link）
    seen: set[str] = set()
    unique: list[dict] = []
    for it in hardware_items:
        if it["link"] and it["link"] not in seen:
            seen.add(it["link"])
            unique.append(it)

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(unique),
        "items": unique,
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / "news.json"
    out_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"硬件新闻 {len(unique)} 条，已写入 {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
