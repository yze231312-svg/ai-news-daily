#!/usr/bin/env python3
"""
AI News Daily - 多源资讯聚合
分类：模型发布、工具平台、研究成果、开源项目、行业动态
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
        "name_en": "Model Releases",
        "sources": [
            {"name": "HuggingFace", "url": "https://huggingface.co/api/models?sort=downloads&direction=-1&limit=30&filter=featured", "type": "api"},
            {"name": "OpenAI", "url": "https://feeds.feedburner.com/OpenAi", "type": "rss"},
            {"name": "Anthropic", "url": "https://www.anthropic.com/rss.xml", "type": "rss"},
            {"name": "Google AI", "url": "https://developers.googleblog.com/feeds/posts/default?alt=rss", "type": "rss"},
            {"name": "Meta AI", "url": "https://ai.meta.com/blog/rss.xml", "type": "rss"},
        ],
        "keywords": ["gpt", "claude", "gemini", "llama", "model", "release", "openai", "anthropic", "google deepmind", "mistral"]
    },
    "tool": {
        "name": "🛠️ 工具平台",
        "name_en": "Tools & Platforms",
        "sources": [
            {"name": "Product Hunt", "url": "https://www.producthunt.com/category/artificial-intelligence/feed", "type": "rss"},
            {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed", "type": "rss"},
            {"name": "Vercel", "url": "https://vercel.com/blog/rss.xml", "type": "rss"},
        ],
        "keywords": ["tool", "platform", "api", "sdk", "launch", "feature", "announcement", "release", "new"]
    },
    "research": {
        "name": "📚 研究成果",
        "name_en": "Research Papers",
        "sources": [
            {"name": "ArXiv AI", "url": "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=-1&limit=30", "type": "arxiv"},
            {"name": "ArXiv ML", "url": "http://export.arxiv.org/api/query?search_query=cat:cs.LG&sortBy=submittedDate&sortOrder=-1&limit=20", "type": "arxiv"},
        ],
        "keywords": ["paper", "research", "arxiv", "study", "benchmark", "performance", "accuracy", "state-of-the-art"]
    },
    "opensource": {
        "name": "📦 开源项目",
        "name_en": "Open Source",
        "sources": [
            {"name": "GitHub Python", "url": "https://github.com/trending/python?since=daily", "type": "github"},
            {"name": "GitHub JavaScript", "url": "https://github.com/trending/javascript?since=daily", "type": "github"},
            {"name": "GitHub Star", "url": "https://github.com/trending?since=daily", "type": "github"},
        ],
        "keywords": ["github", "stars", "repository", "repo", "github.com"]
    },
    "industry": {
        "name": "📰 行业动态",
        "name_en": "Industry News",
        "sources": [
            {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/", "type": "rss"},
            {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/", "type": "rss"},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "type": "rss"},
            {"name": "Wired", "url": "https://www.wired.com/feed/tag/ai/latest/rss", "type": "rss"},
        ],
        "keywords": ["ai", "artificial intelligence", "chatgpt", "openai", "microsoft", "google", "amazon", "meta", "nvidia", "startup"]
    }
}

def fetch_rss(url, source_name):
    """获取 RSS 订阅源"""
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:15]:
            tags = [tag.term for tag in entry.tags] if hasattr(entry, 'tags') else []
            if not tags and hasattr(entry, 'categories'):
                tags = entry.categories
            
            articles.append({
                "title": entry.title,
                "url": entry.link,
                "source": source_name,
                "date": entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                "summary": entry.summary[:200] + "..." if hasattr(entry, 'summary') else "",
                "tags": tags[:5]
            })
        return articles
    except Exception as e:
        print(f"  ⚠️ RSS 错误 {source_name}: {e}")
        return []

def fetch_github_trending(url, source_name):
    """获取 GitHub Trending"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        articles = []
        
        # 简化解析
        lines = response.text.split('\n')
        in_repo = False
        for line in lines:
            if 'article class="Box-row"' in line:
                in_repo = True
                repo_data = {'title': '', 'url': '', 'desc': ''}
            elif in_repo:
                if 'href="/' in line and 'class="Link' in line:
                    match = re.search(r'href="([^"]+)"[^>]*>([^<]+)</a>', line)
                    if match:
                        repo_data['url'] = 'https://github.com' + match.group(1)
                        repo_data['title'] = match.group(2).strip()
                elif '<p class="col-' in line:
                    desc = re.sub(r'<[^>]+>', '', line).strip()
                    repo_data['desc'] = desc[:200] if desc else ''
                elif '</article>' in line:
                    in_repo = False
                    if repo_data['title']:
                        articles.append({
                            "title": repo_data['title'],
                            "url": repo_data['url'],
                            "source": "GitHub",
                            "date": datetime.now().isoformat(),
                            "summary": repo_data['desc'],
                            "tags": ["GitHub", "Trending"]
                        })
        
        return articles[:10]
    except Exception as e:
        print(f"  ⚠️ GitHub 错误: {e}")
        return []

