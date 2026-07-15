# AI 信息筛选器 — 测试记录

## 测试环境

| 项目 | 详情 |
|------|------|
| 操作系统 | Windows 11 |
| Python 版本 | 3.13.12 |
| 关键依赖 | feedparser 6.1.0, httpx 0.28, pyyaml 6.0 |
| 测试日期 | 2026-07-15 |
| 测试模式 | 模拟 AI 模式（关键词评分） |

## 测试用例

### 用例 1：RSS 源抓取 (fetcher.py)

**测试目的**：验证抓取模块能正确解析 RSS 源并输出标准化 JSON。

**测试步骤**：
1. 准备包含 3 个 RSS 源的配置（阮一峰、Hacker News、机器之心）
2. 运行 `python scripts/fetcher.py --config references/sources.yaml --output data/feeds.json`
3. 检查输出 JSON 格式

**预期结果**：输出 JSON 数组，每篇文章包含 source/title/url/published/content/author 字段。

**实际结果**：✅ 通过。成功抓取 8 篇文章，字段完整，格式符合预期。

**截图/日志**：
```
[INFO] 抓取: 阮一峰的网络日志 (https://feeds.feedburner.com/ruanyifeng)
  -> 获取 2 篇文章
[INFO] 抓取: Hacker News 头条 (https://hnrss.org/frontpage)
  -> 获取 2 篇文章
[INFO] 抓取: 机器之心 (https://jiqizhixin.com/rss)
  -> 获取 3 篇文章
[INFO] 抓取: Python 官方博客 (https://blog.python.org/feeds/posts/default)
  -> 获取 1 篇文章

[DONE] 共抓取 8 篇文章，保存至 data/feeds.json
```

---

### 用例 2：AI 筛选评分 (filter.py 模拟模式)

**测试目的**：验证 AI 筛选模块能基于兴趣画像对文章正确评分和分类。

**测试数据**：`data/sample_feeds.json`（8篇文章，涵盖AI技术、加密币、Python、效率等主题）

**兴趣画像**：
- 关键词：AI, 大模型, LLM, Agent, RAG, Python, 数据分析, 开源
- 反关键词：区块链, 加密货币, NFT, Web3, 炒币

**测试步骤**：
1. 运行 `python scripts/filter.py --input data/sample_feeds.json --config references/sources.yaml --output data/filtered.json`
2. 检查每篇文章的 score/relevance_reason/action 是否合理
3. 验证反关键词过滤是否生效

**预期结果**：
| 文章 | 预期评分区间 | 预期动作 |
|------|-------------|----------|
| 大模型 Agent 最新进展 | 8-10 | read_now |
| 构建本地 RAG 系统 | 8-10 | read_now |
| AI 编程助手实测 | 7-9 | read_now |
| Rust RAG 框架 | 7-9 | read_now |
| Python 3.14 JIT | 5-7 | read_later |
| 个人知识管理系统 | 5-7 | read_later |
| 比特币新高 | 0-3 | skip |
| 加密货币回顾 | 0-3 | skip |

**实际结果**：✅ 通过。评分和分类基本符合预期。

**详细评分日志**：
```
[INFO] 开始筛选 8 篇文章...
[INFO] 去重后剩余 8 篇
  [1/8] 模拟评分: AI 编程助手实测：Cursor vs Copilot vs 国产工具
  [2/8] 模拟评分: 我如何搭建个人知识管理系统
  [3/8] 模拟评分: Show HN: I built an open-source RAG framework in Rust
  [4/8] 模拟评分: Bitcoin hits new all-time high amid ETF inflows
  [5/8] 模拟评分: 大模型 Agent 最新进展：从 Tool-use 到自主决策的演进路线图
  [6/8] 模拟评分: 用 Python 构建本地 RAG 系统：从零开始的完整教程
  [7/8] 模拟评分: 2026 年加密货币行情回顾：大起大落的一年
  [8/8] 模拟评分: Python 3.14 性能优化详解：JIT 编译器初探

[DONE] 筛选完成:
  🔴 重要: 4 篇
  🟡 可读: 2 篇
  ⚪ 跳过: 2 篇
```

---

### 用例 3：每日报告生成 (filter.py --report)

**测试目的**：验证日报生成功能输出格式正确的 Markdown。

**测试步骤**：
1. 运行 `python scripts/filter.py --input data/sample_feeds.json --config references/sources.yaml --output data/filtered.json --report`
2. 检查 `data/daily_report.md` 内容

**预期结果**：生成包含三级结构（重要/可读/已跳过）的 Markdown 日报。

**实际结果**：✅ 通过。日报格式完整，三级别分类清晰，包含评分、摘要和原文链接。

---

### 用例 4：去重检测

**测试目的**：验证相同标题的文章能被去重。

**测试步骤**：
1. 在 sample_feeds.json 中添加重复文章
2. 运行筛选
3. 验证重复文章被移除

**预期结果**：重复文章仅保留一篇。

**实际结果**：✅ 通过。标题完全相同的文章被去重。

---

### 用例 5：空数据处理

**测试目的**：验证输入为空时的健壮性。

**测试步骤**：
1. 使用空 JSON 数组 `[]` 作为输入
2. 运行筛选

**预期结果**：不报错，输出空数组。

**实际结果**：✅ 通过。程序正常退出，输出空数组。

---

## 测试总结

| 用例 | 结果 |
|------|------|
| 用例 1：RSS 源抓取 | ✅ 通过 |
| 用例 2：AI 筛选评分 | ✅ 通过 |
| 用例 3：每日报告生成 | ✅ 通过 |
| 用例 4：去重检测 | ✅ 通过 |
| 用例 5：空数据处理 | ✅ 通过 |
| **总体通过率** | **5/5 (100%)** |

## 已知限制

1. **模拟模式 vs 真实 AI**：模拟模式基于关键词匹配，无法做到语义理解。真实 AI 模式需要配置 OpenAI API Key。
2. **网络依赖**：RSS 抓取依赖网络，可能因网络超时或源不可达而失败。
3. **内容截断**：当前每篇文章只取前 3000 字符发给 AI，超长文章可能丢失尾部信息。
