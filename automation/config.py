"""
AI Tech Blog 自动化配置
"""
import os
from pathlib import Path

# 加载 .env 文件
def load_env():
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

load_env()

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

# LLM 配置 - 支持 OpenAI / GLM / DeepSeek
# LLM_PROVIDER: "openai" | "glm" | "deepseek"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek")

LLM_CONFIGS = {
    "openai": {
        "base_url": None,  # 使用默认值
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 2000,
    },
    "glm": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "model": "glm-4-flash",  # 或 glm-4-plus
        "temperature": 0.7,
        "max_tokens": 2000,
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "temperature": 0.7,
        "max_tokens": 2000,
    },
}

LLM_CONFIG = LLM_CONFIGS.get(LLM_PROVIDER, LLM_CONFIGS["deepseek"])

# 翻译配置
TRANSLATION_CONFIG = {
    "source_lang": "EN",
    "target_langs": ["ZH", "JA"],
}

# 去重数据库
DEDUP_DB_PATH = PROJECT_ROOT / "automation" / "data" / "dedup.db"

# API Keys (从环境变量读取)
# LLM_API_KEY: 通用密钥，根据 LLM_PROVIDER 自动选择
LLM_API_KEY = os.getenv("LLM_API_KEY", "") or os.getenv("DEEPSEEK_API_KEY", "") or os.getenv("GLM_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY", "")
