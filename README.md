# AI Daily News v2.0 (Twitter Aggregator)

## Project Overview
A real-time AI news aggregator focusing on high-quality content from Twitter/X.

## Content Focus
- **🔓 Open Source**: AI projects on GitHub/HuggingFace.
- **📖 Tutorials**: Comprehensive AI guides and threads.
- **🤖 Model Releases**: New LLMs and weights.
- **🆓 Free Resources**: Free API credits and AI tools.
- **🛠️ Practical Tools**: Tool recommendations.

## Tech Stack
- **Backend**: Python script (`fetch_news.py`) using Twitter MCP (via `bird` CLI) to aggregate news.
- **Frontend**: Modern responsive web app (to be refactored).
- **Data**: `data.json` updated daily.

## Getting Started
1. Configure Twitter cookies for `bird` CLI.
2. Run `python3 fetch_news.py` to update news.
3. Open `index.html` to view.

## Backend Logic
The `fetch_news.py` uses specific search queries to filter high-signal AI content from X.com, categorizes them, and extracts key metrics.
