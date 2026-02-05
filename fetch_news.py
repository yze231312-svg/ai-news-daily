#!/usr/bin/env python3
"""
AI News Daily - 每日人工智能资讯
支持中英文标题翻译
"""

import json
import feedparser
import requests
import re
from datetime import datetime
from collections import defaultdict

# 分类配置
CATEGORIES = {
    "model": {"name": "🗣️ 模型发布", "keywords": ["gpt", "claude", "gemini", "llama", "model", "release", "openai", "anthropic", "mistral", "moe", "parameter", "billion", "open-source model", "api", "version", "capability", "benchmark"]},
    "tutorial": {"name": "📖 使用教程", "keywords": ["tutorial", "guide", "how to", "getting started", "setup", "configuration", "integration", "api call", "prompt engineering", "opencl", "installation", "documentation", "example", "tips", "best practice"]},
    "tool": {"name": "🛠️ 工具平台", "keywords": ["tool", "platform", "api", "sdk", "launch", "feature", "announcement", "framework", "library", "studio", "plugin", "app", "software"]},
    "research": {"name": "📚 研究成果", "keywords": ["paper", "research", "arxiv", "study", "benchmark", "accuracy", "state-of-the-art", "sota", "performance", "training", "inference", "neural", "network", "learning", "dataset"]},
    "industry": {"name": "📰 行业动态", "keywords": ["ai", "microsoft", "google", "amazon", "meta", "nvidia", "startup", "funding", "valuation", "ipo", "acquisition", "partnership", "ceo", "executive", "company", "news"]}
}

# 翻译器
def translate_to_cn(text):
    """翻译成中文"""
    if not text or len(text) < 5:
        return text
    
    try:
        # 使用 MyMemory API（免费，无需 API Key）
        url = f"https://api.mymemory.translated.net/get?q={requests.utils.quote(text)}&langpair=en|zh-CN"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get('responseStatus') == 200:
            translated = data['responseData']['translatedText']
            if translated and translated != text:
                return translated
    except Exception as e:
        pass
    
    return text

SOURCES = [
    {"name": "GitHub Blog", "url": "https://github.blog/feed/", "type": "rss"},
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
            title = m.get('modelId', 'Unknown')
            articles.append({
                "title": translate_to_cn(title),
                "original_title": title,
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
            title = e.title
            articles.append({
                "title": translate_to_cn(title),
                "original_title": title,
                "url": e.link,
                "source": "arXiv",
                "date": e.published if hasattr(e, 'published') else datetime.now().isoformat(),
                "summary": translate_to_cn(e.summary[:200] + "...") if hasattr(e, 'summary') else "",
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
            title = e.title
            articles.append({
                "title": translate_to_cn(title),
                "original_title": title,
                "url": e.link,
                "source": source_name,
                "date": e.published if hasattr(e, 'published') else datetime.now().isoformat(),
                "summary": translate_to_cn(e.summary[:200] + "...") if hasattr(e, 'summary') else "",
                "tags": []
            })
        return articles
    except Exception as e:
        print(f"  ⚠️ {source_name}: {e}")
        return []

def classify(article, categories):
    # arXiv 来源的论文优先归类为研究成果
    if article.get('source') == 'arXiv':
        return 'research'
    
    text = (article.get('title', '') + ' ' + article.get('original_title', '') + ' ' + article.get('summary', '')).lower()
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
    
    for src in SOURCES:
        print(f"📥 {src['name']}...", end=" ", flush=True)
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
