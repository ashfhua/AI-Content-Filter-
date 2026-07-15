#!/usr/bin/env python3
"""
AI 筛选核心模块 —— 调用 LLM 逐篇阅读文章，基于用户兴趣画像打分、去重、生成摘要。
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml


def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_articles(input_path: str) -> list[dict]:
    with open(input_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_scoring_prompt(article: dict, profile: dict) -> str:
    """构建评分提示词 —— 这是 AI 发挥核心价值的环节。"""
    keywords = profile.get("keywords", [])
    interests = profile.get("interests", "")
    anti_keywords = profile.get("anti_keywords", [])

    content_snippet = article["content"][:3000]

    return f"""你是我的个人AI信息助理。请读取以下文章全文，基于我的兴趣画像做出判断。

【我的兴趣画像】
- 关注领域：{interests}
- 关键词：{", ".join(keywords)}
- 不感兴趣：{", ".join(anti_keywords)}

【文章信息】
- 标题：{article["title"]}
- 来源：{article["source"]}
- 发布日期：{article.get("published", "未知")}
- 全文内容：
{content_snippet}

请完成以下任务，仅输出 JSON，不要任何其它文字：

{{
  "score": 0到10之间的数字,
  "relevance_reason": "简短说明这篇文章为什么对我有价值（或没有），不超过100字",
  "summary": "3-5句核心观点摘要，如果score低于5则为空字符串",
  "category": "归类标签，如：技术/AI/效率/行业动态/无关",
  "action": "read_now（立刻读）| read_later（稍后读）| skip（跳过）",
  "key_takeaway": "如果我只能记住一句话，记住什么（score>7才填写）"
}}

评分标准：
- 8-10分：直接命中我的核心关注领域，不看会错过重要信息
- 5-7分：有一定参考价值但非紧急
- 0-4分：与我的兴趣无关或内容质量差

