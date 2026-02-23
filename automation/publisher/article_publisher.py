"""
文章发布器 - 将处理后的文章写入 Docusaurus 目录
"""
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from config import BLOG_DIR, I18N_DIR, CONTENT_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArticlePublisher:
    """文章发布器"""
    
    def __init__(self):
        self.blog_dir = Path(BLOG_DIR)
        self.i18n_dir = Path(I18N_DIR)
    
    def _generate_slug(self, title: str) -> str:
        """生成 URL 友好的 slug"""
        # 转小写，移除特殊字符
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = slug.strip('-')
        return slug[:50]  # 限制长度
    
    def _generate_frontmatter(self, title: str, summary: str, keywords: List[str], source_url: str, source_name: str) -> str:
        """生成 YAML frontmatter"""
        keywords_str = ', '.join(f'"{kw}"' for kw in keywords)
        return f'''---
slug: {self._generate_slug(title)}
title: "{title.replace('"', '\\"')}"
authors: [ai-editor]
tags: [{keywords_str}]
description: "{summary.replace('"', '\\"')[:160]}"
source_url: {source_url}
source_name: {source_name}
---

'''
    
    def publish_article(
        self,
        title: str,
        summary: str,
        content: str,
        keywords: List[str],
        source_url: str,
        source_name: str,
        translations: Optional[Dict] = None,
        audio_paths: Optional[Dict] = None
    ) -> Dict:
        """发布文章"""
        
        # 生成日期和 slug
        today = datetime.now()
        date_str = today.strftime('%Y-%m-%d')
        slug = self._generate_slug(title)
        
        # 创建文章目录
        article_dir = self.blog_dir / f"{date_str}-{slug}"
        article_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成英文版
        frontmatter = self._generate_frontmatter(title, summary, keywords, source_url, source_name)
        
        # 添加音频播放器（如果有）
        audio_section = ""
        if audio_paths and audio_paths.get('en'):
            audio_section = f'\n<audio controls src="/audio/{slug}/en.mp3"></audio>\n'
        
        en_content = frontmatter + f"# {title}\n\n{audio_section}\n{content}\n\n<!-- truncate -->\n"
        
        # 写入英文版
        en_file = article_dir / "index.md"
        with open(en_file, 'w', encoding='utf-8') as f:
            f.write(en_content)
        logger.info(f"发布英文版: {en_file}")
        
        # 发布翻译版本
        published_translations = {}
        
        if translations:
            for lang, trans in translations.items():
                lang_dir = self.i18n_dir / lang / "docusaurus-plugin-content-blog" / f"{date_str}-{slug}"
                lang_dir.mkdir(parents=True, exist_ok=True)
                
                trans_frontmatter = self._generate_frontmatter(
                    trans['title'], 
                    trans['summary'], 
                    keywords, 
                    source_url, 
                    source_name
                )
                
                # 添加音频播放器
                trans_audio_section = ""
                if audio_paths and audio_paths.get(lang):
                    trans_audio_section = f'\n<audio controls src="/audio/{slug}/{lang}.mp3"></audio>\n'
                
                trans_content = trans_frontmatter + f"# {trans['title']}\n\n{trans_audio_section}\n{trans['content']}\n\n<!-- truncate -->\n"
                
                trans_file = lang_dir / "index.md"
                with open(trans_file, 'w', encoding='utf-8') as f:
                    f.write(trans_content)
                
                published_translations[lang] = str(trans_file)
                logger.info(f"发布{lang}版: {trans_file}")
        
        return {
            'slug': slug,
            'date': date_str,
            'en_file': str(en_file),
            'translations': published_translations,
            'audio_paths': audio_paths
        }
    
    def publish_batch(self, articles: List[Dict]) -> List[Dict]:
        """批量发布文章"""
        published = []
        for article in articles:
            result = self.publish_article(**article)
            published.append(result)
        return published


def main():
    """测试"""
    publisher = ArticlePublisher()
    result = publisher.publish_article(
        title="Test Article Title",
        summary="This is a test article summary.",
        content="This is the main content of the test article.\n\nWith multiple paragraphs.",
        keywords=["AI", "Technology", "Test"],
        source_url="https://example.com",
        source_name="Test Source"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
