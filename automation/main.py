"""
AI Tech Blog 自动化主入口
完整流水线：采集 → 处理 → 翻译 → 发布
"""
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from config import CONTENT_CONFIG
from collector import RSSCollector
from processor import LLMProcessor
from translator import TranslationPipeline
from publisher import ArticlePublisher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutomationPipeline:
    """自动化流水线"""
    
    def __init__(self, skip_audio: bool = False):
        self.collector = RSSCollector()
        self.processor = LLMProcessor()
        self.translator = TranslationPipeline()
        self.publisher = ArticlePublisher()
        self.skip_audio = skip_audio
    
    def run(self, max_articles: int = None) -> Dict:
        """运行完整流水线"""
        results = {
            'collected': 0,
            'processed': 0,
            'translated': 0,
            'published': 0,
            'articles': []
        }
        
        # Step 1: 采集
        logger.info("=" * 50)
        logger.info("Step 1: 采集文章")
        logger.info("=" * 50)
        articles = self.collector.collect_all()
        
        if not articles:
            logger.info("没有新文章需要处理")
            return results
        
        results['collected'] = len(articles)
        
        # 限制文章数量
        if max_articles:
            articles = articles[:max_articles]
        
        # Step 2: LLM 处理
        logger.info("=" * 50)
        logger.info("Step 2: AI 内容处理")
        logger.info("=" * 50)
        processed_articles = []
        
        for article in articles:
            processed = self.processor.process_article(article)
            if processed:
                processed_articles.append({
                    'article': article,
                    'processed': processed
                })
        
        results['processed'] = len(processed_articles)
        
        # Step 3: 翻译 + 发布
        logger.info("=" * 50)
        logger.info("Step 3: 翻译和发布")
        logger.info("=" * 50)
        
        for item in processed_articles:
            article = item['article']
            processed = item['processed']
            
            # 翻译
            slug = self.publisher._generate_slug(processed.title)
            translation_result = self.translator.process(
                title=processed.title,
                summary=processed.summary,
                content=processed.content,
                slug=slug,
                generate_audio=not self.skip_audio
            )
            
            # 发布
            publish_result = self.publisher.publish_article(
                title=processed.title,
                summary=processed.summary,
                content=processed.content,
                keywords=processed.keywords,
                source_url=processed.source_url,
                source_name=processed.source_name,
                translations=translation_result.get('translations'),
                audio_paths=translation_result.get('audio_paths')
            )
            
            results['articles'].append(publish_result)
            results['translated'] += 1
            results['published'] += 1
        
        logger.info("=" * 50)
        logger.info("流水线完成!")
        logger.info(f"采集: {results['collected']} 篇")
        logger.info(f"处理: {results['processed']} 篇")
        logger.info(f"翻译: {results['translated']} 篇")
        logger.info(f"发布: {results['published']} 篇")
        logger.info("=" * 50)
        
        return results
    
    def collect_only(self) -> List:
        """仅采集文章"""
        return self.collector.collect_all()
    
    def process_only(self, input_file: str) -> List:
        """仅处理文章"""
        with open(input_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        return self.processor.process_batch(articles)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='AI Tech Blog 自动化流水线')
    parser.add_argument('--collect', action='store_true', help='仅采集文章')
    parser.add_argument('--process', type=str, help='处理指定文件中的文章')
    parser.add_argument('--max', type=int, default=CONTENT_CONFIG['posts_per_day'], help='最大处理文章数')
    parser.add_argument('--skip-audio', action='store_true', help='跳过音频生成')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际发布')
    
    args = parser.parse_args()
    
    pipeline = AutomationPipeline(skip_audio=args.skip_audio)
    
    if args.collect:
        articles = pipeline.collect_only()
        print(f"采集到 {len(articles)} 篇文章")
        for a in articles[:5]:
            print(f"  - {a.title[:50]}...")
    elif args.process:
        results = pipeline.process_only(args.process)
        print(f"处理了 {len(results)} 篇文章")
    else:
        results = pipeline.run(max_articles=args.max)
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
