"""
Text content analysis using Detoxify and sentiment models.
Detects toxicity, sentiment, spam patterns in captions and comments.
"""

import warnings
warnings.filterwarnings('ignore')

from typing import List, Dict, Union
import numpy as np
from transformers import pipeline
import torch

from src.config import (
    TEXT_TOXICITY_MODEL,
    TEXT_SENTIMENT_MODEL,
    BATCH_SIZE_TEXT,
    DEVICE,
    get_model_cache_path
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class TextAnalyzer:
    """Unified text analysis for toxic and sentiment detection"""
    
    def __init__(self):
        self.device = DEVICE
        logger.info(f"Initializing TextAnalyzer on {self.device}")
        model_name = "unitary/unbiased-toxic-roberta" if "unbiased" in TEXT_TOXICITY_MODEL else "unitary/toxic-bert"
        logger.info(f"Loading Toxicity model: {model_name}")
        
        try:
            self.toxicity_pipeline = pipeline(
                "text-classification", 
                model=model_name, 
                device=0 if self.device == "cuda" else -1,
                top_k=None  # Return all scores
            )
            logger.info("Toxicity model loaded successfully")
        except Exception as e:
            logger.error(f"CRITICAL: Could not load toxicity model: {e}")
            raise e
        
        # Load sentiment model
        logger.info(f"Loading sentiment model: {TEXT_SENTIMENT_MODEL}")
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=TEXT_SENTIMENT_MODEL,
            device=0 if self.device == "cuda" else -1,
            truncation=True,
            max_length=512
        )
        
        logger.info("TextAnalyzer initialized successfully")
    
    def analyze_toxicity(self, texts: Union[str, List[str]]) -> Dict[str, Union[float, List[float]]]:
        """
        Analyze text toxicity using Transformers pipeline.
        
        Args:
            texts: Single text or list of texts
        
        Returns:
            Dictionary with toxicity scores
        """
        if isinstance(texts, str):
            texts = [texts]
            single_input = True
        else:
            single_input = False
        
        # Filter empty texts
        valid_texts = [t if t else " " for t in texts]
        
        try:
            # Pipeline returns list of dicts: [{'label': 'toxic', 'score': 0.9}, ...]
            # or list of lists if top_k=None: [[{'label': 'toxic', 'score': 0.9}, ...], ...]
            results = self.toxicity_pipeline(valid_texts, batch_size=BATCH_SIZE_TEXT, truncation=True, max_length=512)
            
            # Initialize empty results
            labels = ["toxicity", "severe_toxicity", "obscene", "threat", "insult", "identity_attack"]
            formatted_results = {label: [] for label in labels}
            
            for i, res in enumerate(results):
                scores = {}
                try:
                    # Case 1: List of dicts (top_k=None or >1)
                    if isinstance(res, list):
                        for item in res:
                            if isinstance(item, dict):
                                scores[item['label']] = item['score']
                    # Case 2: Single dict (top_k=1)
                    elif isinstance(res, dict):
                        scores[res['label']] = res['score']
                    else:
                        logger.warning(f"Unexpected result format at index {i}: {type(res)}")
                        continue
                        
                    # Map scores to our standard labels
                    formatted_results["toxicity"].append(scores.get("toxicity", scores.get("toxic", 0.0)))
                    formatted_results["severe_toxicity"].append(scores.get("severe_toxicity", 0.0))
                    formatted_results["obscene"].append(scores.get("obscene", 0.0))
                    formatted_results["threat"].append(scores.get("threat", 0.0))
                    formatted_results["insult"].append(scores.get("insult", 0.0))
                    formatted_results["identity_attack"].append(scores.get("identity_attack", 0.0))
                    
                except Exception as e:
                    logger.error(f"Error parsing result at index {i}: {e}")
                    # Append zeros to keep alignment
                    for label in labels:
                        formatted_results[label].append(0.0)
            
            if single_input:
                # Check if we have results
                if formatted_results["toxicity"]:
                    return {k: v[0] for k, v in formatted_results.items()}
                else:
                    return {k: 0.0 for k in labels}
            else:
                return formatted_results
                
        except Exception as e:
            logger.error(f"Toxicity analysis failed: {e}")
            # Return default scores
            default = {
                "toxicity": 0.0,
                "severe_toxicity": 0.0,
                "obscene": 0.0,
                "threat": 0.0,
                "insult": 0.0,
                "identity_attack": 0.0
            }
            return default if single_input else {k: [0.0] * len(texts) for k in default}
    
    def analyze_sentiment(self, texts: Union[str, List[str]]) -> Union[Dict, List[Dict]]:
        """
        Analyze text sentiment.
        
        Args:
            texts: Single text or list of texts
        
        Returns:
            Sentiment results with label and score
        """
        if isinstance(texts, str):
            texts = [texts]
            single_input = True
        else:
            single_input = False
        
        # Filter empty texts
        valid_texts = [t if t else " " for t in texts]
        
        try:
            # Process in batches for efficiency
            results = []
            for i in range(0, len(valid_texts), BATCH_SIZE_TEXT):
                batch = valid_texts[i:i + BATCH_SIZE_TEXT]
                batch_results = self.sentiment_pipeline(batch)
                results.extend(batch_results)
            
            # Map labels to numeric scores
            for result in results:
                label = result['label'].lower()
                score = result['score']
                
                # Convert to -1 to 1 scale (negative, neutral, positive)
                if 'negative' in label:
                    result['sentiment_score'] = -score
                elif 'positive' in label:
                    result['sentiment_score'] = score
                else:  # neutral
                    result['sentiment_score'] = 0.0
            
            return results[0] if single_input else results
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            default = {'label': 'neutral', 'score': 0.5, 'sentiment_score': 0.0}
            return default if single_input else [default] * len(texts)
    
    def analyze_text(self, texts: Union[str, List[str]]) -> Union[Dict, List[Dict]]:
        """
        Complete text analysis: toxicity + sentiment.
        
        Args:
            texts: Single text or list of texts
        
        Returns:
            Combined analysis results
        """
        if isinstance(texts, str):
            texts = [texts]
            single_input = True
        else:
            single_input = False
        
        # Get toxicity scores
        toxicity = self.analyze_toxicity(texts)
        
        # Get sentiment
        sentiment = self.analyze_sentiment(texts)
        # Note: analyze_sentiment returns a list of dicts because we passed 'texts' as a list
        # So we don't need to wrap it again even if single_input is True
        
        # Combine results
        results = []
        for i in range(len(texts)):
            result = {
                "text": texts[i],
                "toxicity": toxicity["toxicity"][i] if isinstance(toxicity["toxicity"], list) else toxicity["toxicity"],
                "severe_toxicity": toxicity["severe_toxicity"][i] if isinstance(toxicity["severe_toxicity"], list) else toxicity["severe_toxicity"],
                "obscene": toxicity["obscene"][i] if isinstance(toxicity["obscene"], list) else toxicity["obscene"],
                "threat": toxicity["threat"][i] if isinstance(toxicity["threat"], list) else toxicity["threat"],
                "insult": toxicity["insult"][i] if isinstance(toxicity["insult"], list) else toxicity["insult"],
                "identity_attack": toxicity["identity_attack"][i] if isinstance(toxicity["identity_attack"], list) else toxicity["identity_attack"],
                "sentiment_label": sentiment[i]['label'],
                "sentiment_confidence": sentiment[i]['score'],
                "sentiment_score": sentiment[i]['sentiment_score']
            }
            results.append(result)
        
        return results[0] if single_input else results
    
    def detect_spam_patterns(self, text: str) -> Dict[str, Union[bool, float]]:
        """
        Detect spam/engagement bait patterns.
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with spam detection results
        """
        if not text:
            return {"is_spam": False, "spam_score": 0.0, "patterns": []}
        
        text_lower = text.lower()
        patterns_found = []
        
        # Common spam patterns
        spam_keywords = [
            "click link", "link in bio", "dm for", "check profile",
            "follow me", "follow back", "like and comment",
            "tag a friend", "giveaway", "contest", "win free",
            "limited time", "act now", "don't miss"
        ]
        
        for keyword in spam_keywords:
            if keyword in text_lower:
                patterns_found.append(keyword)
        
        # Check excessive emojis (>20% of text)
        emoji_count = sum(1 for c in text if ord(c) > 127)
        emoji_ratio = emoji_count / len(text) if len(text) > 0 else 0
        
        if emoji_ratio > 0.2:
            patterns_found.append("excessive_emojis")
        
        # Check excessive caps (>30% uppercase)
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if len(text) > 0 else 0
        
        if caps_ratio > 0.3:
            patterns_found.append("excessive_caps")
        
        spam_score = min(1.0, len(patterns_found) * 0.25)
        
        return {
            "is_spam": spam_score > 0.5,
            "spam_score": spam_score,
            "patterns": patterns_found
        }


# Global instance for reuse
_text_analyzer_instance = None


def get_text_analyzer() -> TextAnalyzer:
    """Get or create global TextAnalyzer instance"""
    global _text_analyzer_instance
    if _text_analyzer_instance is None:
        _text_analyzer_instance = TextAnalyzer()
    return _text_analyzer_instance


if __name__ == "__main__":
    # Test the analyzer
    analyzer = TextAnalyzer()
    
    test_texts = [
        "I love this product! It's amazing!",
        "This is terrible, I hate it. You're an idiot.",
        "Check my link in bio for amazing deals! Don't miss out! 🔥🔥🔥"
    ]
    
    print("\n" + "="*70)
    print("TEXT ANALYSIS TEST")
    print("="*70)
    
    for text in test_texts:
        print(f"\nText: {text}")
        result = analyzer.analyze_text(text)
        print(f"Toxicity: {result['toxicity']:.3f}")
        print(f"Sentiment: {result['sentiment_label']} ({result['sentiment_score']:.3f})")
        
        spam = analyzer.detect_spam_patterns(text)
        print(f"Spam: {spam['is_spam']} (score: {spam['spam_score']:.3f})")
        if spam['patterns']:
            print(f"Patterns: {', '.join(spam['patterns'])}")
