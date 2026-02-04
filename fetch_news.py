#!/usr/bin/env python3
"""
AI News Daily - 新闻抓取与总结脚本
自动从多个来源抓取 AI 资讯，用大模型总结成中文简报
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 尝试导入需要的库
try:
    import requests
except ImportError:
    print("❌ 请安装 requests: pip install requests")
    sys.exit(1)

# Tavily API Key (支持中文搜索)
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "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")
TAVILY_SEARCH_URL = "https://api.tavily.com/search"

# AI 新闻搜索关键词
SEARCH_QUERIES = [
    "artificial intelligence LLM model research breakthrough February 2026",
    "DeepSeek Claude GPT OpenAI news 2026",
    "AI coding assistant Cursor Copilot GitHub",
    "multimodal model vision language 2026",
    "AI agents autonomous workflow 2026",
    "machine learning research paper arxiv 2026",
    "Google Microsoft Anthropic AI product 2026",
    "local LLM quantization Ollama 2026"
]

# 新闻来源映射
SOURCE_MAP = {
    "github.com": "GITHUB",
    "news.ycombinator.com": "HN",
    "arxiv.org": "ARXIV",
    "techmeme.com": "TECHMEME",
    "venturebeat.com": "VENTUREBEAT",
    "techcrunch.com": "TECHCRUNCH",
    "thedecoder.com": "DECODER",
    "reddit.com": "REDDIT",
    "anthropic.com": "ANTHROPIC",
    "openai.com": "OPENAI",
    "google.com": "GOOGLE",
    "microsoft.com": "MICROSOFT"
}

# 每日金句
DAILY_QUOTES = [
    ("AI won't replace humans, but humans using AI will replace those who don't.", "Anonymous"),
    ("The best way to predict the future is to create it.", "Peter Drucker"),
    ("In the future, there will be two types of people: those who use AI, and those who are used by AI.", "Sam Altman"),
    ("AI is the new electricity. It will transform every industry.", "Andrew Ng"),
    ("Don't worry about AI taking your job. Worry about someone using AI to take your job.", "Anonymous"),
    ("The intersection of AI and human creativity is where magic happens.", "Fei-Fei Li"),
    ("The most powerful tool we have is imagination.", "Geoffrey Hinton")
]


def extract_source(url: str) -> str:
    """从 URL 提取来源"""
    try:
        from urllib.parse import urlparse
        hostname = urlparse(url).netloc.lower()
        for domain, source in SOURCE_MAP.items():
            if domain in hostname:
                return source
        # 默认处理
        return hostname.replace("www.", "").split(".")[0].upper()[:10]
    except:
        return "AI NEWS"


def format_date() -> str:
    """格式化日期"""
    return datetime.now().strftime("%Y/%m/%d")


def get_quote() -> dict:
    """获取每日金句"""
    import random
    today = datetime.now().day
    quote = DAILY_QUOTES[today % len(DAILY_QUOTES)]
    return {
        "text": quote[0],
        "author": quote[1]
    }


def search_news(query: str, max_results: int = 5) -> list:
    """使用 Tavily 搜索新闻"""
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": max_results,
        "include_domains": [
            "github.com",
            "news.ycombinator.com", 
            "arxiv.org",
            "techmeme.com",
            "venturebeat.com",
            "techcrunch.com",
            "anthropic.com",
            "openai.com",
            "google.com",
            "microsoft.com"
        ],
        "exclude_domains": ["facebook.com", "twitter.com", "x.com"]
    }
    
    try:
        response = requests.post(TAVILY_SEARCH_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except Exception as e:
        print(f"❌ 搜索失败 ({query[:30]}...): {e}")
        return []


def summarize_with_ai(articles: list) -> list:
    """
    用大模型总结文章（简化版：清理描述）
    完整版可以调用 OpenAI/Gemini API 进行智能总结
    """
    summarized = []
    
    for article in articles[:15]:  # 最多 15 条
        title = article.get("title", "").strip()
        url = article.get("url", "")
        content = article.get("content", "") or article.get("snippet", "")
        
        if not title:
            continue
        
        # 清理描述
        description = content[:300].strip()
        if description:
            # 去除多余空白和特殊字符
            import re
            description = re.sub(r'\s+', ' ', description)
            description = description.replace("#", "").replace("*", "")
        
        summarized.append({
            "title": title,
            "url": url,
            "description": description,
            "source": extract_source(url),
            "date": format_date()
        })
    
    return summarized


def save_to_json(articles: list, output_file: str = "data.json"):
    """保存到 JSON 文件"""
    # 新闻来源列表
    sources = [
        "📰 Hacker News (Y Combinator)",
        "💻 GitHub Trending", 
        "📄 ArXiv (cs.AI)",
        "📊 Techmeme",
        "📈 VentureBeat / TechCrunch",
        "🎯 The Decoder",
        "💬 Reddit (r/ML, r/LocalLLaMA)"
    ]
    
    data = {
        "articles": articles,
        "lastUpdate": datetime.now().strftime("%Y/%m/%d %H:%M"),
        "sources": sources
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存 {len(articles)} 条新闻到 {output_file}")


def update_html_quote():
    """更新 HTML 页面的金句"""
    quote = get_quote()
    quote_js = f'''
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const quotes = [
                {{ text: "{quote['text']}", author: "{quote['author']}" }}
            ];
            const today = new Date().getDate();
            const q = quotes[today % quotes.length];
            document.getElementById('quote-text').textContent = '"' + q.text + '"';
            document.getElementById('quote-author').textContent = '— ' + q.author;
        }});
    </script>
'''
    return quote_js


def main():
    """主函数"""
    print("🤖 AI News Daily - 开始抓取新闻...")
    print("=" * 50)
    
    # 搜索所有查询
    all_articles = []
    
    for i, query in enumerate(SEARCH_QUERIES, 1):
        print(f"🔍 [{i}/{len(SEARCH_QUERIES)}] 搜索: {query[:40]}...")
        results = search_news(query, max_results=3)
        all_articles.extend(results)
        print(f"   → 获取 {len(results)} 条结果")
    
    print("=" * 50)
    print(f"📊 共获取 {len(all_articles)} 条原始新闻")
    
    # 去重
    seen = set()
    unique_articles = []
    for article in all_articles:
        key = article.get("url", article.get("title", ""))
        if key and key not in seen:
            seen.add(key)
            unique_articles.append(article)
    
    print(f"🔗 去重后剩 {len(unique_articles)} 条")
    
    # 总结
    print("📝 正在总结...")
    summarized = summarize_with_ai(unique_articles)
    print(f"✅ 总结完成，共 {len(summarized)} 条")
    
    # 保存
    output_file = os.environ.get("OUTPUT_FILE", "data.json")
    save_to_json(summarized, output_file)
    
    # 打印统计
    sources_count = {}
    for article in summarized:
        source = article["source"]
        sources_count[source] = sources_count.get(source, 0) + 1
    
    print("\n📊 来源统计:")
    for source, count in sorted(sources_count.items(), key=lambda x: -x[1]):
        print(f"   {source}: {count}")
    
    print("\n🎉 完成！数据已保存，可推送到 GitHub")


if __name__ == "__main__":
    main()
