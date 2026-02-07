#!/usr/bin/env python3
"""
AI News Daily - Twitter AI 资讯聚合后端
使用 Twitter MCP (via bird CLI) 抓取实时资讯
"""

import json
import os
import subprocess
import datetime
import random
import sys

# 分类配置与搜索查询
CATEGORIES = {
    "open_source": {
        "name": "🔓 开源项目",
        "query": "AI open source project (github.com OR huggingface.co) -is:retweet lang:en",
        "icon": "🔓"
    },
    "tutorial": {
        "name": "📖 AI 教程",
        "query": "AI tutorial guide how-to thread -is:retweet lang:en",
        "icon": "📖"
    },
    "model": {
        "name": "🤖 模型发布",
        "query": "new AI model release weights Llama Claude GPT -is:retweet lang:en",
        "icon": "🤖"
    },
    "free": {
        "name": "🆓 免费资源",
        "query": "free AI tool access credit API white-prostitute -is:retweet lang:zh",
        "icon": "🆓"
    },
    "tool": {
        "name": "🛠️ 实用工具",
        "query": "useful AI tool recommendation productivity -is:retweet lang:en",
        "icon": "🛠️"
    }
}

class TwitterFetcher:
    def __init__(self, use_mock=False):
        self.use_mock = use_mock
        self.bird_available = self._check_bird()

    def _check_bird(self):
        try:
            subprocess.run(["bird", "--version"], capture_output=True, check=True)
            return True
        except:
            return False

    def fetch(self, category_key, query):
        if self.use_mock or not self.bird_available:
            return self.generate_mock(category_key)
        
        try:
            # 执行 bird search 命令获取 JSON 格式结果
            # 注意：实际运行时需要 bird 已配置好 Twitter cookies
            result = subprocess.run(
                ["bird", "search", "--json", "--count", "10", query],
                capture_output=True, text=True, check=True
            )
            tweets = json.loads(result.stdout)
            return self.process_tweets(tweets, category_key)
        except Exception as e:
            print(f"  ⚠️ 抓取 {category_key} 失败: {e}. 使用 Mock 数据替代。")
            return self.generate_mock(category_key)

    def process_tweets(self, tweets, category_key):
        articles = []
        for t in tweets:
            # 兼容 bird 不同版本的输出格式
            tweet_id = t.get("id_str") or str(t.get("id"))
            text = t.get("full_text") or t.get("text") or ""
            user = t.get("user") or {}
            
            articles.append({
                "id": tweet_id,
                "source": "Twitter/X",
                "published_at": t.get("created_at") or datetime.datetime.now().isoformat(),
                "title": self._extract_title(text),
                "content": text,
                "summary": text[:200] + "..." if len(text) > 200 else text,
                "url": f"https://x.com/i/status/{tweet_id}",
                "tags": [h.get("text") for h in t.get("entities", {}).get("hashtags", [])],
                "category": category_key,
                "author": {
                    "username": user.get("screen_name") or "unknown",
                    "display_name": user.get("name") or "Anonymous",
                    "avatar": user.get("profile_image_url_https")
                },
                "metrics": {
                    "likes": t.get("favorite_count", 0),
                    "retweets": t.get("retweet_count", 0),
                    "replies": t.get("reply_count", 0)
                }
            })
        return articles

    def _extract_title(self, text):
        # 提取第一行或前 60 个字符作为标题
        lines = text.split('\n')
        first_line = lines[0].strip()
        if len(first_line) > 80:
            return first_line[:77] + "..."
        return first_line or "AI News Update"

    def generate_mock(self, category_key):
        """生成高质量的模拟数据，确保前端重构有内容展示"""
        now = datetime.datetime.now()
        mocks = {
            "open_source": [
                {
                    "title": "DeepSeek-V3: The New Open Source SOTA",
                    "content": "DeepSeek-V3 is here! Outperforming GPT-4o on many reasoning tasks. Fully open weights and training logs. Check it out: github.com/deepseek-ai/DeepSeek-V3 #AI #OpenSource",
                    "author": "DeepSeek AI", "handle": "deepseek_ai", "likes": 5200, "retweets": 1200
                },
                {
                    "title": "Flux.1: Next-Gen Image Generation",
                    "content": "Black Forest Labs released Flux.1. The details in these images are insane. Better than Midjourney v6? Try it now on HuggingFace. #Flux1 #GenerativeAI",
                    "author": "AI Art Daily", "handle": "ai_art_daily", "likes": 3100, "retweets": 800
                }
            ],
            "tutorial": [
                {
                    "title": "How to deploy Llama 3.3 locally with Ollama",
                    "content": "Thread: 🧵 A complete guide to running the latest Llama 3.3 on your laptop. \n1. Install Ollama\n2. Pull llama3.3:70b\n3. Set up memory optimization...\nFull tutorial here: [Link]",
                    "author": "The AI Guide", "handle": "the_ai_guide", "likes": 1500, "retweets": 450
                }
            ],
            "model": [
                {
                    "title": "Claude 3.7 Opus Rumors heating up",
                    "content": "Rumors suggest Anthropic is preparing to launch Claude 3.7 Opus next week. Expecting massive leaps in coding and agency. #Anthropic #Claude37",
                    "author": "LLM Insights", "handle": "llm_insights", "likes": 2800, "retweets": 600
                }
            ],
            "free": [
                {
                    "title": "Groq: Free API Credits for Developers",
                    "content": "Groq is offering free tier API access for Llama 3.1 405B. The speed is unbelievable (500 t/s). Get your key at groq.com/developers #FreeAI #Groq",
                    "author": "Dev Tools", "handle": "dev_tools", "likes": 4200, "retweets": 1500
                }
            ],
            "tool": [
                {
                    "title": "Cursor AI: The best coding experience in 2026",
                    "content": "Cursor's new 'Tab' feature is basically reading my mind. It's not just auto-complete, it's auto-architecture. #Cursor #CodingAI",
                    "author": "Web Dev Hub", "handle": "webdev_hub", "likes": 2100, "retweets": 300
                }
            ]
        }
        
        category_mocks = mocks.get(category_key, [])
        articles = []
        for i, m in enumerate(category_mocks):
            pub_time = now - datetime.timedelta(hours=random.randint(1, 48))
            articles.append({
                "id": f"mock_{category_key}_{i}",
                "source": "Twitter/X",
                "published_at": pub_time.isoformat(),
                "title": m["title"],
                "content": m["content"],
                "summary": m["content"][:150] + "...",
                "url": f"https://x.com/{m['handle']}/status/{random.randint(100000, 999999)}",
                "tags": ["AI", category_key, "2026"],
                "category": category_key,
                "author": {
                    "username": m["handle"],
                    "display_name": m["author"],
                    "avatar": f"https://ui-avatars.com/api/?name={m['author']}&background=random"
                },
                "metrics": {
                    "likes": m["likes"],
                    "retweets": m["retweets"],
                    "replies": random.randint(10, 200)
                }
            })
        return articles