def fetch_arxiv(url, source_name):
    """获取 ArXiv 论文"""
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:15]:
            arxiv_id = entry.id.split('/abs/')[-1] if '/abs/' in entry.id else entry.id
            pdf_url = entry.link.replace('/abs/', '/pdf/') if '/abs/' in entry.link else entry.link
            
            tags = []
            if hasattr(entry, 'tags'):
                for tag in entry.tags:
                    if tag.term:
                        tags.append(tag.term)
            
            articles.append({
                "title": entry.title,
                "url": pdf_url,
                "source": "arXiv",
                "date": entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                "summary": entry.summary[:200] + "..." if hasattr(entry, 'summary') else "",
                "tags": tags[:5] if tags else ["AI", "Research"]
            })
        return articles
    except Exception as e:
        print(f"  ⚠️ ArXiv 错误: {e}")
        return []

def fetch_huggingface(url, source_name):
    """获取 HuggingFace 热门模型"""
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        articles = []
        
        for model in data[:30]:
            tags = model.get('tags', [])
            if 'transformers' in tags:
                tags = ['Transformers'] + [t for t in tags if t != 'transformers']
            elif 'diffusers' in tags:
                tags = ['Diffusion'] + [t for t in tags if t != 'diffusers']
            
            articles.append({
                "title": model.get('modelId', 'Unknown Model'),
                "url": f"https://huggingface.co/{model.get('modelId', '')}",
                "source": "HuggingFace",
                "date": datetime.now().isoformat(),
                "summary": f"Downloads: {model.get('downloads', 0):,} | Likes: {model.get('likes', 0):,}",
                "tags": tags[:5] if tags else ["Model", "AI"]
            })
        return articles
    except Exception as e:
        print(f"  ⚠️ HuggingFace 错误: {e}")
        return []

def classify_article(article, categories):
    """根据关键词对文章进行分类"""
    title = article.get('title', '').lower()
    summary = article.get('summary', '').lower()
    text = title + " " + summary
    
    scores = {}
    for cat_key, config in categories.items():
        score = 0
        for keyword in config.get('keywords', []):
            if keyword.lower() in text:
                score += 1
        scores[cat_key] = score
    
    if scores:
        best_cat = max(scores, key=scores.get)
        return best_cat if scores[best_cat] > 0 else None
    return None

def fetch_all_news():
    """获取所有新闻并分类"""
    all_articles = defaultdict(list)
    seen_urls = set()
    
    print("\n🚀 开始获取资讯...\n")
    
    for cat_key, config in CATEGORIES.items():
        print(f"📥 获取 {config['name']}...")
        
        for source in config['sources']:
            if source['type'] == 'rss':
                articles = fetch_rss(source['url'], source['name'])
            elif source['type'] == 'github':
                articles = fetch_github_trending(source['url'], source['name'])
            elif source['type'] == 'arxiv':
                articles = fetch_arxiv(source['url'], source['name'])
            elif source['type'] == 'api':
                articles = fetch_huggingface(source['url'], source['name'])
            else:
                articles = []
            
            for article in articles:
                if article['url'] in seen_urls:
                    continue
                seen_urls.add(article['url'])
                
                article['category'] = cat_key
                article['category_name'] = config['name']
                
                all_articles[cat_key].append(article)
        
        print(f"   ✓ {len(all_articles[cat_key])} 条")
    
    # 构建最终数据
    result = {
        "lastUpdate": datetime.now().strftime("%Y/%m/%d %H:%M"),
        "categories": [],
        "articles": []
    }
    
    for cat_key, config in CATEGORIES.items():
        category_data = {
            "key": cat_key,
            "name": config['name'],
            "name_en": config['name_en'],
            "count": len(all_articles[cat_key])
        }
        result['categories'].append(category_data)
        result['articles'].extend(all_articles[cat_key])
    
    # 按日期排序
    result['articles'].sort(key=lambda x: x['date'], reverse=True)
    
    return result

def main():
    data = fetch_all_news()
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 更新完成！")
    print(f"📊 总计: {len(data['articles'])} 条新闻")
    for cat in data['categories']:
        print(f"   {cat['name']}: {cat['count']} 条")

if __name__ == "__main__":
    main()