注意：
- 标题党文章即使标题吸引人，内容空洞也要打低分
- 注意区分"对我个人"的价值，不是文章质量本身
- 如果涉及我不感兴趣的领域但角度新颖，可以适度加分
"""


def simulate_ai_filter(article: dict, profile: dict) -> dict:
    """
    模拟 AI 筛选逻辑 —— 当没有真实 LLM API 时使用基于关键词的评分。
    在真实场景中，此函数应替换为调用 OpenAI / Claude / 本地模型 API。

    注意：此模拟仅用于演示和测试，真实场景中 AI 的语义理解远超关键词匹配。
    """
    title = article.get("title", "").lower()
    content = (article.get("content", "")[:2000]).lower()
    full_text = title + " " + content

    keywords = [k.lower() for k in profile.get("keywords", [])]
    anti_keywords = [k.lower() for k in profile.get("anti_keywords", [])]

    # 关键词命中
    keyword_hits = sum(1 for kw in keywords if kw in full_text)
    anti_hits = sum(1 for ak in anti_keywords if ak in full_text)

    # 基于命中率的基础分
    base_score = min(10, keyword_hits * 2.5)
    # 反关键词惩罚
    penalty = anti_hits * 3
    score = max(0, min(10, base_score - penalty))

    # 根据分数生成反馈
    if score >= 8:
        action = "read_now"
        relevance = f"文章涵盖多个你关注的关键词，与你的兴趣高度匹配 (命中 {keyword_hits} 个关键词)"
    elif score >= 5:
        action = "read_later"
        relevance = f"文章部分涉及你的关注领域 (命中 {keyword_hits} 个关键词)"
    elif anti_hits > 0:
        action = "skip"
        relevance = f"文章主要涉及你不感兴趣的领域"
    else:
        action = "skip"
        relevance = "文章与你的兴趣领域无显著关联"

    # 模拟摘要生成 (真实场景由 LLM 生成)
    summary = ""
    if score >= 5:
        sentences = [s.strip() for s in content.replace("\n", " ").split("。") if len(s.strip()) > 10]
        summary = "\n".join(f"{i+1}. {s}。" for i, s in enumerate(sentences[:4]))

    return {
        "score": round(score, 1),
        "relevance_reason": relevance,
        "summary": summary,
        "category": "技术" if keyword_hits >= 2 else "综合",
        "action": action,
        "key_takeaway": sentences[0] + "。" if score >= 7 and sentences else "",
    }


def detect_duplicates(articles: list[dict], threshold: float = 0.7) -> list[dict]:
    """简单去重：检测标题高度相似的文章。真实场景应由 AI 做语义相似度检测。"""
    seen_titles = set()
    unique = []
    for art in articles:
        title_simple = "".join(c for c in art["title"] if c.isalnum())
        if title_simple.lower() not in seen_titles:
            seen_titles.add(title_simple.lower())
            unique.append(art)
    return unique


def generate_report(filtered: list[dict], profile: dict) -> str:
    """生成 Markdown 格式日报。"""
    read_now = [a for a in filtered if a.get("ai_result", {}).get("action") == "read_now"]
    read_later = [a for a in filtered if a.get("ai_result", {}).get("action") == "read_later"]
    skipped = [a for a in filtered if a.get("ai_result", {}).get("action") == "skip"]

    lines = [
        f"# AI 信息日报",
        f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> 关注领域：{profile.get('interests', '未设置')}",
        f"> 共扫描 {len(filtered)} 篇文章",
        "",
        "---",
        "",
        f"## 🔴 重要 ({len(read_now)} 篇)",
        "",
    ]

    for art in read_now:
        r = art.get("ai_result", {})
        lines.append(f"### [{art['title']}]({art['url']})")
        lines.append(f"**评分：{r.get('score', 'N/A')}/10** | 来源：{art['source']}  | 归类：{r.get('category', 'N/A')}")
        lines.append(f"> {r.get('relevance_reason', '')}")
        if r.get("key_takeaway"):
            lines.append(f"💡 **要点**：{r['key_takeaway']}")
        lines.append(f"摘要：\n{r.get('summary', '无')}")
        lines.append("")

    lines.append(f"## 🟡 可读 ({len(read_later)} 篇)")
    lines.append("")
    for art in read_later:
        r = art.get("ai_result", {})
        lines.append(f"- [{art['title']}]({art['url']}) — {r.get('score', 'N/A')}分 | {art['source']}")
    lines.append("")

    lines.append(f"## ⚪ 已跳过 ({len(skipped)} 篇)")
    lines.append("")
    for art in skipped[:10]:
        r = art.get("ai_result", {})
        lines.append(f"- ~~{art['title']}~~ — {r.get('relevance_reason', '')}")
    if len(skipped) > 10:
        lines.append(f"- ... 等共 {len(skipped)} 篇")
    lines.append("")

    lines.extend([
        "---",
        f"*由 AI 信息筛选器自动生成 · {datetime.now().strftime('%Y-%m-%d')}*",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="AI 信息筛选器")
    parser.add_argument("--input", required=True, help="输入 JSON 文件 (fetcher 的输出)")
    parser.add_argument("--config", required=True, help="配置文件路径 (YAML)")
    parser.add_argument("--output", default="data/filtered.json", help="输出 JSON 路径")
    parser.add_argument("--report", action="store_true", help="生成 Markdown 日报")
    parser.add_argument("--api-key", help="LLM API Key (可选，不提供则使用模拟模式)")
    parser.add_argument("--api-base", help="LLM API Base URL")
    parser.add_argument("--model", default="gpt-4o-mini", help="模型名称")
    args = parser.parse_args()

    config = load_config(args.config)
    profile = config.get("profile", {})
    articles = load_articles(args.input)

    print(f"[INFO] 开始筛选 {len(articles)} 篇文章...")

    # 去重
    articles = detect_duplicates(articles)
    print(f"[INFO] 去重后剩余 {len(articles)} 篇")

    # AI 评分 (使用模拟模式演示)
    use_real_ai = bool(args.api_key)

    for i, art in enumerate(articles):
        if use_real_ai:
            # TODO: 调用真实 LLM API
            # response = openai.ChatCompletion.create(
            #     model=args.model,
            #     messages=[{"role": "user", "content": build_scoring_prompt(art, profile)}],
            # )
            # result = json.loads(response.choices[0].message.content)
            pass
        else:
            print(f"  [{i+1}/{len(articles)}] 模拟评分: {art['title'][:40]}...")
            result = simulate_ai_filter(art, profile)

        art["ai_result"] = result

    # 按评分降序
    articles.sort(key=lambda x: x.get("ai_result", {}).get("score", 0), reverse=True)

    # 保存筛选结果
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    # 统计
    read_now = sum(1 for a in articles if a.get("ai_result", {}).get("action") == "read_now")
    read_later = sum(1 for a in articles if a.get("ai_result", {}).get("action") == "read_later")
    skipped = sum(1 for a in articles if a.get("ai_result", {}).get("action") == "skip")
    print(f"\n[DONE] 筛选完成:")
    print(f"  🔴 重要: {read_now} 篇")
    print(f"  🟡 可读: {read_later} 篇")
    print(f"  ⚪ 跳过: {skipped} 篇")
    print(f"  结果保存至: {output_path}")

    # 生成日报
    if args.report:
        report = generate_report(articles, profile)
        report_path = Path(args.output).parent / "daily_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"  日报保存至: {report_path}")


if __name__ == "__main__":
    main()