def main():
    # 检测是否强制使用 Mock
    use_mock = "--mock" in sys.argv
    fetcher = TwitterFetcher(use_mock=use_mock) 
    
    print(f"🚀 开始抓取 AI Daily News (Twitter/X)...")
    if fetcher.use_mock:
        print("  📝 处于 MOCK 模式")
    elif not fetcher.bird_available:
        print("  ⚠️ 未检测到 bird CLI，将自动降级为 MOCK 模式")

    all_articles = []
    category_meta = []
    
    for key, info in CATEGORIES.items():
        print(f"  📥 正在抓取: {info['name']}...")
        articles = fetcher.fetch(key, info['query'])
        all_articles.extend(articles)
        category_meta.append({
            "key": key,
            "name": info["name"],
            "icon": info["icon"],
            "count": len(articles)
        })
    
    # 按发布时间倒序排列
    all_articles.sort(key=lambda x: x['published_at'], reverse=True)
    
    result = {
        "lastUpdate": datetime.datetime.now().strftime("%Y/%m/%d %H:%M"),
        "categories": category_meta,
        "articles": all_articles
    }
    
    # 写入 data.json
    output_path = "data.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 数据更新完成！共计 {len(all_articles)} 条资讯。")
    print(f"📂 输出文件: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    main()
