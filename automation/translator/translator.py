"""
多语言翻译模块 - DeepL + Edge TTS
"""
import json
import logging
import asyncio
import os
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass

try:
    import deepl
except ImportError:
    deepl = None

try:
    import edge_tts
except ImportError:
    edge_tts = None

from config import DEEPL_API_KEY, TRANSLATION_CONFIG, AUDIO_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TranslatedContent:
    """翻译后的内容"""
    original_text: str
    zh_text: str
    ja_text: str
    zh_audio_path: Optional[str]
    ja_audio_path: Optional[str]


class Translator:
    """翻译器"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or DEEPL_API_KEY
        if not self.api_key:
            logger.warning("未配置 DEEPL_API_KEY，翻译功能将被模拟")
            self.translator = None
        else:
            self.translator = deepl.Translator(self.api_key)
    
    def translate(self, text: str, target_lang: str) -> str:
        """翻译文本"""
        if not self.translator:
            # 模拟翻译
            if target_lang == 'ZH':
                return f"[中文翻译] {text[:100]}..."
            elif target_lang == 'JA':
                return f"[日本語翻訳] {text[:100]}..."
            return text
        
        try:
            result = self.translator.translate_text(
                text,
                source_lang='EN',
                target_lang=target_lang
            )
            return result.text
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            return text
    
    def translate_article(self, title: str, summary: str, content: str) -> Dict:
        """翻译文章标题、摘要和内容"""
        return {
            'zh': {
                'title': self.translate(title, 'ZH'),
                'summary': self.translate(summary, 'ZH'),
                'content': self.translate(content, 'ZH')
            },
            'ja': {
                'title': self.translate(title, 'JA'),
                'summary': self.translate(summary, 'JA'),
                'content': self.translate(content, 'JA')
            }
        }


class TTSGenerator:
    """语音生成器"""
    
    # Edge TTS 语音配置
    VOICE_CONFIG = {
        'en': 'en-US-AriaNeural',
        'zh': 'zh-CN-XiaoxiaoNeural',
        'ja': 'ja-JP-NanamiNeural'
    }
    
    async def generate_audio_async(self, text: str, lang: str, output_path: str) -> bool:
        """异步生成音频"""
        if not edge_tts:
            logger.warning("edge_tts 未安装，跳过音频生成")
            return False
        
        try:
            voice = self.VOICE_CONFIG.get(lang, 'en-US-AriaNeural')
            communicate = edge_tts.Communicate(text, voice)
            
            # 确保目录存在
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            await communicate.save(output_path)
            logger.info(f"音频生成成功: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"音频生成失败: {e}")
            return False
    
    def generate_audio(self, text: str, lang: str, output_path: str) -> bool:
        """同步生成音频"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.generate_audio_async(text, lang, output_path)
        )
    
    def generate_article_audio(
        self, 
        slug: str, 
        en_content: str, 
        zh_content: str, 
        ja_content: str
    ) -> Dict[str, str]:
        """为文章生成三语音频"""
        audio_dir = AUDIO_DIR / slug
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        paths = {
            'en': str(audio_dir / 'en.mp3'),
            'zh': str(audio_dir / 'zh.mp3'),
            'ja': str(audio_dir / 'ja.mp3')
        }
        
        # 生成音频（可以并行处理）
        self.generate_audio(en_content, 'en', paths['en'])
        self.generate_audio(zh_content, 'zh', paths['zh'])
        self.generate_audio(ja_content, 'ja', paths['ja'])
        
        return paths


class TranslationPipeline:
    """翻译流水线"""
    
    def __init__(self):
        self.translator = Translator()
        self.tts = TTSGenerator()
    
    def process(self, title: str, summary: str, content: str, slug: str, generate_audio: bool = True) -> Dict:
        """完整翻译流程"""
        # 翻译
        translations = self.translator.translate_article(title, summary, content)
        
        result = {
            'translations': translations,
            'audio_paths': None
        }
        
        # 生成音频
        if generate_audio:
            audio_paths = self.tts.generate_article_audio(
                slug,
                content,
                translations['zh']['content'],
                translations['ja']['content']
            )
            result['audio_paths'] = audio_paths
        
        return result


def main():
    """测试"""
    pipeline = TranslationPipeline()
    result = pipeline.process(
        title="AI Breakthrough in Natural Language Processing",
        summary="A new model achieves state-of-the-art results.",
        content="This is a test article content about AI technology breakthrough...",
        slug="test-article",
        generate_audio=False
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
