# 🤖 AI News Daily

每天自动更新的 AI 资讯聚合网站。

## ✨ 特点

- 🤖 自动抓取全球 AI 资讯
- 📰 聚合 Hacker News、GitHub Trending、ArXiv、Techmeme 等来源
- 🕐 每天早上 8 点自动更新
- 🚀 一键部署到 Vercel
- 📱 响应式设计，支持手机和电脑

## 📊 数据来源

- 📰 Hacker News (Y Combinator)
- 💻 GitHub Trending
- 📄 ArXiv (cs.AI)
- 📊 Techmeme
- 📈 VentureBeat / TechCrunch
- 🎯 The Decoder
- 💬 Reddit (r/ML, r/LocalLLaMA)

## 🚀 快速部署

### 方式一：Vercel（推荐）

1.Fork 本仓库

2.登录 [Vercel](https://vercel.com)

3.点击 "Import Project"，选择你的 fork 仓库

4.点击 "Deploy"，等待部署完成

5.访问生成的链接即可

### 方式二：本地运行

```bash
# 克隆仓库
git clone https://github.com/你的用户名/ai-news-daily.git
cd ai-news-daily

# 安装依赖
pip install requests

# 运行抓取脚本
python fetch_news.py

# 启动本地服务器（需要安装 Node.js）
npx serve .
```

## ⚙️ 配置

### Tavily API Key

本项目使用 Tavily API 搜索 AI 新闻。

1.获取 Tavily API Key: https://tavily.com/

2.在 GitHub 仓库中添加 secret：
   - 进入 Settings → Secrets and variables → Actions
   - 添加 `TAVILY_API_KEY`

### GitHub Actions

自动更新工作流已配置：
- 每天早上 8 点自动运行
- 抓取最新 AI 新闻
- 自动提交并推送到仓库

## 📁 项目结构

```
ai-news-daily/
├── index.html          # 前端页面
├── data.json           # 新闻数据（自动生成）
├── fetch_news.py       # 新闻抓取脚本
├── README.md           # 说明文档
└── .github/
    └── workflows/
        └── update.yml  # GitHub Actions 工作流
```

## 🎨 自定义

### 每日金句

编辑 `fetch_news.py` 中的 `DAILY_QUOTES` 列表

### 搜索关键词

编辑 `fetch_news.py` 中的 `SEARCH_QUERIES` 列表

### 样式

编辑 `index.html` 中的 CSS 样式

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📝 许可证

MIT License

---

Made with 🤖 by OpenClaw
