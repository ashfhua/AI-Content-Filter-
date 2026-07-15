---
name: ai-content-filter
description: >
  智能信息筛选器 —— 订阅公开信息源（RSS/Blog/公众号），
  由 AI 逐篇阅读全文并判断对你是否有价值，提炼核心观点推送，
  帮你从信息洪流中解放注意力。
version: 1.0.0
author: ashfhua
triggers:
  - 信息筛选
  - 信息过滤
  - 内容筛选
  - RSS筛选
  - 订阅筛选
  - 信息过载
  - 筛选有价值文章
  - content filter
---

# AI 信息筛选器 (AI Content Filter)

## 一句话简介

关注太多信息源？刷 App 浪费时间？被标题党骗点击？这个 Skill 帮你**自动筛选**：订阅公开源 → AI 逐篇阅读全文 → 判断对你有没有价值 → 提炼核心观点 → 推送给你的只有精华。

## 为什么必须用 AI？

| 传统 RSS 阅读器 | AI 信息筛选器 |
|---|---|
| 只做关键词匹配标题 | AI 逐篇**读懂全文** |
| 标题党一样推给你 | 读完内容再判断，标题党无处遁形 |
| 不了解你的兴趣深度 | 基于你的兴趣画像做**语义级相关性判断** |
| 所有文章一视同仁 | 给每篇文章打分 + 理由，你只看最重要那几篇 |
| 看完还要自己总结 | AI 直接提炼核心观点，3 句话了解全文 |

**没有 LLM 级别的文本理解能力，以上任何一条都做不到。这就是 AI 的核心价值。**

## 核心功能

1. **订阅源管理**：支持 RSS/Atom 源、静态网页列表等
2. **AI 全文阅读与评分**：每篇文章由 AI 逐字阅读，基于用户兴趣画像打分（0-10）
3. **核心观点提炼**：高价值文章自动生成 3-5 句核心观点摘要
4. **去重检测**：跨信息源检测重复/高度相似内容
5. **日报生成**：每日汇总有价值文章，Markdown 格式推送

## 安装与依赖

```bash
pip install feedparser openai httpx pyyaml rich
```

## 使用方式

### 1. 配置订阅源

编辑 `references/sources.yaml`，填入你想要订阅的信息源：

```yaml
sources:
  - name: "阮一峰的网络日志"
    url: "https://feeds.feedburner.com/ruanyifeng"
    type: rss
  - name: "Hacker News Top"
    url: "https://hnrss.org/frontpage"
    type: rss
```

### 2. 配置你的兴趣画像

编辑 `references/sources.yaml` 中的 `profile` 部分，告诉 AI 你关心什么：

```yaml
profile:
  keywords: ["AI", "大模型", "Python", "数据分析"]
  interests: "AI Agent 开发、RAG 技术、开源项目、独立开发"
  anti_keywords: ["区块链", "加密货币", "NFT"]
```

### 3. 运行筛选

```bash
# 抓取所有订阅源的最新文章
python scripts/fetcher.py --config references/sources.yaml --output data/feeds.json

# AI 筛选 + 评分
python scripts/filter.py --input data/feeds.json --config references/sources.yaml --output data/filtered.json

# 生成每日报告
python scripts/filter.py --input data/feeds.json --config references/sources.yaml --report
```

### 4. 查看结果

筛选结果 JSON 示例：

```json
{
  "article": "GPT-5 发布：多模态能力大幅提升",
  "score": 9.2,
  "relevance_reason": "与你关注的 AI Agent 开发直接相关，GPT-5 的 tool-use 能力是 Agent 的核心基础设施",
  "summary": "1. GPT-5 在工具调用准确率上提升 40%\n2. 新增原生多模态输入支持\n3. API 成本降低 60%"
}
```

## 配置文件说明

| 文件 | 说明 |
|---|---|
| `scripts/fetcher.py` | 信息源抓取模块，支持 RSS/Atom |
| `scripts/filter.py` | AI 筛选核心模块，调用 LLM 进行内容理解和评分 |
| `references/sources.yaml` | 订阅源配置 + 用户兴趣画像 |
| `references/usage_guide.md` | 详细使用指南 |

## 适用场景

- 技术从业者跟踪行业动态
- 研究人员筛选领域论文
- 任何被信息过载困扰的人

## 后续迭代方向

详见 `iteration/iteration_log.md`。
