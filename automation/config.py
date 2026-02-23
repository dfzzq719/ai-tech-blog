"""
AI Tech Blog 自动化配置
"""
import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
BLOG_DIR = PROJECT_ROOT / "blog"
I18N_DIR = PROJECT_ROOT / "i18n"
AUDIO_DIR = PROJECT_ROOT / "static" / "audio"

# RSS 源配置 - AI技术类网站
RSS_SOURCES = [
    {
        "name": "MIT Technology Review AI",
        "url": "https://www.technologyreview.com/feed/",
        "category": "AI",
        "priority": 1,
    },
    {
        "name": "AI Weekly",
        "url": "https://aiweekly.co/feed",
        "category": "AI",
        "priority": 1,
    },
    {
        "name": "The Gradient",
        "url": "https://thegradient.pub/rss/",
        "category": "AI",
        "priority": 2,
    },
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml",
        "category": "AI",
        "priority": 1,
    },
    {
        "name": "Google AI Blog",
        "url": "https://blog.google/technology/ai/rss/",
        "category": "AI",
        "priority": 1,
    },
    {
        "name": "DeepMind Blog",
        "url": "https://deepmind.com/blog/rss.xml",
        "category": "AI",
        "priority": 1,
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/artificial-intelligence/feed/",
        "category": "AI",
        "priority": 2,
    },
    {
        "name": "Synced AI",
        "url": "https://syncedreview.com/feed/",
        "category": "AI",
        "priority": 2,
    },
]

# 内容处理配置
CONTENT_CONFIG = {
    "min_word_count": 300,      # 最小字数
    "max_word_count": 3000,     # 最大字数
    "target_word_count": 1500,  # 目标字数
    "posts_per_day": 3,         # 每天发布数量
}

# LLM 配置
LLM_CONFIG = {
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 2000,
}

# 翻译配置
TRANSLATION_CONFIG = {
    "source_lang": "EN",
    "target_langs": ["ZH", "JA"],
}

# 去重数据库
DEDUP_DB_PATH = PROJECT_ROOT / "automation" / "data" / "dedup.db"

# API Keys (从环境变量读取)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY", "")
