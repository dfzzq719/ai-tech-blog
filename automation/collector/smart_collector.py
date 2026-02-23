"""
智能内容筛选器 - 高效采集和筛选 AI 技术内容
"""
import feedparser
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AI 生产力工具信息源配置（面向中小企业和个人用户）
VERIFIED_SOURCES = {
    # Tier 1: 核心生产力内容源
    "zapier": {
        "name": "Zapier Blog",
        "url": "https://zapier.com/blog/feed/",
        "priority": 1,
        "quality_score": 10,
        "content_type": "productivity",  # 生产力工具
        "keywords": ["automation", "workflow", "productivity", "AI tools", "tutorial"]
    },
    "openai": {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml",
        "priority": 1,
        "quality_score": 10,
        "content_type": "product_updates",
        "keywords": ["ChatGPT", "GPT", "feature", "update", "tips", "guide"]
    },
    "anthropic": {
        "name": "Anthropic Blog",
        "url": "https://www.anthropic.com/news/rss.xml",
        "priority": 1,
        "quality_score": 9,
        "content_type": "product_updates",
        "keywords": ["Claude", "feature", "update", "use case", "tutorial"]
    },
    # Tier 2: AI 工具评测和教程
    "producthunt": {
        "name": "Product Hunt AI",
        "url": "https://www.producthunt.com/feed?category=artificial-intelligence",
        "priority": 2,
        "quality_score": 8,
        "content_type": "new_tools",
        "keywords": ["AI tool", "productivity", "new launch"]
    },
    # Tier 3: YouTube 内容创作者（需要手动整合或使用 API）
    # Matt Wolfe: AI 工具评测、生产力技巧
    # Ali Abdaal: 生产力、工作流优化
    # Thomas Frank: Notion、生产力系统
    # The AI Advantage: AI 工具教程
    # Wes Roth: AI 新闻解读
    # 参考: 手动精选内容，后续可接入 YouTube API
}

# AI 生产力相关关键词 (用于评分)
AI_KEYWORDS = {
    # 高权重关键词 - 实用性和生产力
    "high": [
        # 工具和应用
        "ChatGPT", "Claude", "Gemini", "Midjourney", "Notion AI",
        # 生产力场景
        "automation", "workflow", "productivity", "efficiency",
        "save time", "template", "tutorial", "how to", "guide",
        # 功能关键词
        "feature", "update", "new release", "integration", "API"
    ],
    # 中等权重关键词
    "medium": [
        # 应用场景
        "content creation", "writing", "marketing", "design",
        "customer service", "data analysis", "coding", "SEO",
        # 工具类型
        "AI tool", "AI assistant", "chatbot", "generator"
    ],
    # 低权重关键词
    "low": ["AI", "ML", "automation", "tool", "tips"]
}

# 排除关键词 (学术性/研究性内容)
EXCLUDE_KEYWORDS = [
    # 学术研究
    "arXiv", "paper", "research", "algorithm", "model architecture",
    "neural network", "training", "benchmark", "dataset",
    # 量子物理/生物等非生产力领域
    "quantum", "protein", "molecular", "physics", "biology"
]


@dataclass
class Article:
    """文章数据结构"""
    id: str
    title: str
    url: str
    source: str
    published: Optional[str]
    summary: str
    content: str
    ai_relevance_score: float = 0.0
    quality_score: float = 0.0
    final_score: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


