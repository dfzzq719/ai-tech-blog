"""
RSS 内容采集器
"""
import feedparser
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import requests
from bs4 import BeautifulSoup

from config import RSS_SOURCES, DEDUP_DB_PATH

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Article:
    """文章数据结构"""
    id: str
    title: str
    url: str
    source: str
    category: str
    published: Optional[str]
    summary: str
    content: str
    collected_at: str
    priority: int = 1

    def to_dict(self) -> Dict:
        return asdict(self)


class RSSCollector:
    """RSS 采集器"""
    
    def __init__(self):
        self.seen_ids = self._load_seen_ids()
        
    def _load_seen_ids(self) -> set:
        """加载已处理的文章ID"""
        db_path = Path(DEDUP_DB_PATH)
        if db_path.exists():
            with open(db_path, 'r', encoding='utf-8') as f:
                return set(line.strip() for line in f if line.strip())
        return set()
    
    def _save_seen_id(self, article_id: str):
        """保存已处理的文章ID"""
        db_path = Path(DEDUP_DB_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(db_path, 'a', encoding='utf-8') as f:
            f.write(f"{article_id}\n")
        self.seen_ids.add(article_id)
    
    def _generate_id(self, url: str, title: str) -> str:
        """生成唯一ID"""
        content = f"{url}:{title}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _fetch_full_content(self, url: str) -> str:
        """获取文章完整内容"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除不需要的元素
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # 获取主要内容
            article = soup.find('article') or soup.find('main') or soup.find('div', class_='content')
            if article:
                return article.get_text(separator='\n', strip=True)
            
            # 回退到body
            body = soup.find('body')
            return body.get_text(separator='\n', strip=True) if body else ""
            
        except Exception as e:
            logger.warning(f"获取文章内容失败 {url}: {e}")
            return ""
    
    def collect_from_source(self, source: Dict) -> List[Article]:
        """从单个RSS源采集文章"""
        articles = []
        
        try:
            logger.info(f"正在采集: {source['name']}")
            feed = feedparser.parse(source['url'])
            
            if feed.bozo:
                logger.warning(f"RSS解析警告: {source['name']} - {feed.bozo_exception}")
            
            for entry in feed.entries[:10]:  # 每个源最多取10篇
                article_id = self._generate_id(entry.get('link', ''), entry.get('title', ''))
                
                # 去重检查
                if article_id in self.seen_ids:
                    continue
                
                # 获取内容
                content = entry.get('content', [{}])[0].get('value', '')
                if not content:
                    content = entry.get('summary', '')
                if not content:
                    content = self._fetch_full_content(entry.get('link', ''))
                
                if len(content) < 200:  # 内容太短，跳过
                    continue
                
                article = Article(
                    id=article_id,
                    title=entry.get('title', 'Untitled'),
                    url=entry.get('link', ''),
                    source=source['name'],
                    category=source['category'],
                    published=entry.get('published', entry.get('updated', '')),
                    summary=entry.get('summary', '')[:500],
                    content=content[:10000],  # 限制长度
                    collected_at=datetime.now().isoformat(),
                    priority=source.get('priority', 1)
                )
                
                articles.append(article)
                self._save_seen_id(article_id)
                
            logger.info(f"从 {source['name']} 采集到 {len(articles)} 篇新文章")
            
        except Exception as e:
            logger.error(f"采集失败 {source['name']}: {e}")
        
        return articles
    
    def collect_all(self) -> List[Article]:
        """从所有RSS源采集文章"""
        all_articles = []
        
        for source in RSS_SOURCES:
            articles = self.collect_from_source(source)
            all_articles.extend(articles)
        
        # 按优先级和发布时间排序
        all_articles.sort(key=lambda x: (x.priority, x.published or ''), reverse=False)
        
        logger.info(f"总计采集到 {len(all_articles)} 篇新文章")
        return all_articles
    
    def save_articles(self, articles: List[Article], output_file: str = "pending_articles.json"):
        """保存文章到待处理队列"""
        output_path = Path(__file__).parent / "data" / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([a.to_dict() for a in articles], f, ensure_ascii=False, indent=2)
        
        logger.info(f"已保存 {len(articles)} 篇文章到 {output_path}")


def main():
    """主函数"""
    collector = RSSCollector()
    articles = collector.collect_all()
    collector.save_articles(articles)
    return articles


if __name__ == "__main__":
    main()
