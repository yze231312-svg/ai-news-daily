#!/usr/bin/env python3
"""
AI News Daily - 多源资讯聚合
"""

import json
import feedparser
import requests
import re
from datetime import datetime
from collections import defaultdict

# 分类配置
CATEGORIES = {
    "model": {
        "name": "🗣️ 模型发布",
        "keywords": ["gpt", "claude", "gemini", "llama", "model", "release", "openai", "anthropic", "mistral"]
    },
    "tool": {
        "name": "🛠️ 工具平台",
        "keywords": ["tool", "platform", "api", "sdk", "launch", "feature", "announcement"]
    },
    "research": {
        "name": "📚 研究成果",
        "keywords": ["paper", "research", "arxiv", "study", "benchmark", "accuracy", "state-of-the-art"]
    },
    "opensource": {
        "name": "📦 开源项目",
        "keywords": ["github", "stars", "repository", "repo", "open source"]
    },
    "industry": {
        "name": "📰 行业动态",
        "keywords": ["ai", "microsoft", "google", "amazon", "meta", "nvidia", "startup"]
    }
}

SOURCES = [
    {"name": "HuggingFace", "url": "https://huggingface.co/api/models?sort=downloads&direction=-1&limit=30&filter=featured", "type": "huggingface"},
    {"name": "arXiv AI", "url": "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=-1&limit=25", "type": "arxiv"},
    {"name": "arXiv ML", "url": "http://export.arxiv.org/api/query?search_query=cat:cs.LG&sortBy=submittedDate&sortOrder=-1&limit=20", "type": "arxiv"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/", "type": "rss"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed", "type": "rss"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/", "type": "rss"},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "type": "rss"},
    {"name": "Product Hunt", "url": "https://www.producthunt.com/category/artificial-intelligence/feed", "type": "rss"},
]

def fetch_huggingface(url, source_name):
    try:
        resp = requests.get(url, timeout=15)
        data = resp.json()
        articles = []
        for m in data[:25]:
            articles.append({
                "title": m.get('modelId', 'Unknown'),
                "url": f"https://huggingface.co/{m.get('modelId', '')}",
                "source": "HuggingFace",
                "date": datetime.now().isoformat(),
                "summary": f"Downloads: {m.get('downloads', 0):,} | Likes: {m.get('likes', 0):,}",
                "tags": ["Model", "AI"]
            })
        return articles
    except Exception as e:
        print(f"  ⚠️ HuggingFace: {e}")
        return []

def fetch_arxiv(url, source_name):
    try:
        feed = feedparser.parse(url)
        articles = []
        for e in feed.entries[:20]:
            articles.append({
                "title": e.title,
                "url": e.link,
                "source": "arXiv",
                "date": e.published if hasattr(e, 'published') else datetime.now().isoformat(),
                "summary": e.summary[:200] + "..." if hasattr(e, 'summary') else "",
                "tags": ["Research", "AI"]
            })
        return articles
    except Exception as e:
        print(f"  ⚠️ arXiv: {e}")
        return []

def fetch_rss(url, source_name):
    try:
        feed = feedparser.parse(url)
        articles = []
        for e in feed.entries[:15]:
            articles.append({
                "title": e.title,
                "url": e.link,
                "source": source_name,
                "date": e.published if hasattr(e, 'published') else datetime.now().isoformat(),
                "summary": e.summary[:200] + "..." if hasattr(e, 'summary') else "",
                "tags": []
            })
        return articles
    except Exception as e:
        print(f"  ⚠️ {source_name}: {e}")
        return []

def fetch_github_trending():
    """抓取GitHub Trending"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get('https://github.com/trending?since=daily', headers=headers, timeout=15)
        articles = []
        
        # 简单解析
        pattern = r'<article[^>]*class="Box-row"[^>]*>.*?href="([^"]+)"[^>]*>([^<]+)</a>.*?<p[^>]*class="[^"]*"[^>]*>([^<]+)</p>'
        matches = re.findall(pattern, resp.text, re.DOTALL)
        
        for match in matches[:15]:
            url, title, desc = match
            articles.append({
                "title": title.strip(),
                "url": f"https://github.com{url}",
                "source": "GitHub",
                "date": datetime.now().isoformat(),
                "summary": desc.strip()[:200] if desc else "",
                "tags": ["GitHub", "Trending"]
            })
        return articles
    except Exception as e:
        print(f"  ⚠️ GitHub Trending: {e}")
        return []

def classify(article, categories):
    text = (article.get('title', '') + ' ' + article.get('summary', '')).lower()
    scores = {}
    for cat, config in categories.items():
        score = sum(1 for k in config.get('keywords', []) if k.lower() in text)
        scores[cat] = score
    if scores:
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else 'industry'
    return 'industry'

def fetch_all():
    all_articles = defaultdict(list)
    seen = set()
    
    print("\n🚀 开始获取资讯...\n")
    
    # RSS/API 源
    for src in SOURCES:
        print(f"📥 {src['name']}...", end=" ")
        if src['type'] == 'arxiv':
            arts = fetch_arxiv(src['url'], src['name'])
        elif src['type'] == 'huggingface':
            arts = fetch_huggingface(src['url'], src['name'])
        else:
            arts = fetch_rss(src['url'], src['name'])
        print(f"{len(arts)} 条")
        
        for a in arts:
            if a['url'] in seen:
                continue
            seen.add(a['url'])
            a['category'] = classify(a, CATEGORIES)
            a['category_name'] = CATEGORIES[a['category']]['name']
            all_articles[a['category']].append(a)
    
    # GitHub Trending
    print("📥 GitHub Trending...", end=" ")
    github_arts = fetch_github_trending()
    print(f"{len(github_arts)} 条")
    for a in github_arts:
        if a['url'] in seen:
            continue
        seen.add(a['url'])
        a['category'] = 'opensource'
        a['category_name'] = CATEGORIES['opensource']['name']
        all_articles['opensource'].append(a)
    
    # 构建结果
    result = {
        "lastUpdate": datetime.now().strftime("%Y/%m/%d %H:%M"),
        "categories": [],
        "articles": []
    }
    
    for cat, config in CATEGORIES.items():
        result['categories'].append({
            "key": cat,
            "name": config['name'],
            "count": len(all_articles[cat])
        })
        result['articles'].extend(all_articles[cat])
    
    result['articles'].sort(key=lambda x: x['date'], reverse=True)
    
    return result

def main():
    data = fetch_all()
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 更新完成！共 {len(data['articles'])} 条")
    for c in data['categories']:
        print(f"   {c['name']}: {c['count']} 条")

if __name__ == "__main__":
    main()