class AISmartCollector:
    """智能 AI 内容采集器"""
    
    def __init__(self, max_articles_per_source: int = 20):
        self.max_articles = max_articles_per_source
        self.seen_ids = set()
        
    def _generate_id(self, url: str, title: str) -> str:
        return hashlib.md5(f"{url}:{title}".encode()).hexdigest()
    
    def _calculate_ai_relevance(self, title: str, summary: str) -> float:
        """计算 AI 相关性分数 (0-100)"""
        text = f"{title} {summary}".lower()
        score = 0.0
        
        # 检查排除关键词
        for keyword in EXCLUDE_KEYWORDS:
            if keyword.lower() in text:
                return 0.0
        
        # 高权重关键词
        for keyword in AI_KEYWORDS["high"]:
            if keyword.lower() in text:
                score += 15
        
        # 中等权重关键词
        for keyword in AI_KEYWORDS["medium"]:
            if keyword.lower() in text:
                score += 8
        
        # 低权重关键词
        for keyword in AI_KEYWORDS["low"]:
            if keyword.lower() in text:
                score += 3
        
        return min(score, 100.0)
    
    def _calculate_quality_score(self, article: Dict, source_config: Dict) -> float:
        """计算质量分数"""
        score = source_config.get("quality_score", 5) * 5  # 基础分
        
        # 标题长度 (太短或太长扣分)
        title_len = len(article.get("title", ""))
        if 30 <= title_len <= 100:
            score += 10
        elif title_len < 20:
            score -= 5
        
        # 摘要长度
        summary_len = len(article.get("summary", ""))
        if summary_len >= 200:
            score += 10
        
        # 发布时间 (越新越好)
        try:
            published = article.get("published", "")
            if published:
                # 简单判断是否最近
                if "2026" in published or "2025" in published:
                    score += 15
        except:
            pass
        
        return min(score, 100.0)
    
    def collect_from_rss(self, source_key: str) -> List[Article]:
        """从 RSS 源采集"""
        config = VERIFIED_SOURCES.get(source_key)
        if not config:
            return []
        
        articles = []
        try:
            logger.info(f"采集: {config['name']}")
            feed = feedparser.parse(config["url"])
            
            for entry in feed.entries[:self.max_articles]:
                article_id = self._generate_id(
                    entry.get("link", ""), 
                    entry.get("title", "")
                )
                
                if article_id in self.seen_ids:
                    continue
                
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                
                # 计算 AI 相关性
                ai_score = self._calculate_ai_relevance(title, summary)
                if ai_score < 10:  # 低于阈值跳过
                    continue
                
                article = Article(
                    id=article_id,
                    title=title,
                    url=entry.get("link", ""),
                    source=config["name"],
                    published=entry.get("published", ""),
                    summary=summary[:500],
                    content=summary,
                    ai_relevance_score=ai_score
                )
                
                # 计算质量分数
                article.quality_score = self._calculate_quality_score(
                    {"title": title, "summary": summary}, 
                    config
                )
                
                # 最终分数 = 相关性 * 0.6 + 质量 * 0.4
                article.final_score = article.ai_relevance_score * 0.6 + article.quality_score * 0.4
                
                articles.append(article)
                self.seen_ids.add(article_id)
            
            logger.info(f"从 {config['name']} 采集到 {len(articles)} 篇相关文章")
            
        except Exception as e:
            logger.error(f"采集失败 {config['name']}: {e}")
        
        return articles
    
    def collect_all(self) -> List[Article]:
        """从所有源采集"""
        all_articles = []
        
        for source_key in VERIFIED_SOURCES:
            articles = self.collect_from_rss(source_key)
            all_articles.extend(articles)
        
        # 按最终分数排序
        all_articles.sort(key=lambda x: x.final_score, reverse=True)
        
        logger.info(f"总计采集 {len(all_articles)} 篇高质量 AI 文章")
        return all_articles
    
    def get_top_articles(self, n: int = 10) -> List[Article]:
        """获取 Top N 文章"""
        articles = self.collect_all()
        return articles[:n]
    
    def print_summary(self, articles: List[Article]):
        """打印摘要"""
        print("\n" + "="*60)
        print("[Summary] Collection Results")
        print("="*60)
        
        for i, article in enumerate(articles[:10], 1):
            print(f"\n{i}. [{article.final_score:.1f}分] {article.title[:60]}...")
            print(f"   来源: {article.source}")
            print(f"   AI相关性: {article.ai_relevance_score:.1f} | 质量: {article.quality_score:.1f}")
        
        print("\n" + "="*60)


def main():
    """测试采集"""
    collector = AISmartCollector()
    articles = collector.collect_all()
    collector.print_summary(articles)
    
    # 返回 Top 5 推荐
    print("\n[TOP 5 Recommendations]:")
    for i, article in enumerate(articles[:5], 1):
        print(f"{i}. {article.title[:50]}... (score: {article.final_score:.1f})")


if __name__ == "__main__":
    main()
