# AI 信息筛选器 — 使用指南

## 快速上手

### 前置依赖

```bash
pip install feedparser openai httpx pyyaml rich
```

### 三步开始使用

```bash
# 第1步：编辑订阅源和兴趣画像
vim skill/references/sources.yaml

# 第2步：抓取最新文章
python skill/scripts/fetcher.py --config skill/references/sources.yaml --output data/feeds.json

# 第3步：AI 筛选 + 生成日报
python skill/scripts/filter.py \
  --input data/feeds.json \
  --config skill/references/sources.yaml \
  --output data/filtered.json \
  --report
```

## 工作流程详解

```
                   ┌──────────────┐
                   │  sources.yaml │  ← 你配置的订阅源 + 兴趣画像
                   └──────┬───────┘
                          │
                   ┌──────▼───────┐
                   │  fetcher.py   │  ← 抓取 RSS，标准化输出
                   └──────┬───────┘
                          │  feeds.json
                   ┌──────▼───────┐
                   │  filter.py    │  ← AI 逐篇阅读、评分、去重、摘要
                   └──────┬───────┘
                          │  filtered.json
                   ┌──────▼───────┐
                   │  日报生成      │  ← Markdown 格式，按重要性分级
                   └──────────────┘
```

## 配置订阅源

### RSS 源

大部分博客和新闻网站都提供 RSS。找 RSS 的方法：
- 网站底部通常有 RSS 图标链接
- 在网址后加 `/rss`、`/feed`、`/atom.xml` 试试
- 使用 [RSSHub](https://rsshub.app/) 为不提供 RSS 的网站生成源

配置示例：
```yaml
sources:
  - name: "我的博客"
    url: "https://example.com/feed.xml"
    type: rss
    enabled: true
```

### 启用/禁用源

设置 `enabled: false` 可临时关闭某个源，无需删除配置。

## 兴趣画像调优建议

### 关键词设置技巧
- **不要太泛**：如"技术"会匹配几乎所有内容
- **不要太窄**：如一个特定的库名可能匹配太少
- **适度组合**：3-15 个关键词效果最好

### 反关键词
- 用于排除确定不感兴趣的主题
- 例如你不关注区块链，加上相关关键词 AI 会自动降低评分

### 自然语言兴趣描述
这是最关键的配置项。AI 会做语义级理解，不需要精确匹配关键词。
尽量用完整的自然语言描述你真正关心的东西。

## 真实 AI vs 模拟模式

### 模拟模式（默认）
不配置 API Key 时，使用基于关键词匹配的模拟评分。适合测试流程。

### 真实 AI 模式
设置环境变量后使用：
```bash
export OPENAI_API_KEY="sk-xxxxx"
export OPENAI_API_BASE="https://api.openai.com/v1"  # 或用代理地址

python skill/scripts/filter.py \
  --input data/feeds.json \
  --config skill/references/sources.yaml \
  --api-key "$OPENAI_API_KEY" \
  --api-base "$OPENAI_API_BASE" \
  --model "gpt-4o-mini" \
  --report
```

真实 AI 相比模拟模式的核心优势：
1. 语义理解，不受关键词字面限制
2. 识别标题党（标题吸引人但内容空洞）
3. 跨领域联想（文章没提到你的关键词但确实相关）
4. 更精准的摘要生成

## 日报解读

日报按重要性分三级：

| 标记 | 含义 | 行动建议 |
|------|------|----------|
| 🔴 重要 | 8-10 分，直接命中核心关注 | 立即阅读 |
| 🟡 可读 | 5-7 分，有一定参考价值 | 有空再看 |
| ⚪ 跳过 | 0-4 分，无关或质量差 | 无需关注 |

## 最佳实践

1. **每天定时运行**：建议通过 cron / 定时任务每天固定时间运行
2. **每周复盘调整**：根据推送质量调整关键词和兴趣描述
3. **控制信息源数量**：5-10 个高质量源 > 50 个低质量源
4. **结合人工反馈**：如果你发现 AI 经常误判某类文章，更新反关键词
5. **不要完全依赖筛选**：AI 是辅助，偶尔手动浏览一下原始源，发现 AI 可能漏掉的新方向
