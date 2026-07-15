#!/usr/bin/env python3
"""
信息源抓取模块 —— 支持 RSS/Atom 源的内容抓取与标准化输出。
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import feedparser
import httpx
import yaml


def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def fetch_rss(name: str, url: str, timeout: int = 15) -> list[dict]:
    """抓取单个 RSS/Atom 源，返回标准化文章列表。"""
    try:
        resp = httpx.get(url, timeout=timeout, follow_redirects=True)
        resp.raise_for_status()
    except Exception as e:
        print(f"[WARN] 抓取失败 {name} ({url}): {e}", file=sys.stderr)
        return []

    feed = feedparser.parse(resp.text)
    articles = []
    for entry in feed.entries:
        published = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc).isoformat()

        content = entry.get("content", [{}])[0].get("value", "") if entry.get("content") else ""
        if not content:
            content = entry.get("summary", entry.get("description", ""))

        articles.append({
            "source": name,
            "title": entry.get("title", "").strip(),
            "url": entry.get("link", ""),
            "published": published or datetime.now(timezone.utc).isoformat(),
            "content": _clean_html(content),
            "author": entry.get("author", ""),
        })
    return articles


def _clean_html(html_text: str) -> str:
    """简单去除 HTML 标签，保留纯文本。"""
    import re
    text = re.sub(r"<[^>]+>", "", html_text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def main():
    parser = argparse.ArgumentParser(description="信息源抓取器")
    parser.add_argument("--config", required=True, help="配置文件路径 (YAML)")
    parser.add_argument("--output", default="data/feeds.json", help="输出 JSON 文件路径")
    parser.add_argument("--source", help="仅抓取指定源名称")
    args = parser.parse_args()

    config = load_config(args.config)
    sources = config.get("sources", [])

    all_articles = []
    for src in sources:
        if args.source and src["name"] != args.source:
            continue
        src_type = src.get("type", "rss")
        print(f"[INFO] 抓取: {src['name']} ({src['url']})")
        if src_type == "rss":
            articles = fetch_rss(src["name"], src["url"])
        else:
            print(f"[WARN] 不支持的类型: {src_type}", file=sys.stderr)
            continue
        all_articles.extend(articles)
        print(f"  -> 获取 {len(articles)} 篇文章")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] 共抓取 {len(all_articles)} 篇文章，保存至 {output_path}")


if __name__ == "__main__":
    main()
