# AI Daily News - Data Schema v2.0

## Overview
The data is stored in `data.json` and follows a structured format for Twitter AI news aggregation.

## Root Object
| Field | Type | Description |
| :--- | :--- | :--- |
| `lastUpdate` | string | ISO 8601 timestamp of the last fetch |
| `categories` | array | List of category metadata |
| `articles` | array | List of news articles |

## Category Object
| Field | Type | Description |
| :--- | :--- | :--- |
| `key` | string | Unique identifier for the category |
| `name` | string | Display name of the category |
| `count` | number | Number of articles in this category |

## Article Object
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | string | Unique tweet ID |
| `source` | string | Always "Twitter/X" |
| `published_at` | string | ISO 8601 timestamp of the tweet |
| `title` | string | Extracted headline (first line or summary) |
| `content` | string | Full text of the tweet |
| `summary` | string | Brief summary of the content |
| `url` | string | Original tweet URL |
| `tags` | array | List of hashtags or keywords |
| `category` | string | Category key (e.g., `open_source`, `tutorial`, `model`, `free`, `tool`) |
| `author` | object | { `username`, `display_name`, `avatar` } |
| `metrics` | object | { `likes`, `retweets`, `replies` } |

## Categories Definitions
- `open_source`: AI Open Source projects from Twitter/X
- `tutorial`: AI tutorials and sharing
- `model`: Model release information
- `free`: Free use/access (white-prostitutes)
- `tool`: Practical tool recommendations
