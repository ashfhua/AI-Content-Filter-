# AI 信息筛选器 (AI Content Filter)

> 智能信息筛选 Skill —— 订阅公开信息源，由 AI 逐篇阅读全文并判断对你是否有价值，提炼核心观点推送。

## 选题来源

选题来自「AI个人系统实践」课程 `AI实践场景清单.xlsx` 第 20 号题目：**AI 信息筛选器**。

## 一句话简介

关注太多信息源？刷 App 浪费时间？被标题党骗点击？这个工具帮你自动筛选：订阅公开源 → AI 逐篇阅读全文 → 判断对你有没有价值 → 提炼核心观点 → 只推送精华。

## 为什么必须用 AI？

传统 RSS 阅读器只能做关键词匹配标题，而 AI 信息筛选器能做到：

- **全文阅读**：AI 逐字阅读文章全文，而不是只看标题
- **语义理解**：理解你真正的兴趣，不需要精确关键词匹配
- **标题党识别**：读完内容再判断，标题党无处遁形
- **智能摘要**：高价值文章自动提炼 3-5 句核心观点
- **个性化**：越用越懂你，评分准度持续提升

**没有 LLM 级别的文本理解能力，以上任何一条都做不到。**

## 项目结构

```
AI信息筛选器/
├── skill/
│   ├── SKILL.md                   # Skill 定义文件
│   ├── scripts/
│   │   ├── fetcher.py             # RSS 信息源抓取模块
│   │   └── filter.py              # AI 筛选核心模块
│   └── references/
│       ├── sources.yaml           # 订阅源 + 兴趣画像配置示例
│       └── usage_guide.md         # 详细使用指南
├── data/
│   ├── sample_feeds.json          # 测试用 RSS 样例数据
│   └── test_output.json           # 预期筛选输出
├── tests/
│   └── test_record.md             # 测试记录（5 个测试用例）
├── iteration/
│   └── iteration_log.md           # 5 个后续迭代方向
└── README.md
```

## 快速上手

```bash
# 1. 安装依赖
pip install feedparser openai httpx pyyaml rich

# 2. 编辑你的订阅源和兴趣画像
vim skill/references/sources.yaml

# 3. 抓取最新文章
python skill/scripts/fetcher.py --config skill/references/sources.yaml --output data/feeds.json

# 4. AI 筛选 + 生成日报
python skill/scripts/filter.py \
  --input data/feeds.json \
  --config skill/references/sources.yaml \
  --output data/filtered.json \
  --report
```

## 技术栈

- **抓取**：feedparser + httpx
- **AI**：OpenAI 兼容 API（支持任意 LLM，默认包含模拟模式）
- **配置**：YAML
- **输出**：JSON + Markdown 日报

## 后续迭代

详见 `iteration/iteration_log.md`，包含 5 个方向的详细计划：

1. 真实 LLM 接入 + 语义理解升级
2. 多模态内容支持（视频/播客/论文）
3. 个性化学习 + 反馈闭环
4. 团队/社群共享筛选
5. 定时任务 + 多渠道推送
