"""
LLM 内容处理器 - 专业深度分析风格
"""
import json
import logging
import os
from typing import Dict, Optional
from dataclasses import dataclass

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from config import LLM_CONFIG, LLM_API_KEY, LLM_PROVIDER

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ProcessedArticle:
    """处理后的文章"""
    original_title: str
    title: str
    summary: str
    content: str
    keywords: list
    category: str
    source_url: str
    source_name: str


# Prompt 模板 - 专业深度分析风格
PROCESSING_PROMPT = """You are an expert AI technology analyst writing for a professional tech blog.

Transform the following raw article content into a professional, in-depth analysis article.

## Requirements:
1. **Title**: Create a compelling, professional title (not clickbait)
2. **Summary**: Write a concise 2-3 sentence summary highlighting the key insights
3. **Content**: Rewrite as a professional analysis article with:
   - Clear introduction explaining the context and significance
   - Detailed analysis of the technology/topic
   - Implications for the industry and future developments
   - Professional tone suitable for tech professionals
   - Well-structured paragraphs with logical flow
   - Target length: 1000-2000 words
4. **Keywords**: Extract 3-5 relevant keywords/tags

## Raw Article:
Title: {original_title}
Source: {source_name}
Content:
{raw_content}

## Output Format (JSON):
{{
    "title": "Your professional title here",
    "summary": "Your 2-3 sentence summary here",
    "content": "Your full article content here (use markdown format)",
    "keywords": ["keyword1", "keyword2", "keyword3"]
}}
"""


class LLMProcessor:
    """LLM 内容处理器"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or LLM_API_KEY
        self.provider = LLM_PROVIDER
        self.config = LLM_CONFIG

        if not self.api_key:
            logger.warning(f"未配置 LLM_API_KEY，将使用模拟模式")
            self.client = None
        else:
            # 支持不同 LLM 提供商（都兼容 OpenAI 格式）
            client_kwargs = {"api_key": self.api_key}
            if self.config.get("base_url"):
                client_kwargs["base_url"] = self.config["base_url"]

            self.client = OpenAI(**client_kwargs)
            logger.info(f"LLM 已初始化: {self.provider} - {self.config['model']}")
    
    def process_article(self, article_data: Dict) -> Optional[ProcessedArticle]:
        """处理单篇文章"""
        if not self.client:
            return self._mock_process(article_data)
        
        try:
            prompt = PROCESSING_PROMPT.format(
                original_title=article_data.get('title', ''),
                source_name=article_data.get('source', ''),
                raw_content=article_data.get('content', '')[:6000]  # 限制输入长度
            )
            
            response = self.client.chat.completions.create(
                model=LLM_CONFIG['model'],
                messages=[
                    {"role": "system", "content": "You are a professional AI technology analyst. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=LLM_CONFIG['temperature'],
                max_tokens=LLM_CONFIG['max_tokens']
            )
            
            result_text = response.choices[0].message.content
            
            # 解析 JSON 响应
            # 处理可能的 markdown 代码块
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            result = json.loads(result_text.strip())
            
            return ProcessedArticle(
                original_title=article_data.get('title', ''),
                title=result.get('title', article_data.get('title', '')),
                summary=result.get('summary', ''),
                content=result.get('content', ''),
                keywords=result.get('keywords', []),
                category=article_data.get('category', 'AI'),
                source_url=article_data.get('url', ''),
                source_name=article_data.get('source', '')
            )
            
        except Exception as e:
            logger.error(f"LLM 处理失败: {e}")
            return None
    
    def _mock_process(self, article_data: Dict) -> ProcessedArticle:
        """模拟处理（无 API Key 时使用）"""
        return ProcessedArticle(
            original_title=article_data.get('title', ''),
            title=f"[Analysis] {article_data.get('title', '')}",
            summary=article_data.get('summary', '')[:200],
            content=article_data.get('content', '')[:2000],
            keywords=['AI', 'Technology'],
            category=article_data.get('category', 'AI'),
            source_url=article_data.get('url', ''),
            source_name=article_data.get('source', '')
        )
    
    def process_batch(self, articles: list) -> list:
        """批量处理文章"""
        processed = []
        for i, article in enumerate(articles):
            logger.info(f"处理文章 {i+1}/{len(articles)}: {article.get('title', '')[:50]}")
            result = self.process_article(article)
            if result:
                processed.append(result)
        return processed


def main():
    """测试"""
    processor = LLMProcessor()
    test_article = {
        'title': 'Test Article',
        'content': 'This is a test article about AI technology.',
        'source': 'Test Source',
        'url': 'https://example.com'
    }
    result = processor.process_article(test_article)
    if result:
        print(f"Title: {result.title}")
        print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
