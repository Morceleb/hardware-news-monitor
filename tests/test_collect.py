"""collect.py 的单元测试。

覆盖：HTML 清洗、硬件关键词过滤、按 link 去重。
不发起真实网络请求，纯离线、确定性。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 让 tests 能 import scripts/collect.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import collect


def test_strip_html_removes_tags():
    assert collect.strip_html("<p>显卡 <b>涨价</b></p>") == "显卡 涨价"


def test_strip_html_collapses_whitespace():
    assert collect.strip_html("  内存\n\n价格\t 走势  ") == "内存 价格 走势"


def test_is_hardware_hits_keyword():
    assert collect.is_hardware("RTX 5090 正式发布", "") is True
    assert collect.is_hardware("", "AMD 锐龙新品曝光") is True


def test_is_hardware_misses_irrelevant():
    assert collect.is_hardware("某明星恋情曝光", "娱乐八卦") is False
    assert collect.is_hardware("今日天气晴", "多云转晴") is False


def test_is_hardware_case_insensitive():
    assert collect.is_hardware("geforce rtx 传闻", "") is True


def test_dedupe_by_link_removes_duplicates():
    items = [
        {"link": "https://a/1", "title": "A"},
        {"link": "https://a/1", "title": "A 重复"},
        {"link": "https://a/2", "title": "B"},
    ]
    result = collect.dedupe_by_link(items)
    assert [it["title"] for it in result] == ["A", "B"]


def test_dedupe_by_link_skips_empty_link():
    items = [
        {"link": "", "title": "无链接"},
        {"link": "https://a/3", "title": "C"},
    ]
    result = collect.dedupe_by_link(items)
    assert [it["title"] for it in result] == ["C"]
