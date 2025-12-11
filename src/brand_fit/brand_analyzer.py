<<<<<<< HEAD
"""
Brand Fit Analyzer
Matches influencers with brands based on safety, values, and content fit.
"""

import json
from pathlib import Path
from typing import Dict, List, Union, Optional
import logging

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class BrandFitAnalyzer:
    """Analyzes fit between influencer content and brand requirements"""
    
    def __init__(self, brand_profile_path: Union[str, Path]):
        self.brand_profile = self._load_brand_profile(brand_profile_path)
        logger.info(f"Initialized BrandFitAnalyzer for {self.brand_profile['name']}")
        
    def _load_brand_profile(self, path: Union[str, Path]) -> Dict:
        """Load brand profile from JSON"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load brand profile: {e}")
            raise

    def analyze_fit(self, influencer_results: Dict) -> Dict:
        """
        Analyze fit between influencer and brand.
        
        Args:
            influencer_results: The full output from run_full_pipeline
            
        Returns:
            Dict containing fit score, rating, and detailed report
        """
        logger.info(f"Analyzing brand fit for @{influencer_results['username']} with {self.brand_profile['name']}")
        
        score = 100.0
        reasons = []
        risk_factors = []
        
        # 1. Safety Check (Critical)
        safety_score, safety_risks = self._check_safety(influencer_results)
        if safety_risks:
            score -= (100 - safety_score)
            risk_factors.extend(safety_risks)
            reasons.append(f"Safety violations detected (-{100-safety_score:.1f})")
        
        # 2. Excluded Topics Check
        topic_score, topic_risks = self._check_excluded_topics(influencer_results)
        if topic_risks:
            score -= (100 - topic_score)
            risk_factors.extend(topic_risks)
            reasons.append(f"Excluded topics found (-{100-topic_score:.1f})")
            
        # 3. Values Alignment (Bonus)
        values_score, values_matches = self._check_values_alignment(influencer_results)
        if values_matches:
            score += values_score
            reasons.append(f"Values alignment bonus (+{values_score:.1f})")
            
        # Clamp score
        score = max(0.0, min(100.0, score))
        
        # Determine rating
        if score >= 90: rating = "Perfect Match"
        elif score >= 75: rating = "Good Fit"
        elif score >= 60: rating = "Moderate Risk"
        elif score >= 40: rating = "High Risk"
        else: rating = "Unsafe / Do Not Partner"
        
        return {
            "brand_name": self.brand_profile['name'],
            "fit_score": round(score, 1),
            "rating": rating,
            "risk_factors": risk_factors,
            "reasons": reasons,
            "details": {
                "safety_score": safety_score,
                "topic_score": topic_score,
                "values_score": values_score
            }
        }

    def _check_safety(self, results: Dict) -> (float, List[str]):
        """Check safety thresholds including sub-scores"""
        score = 100.0
        risks = []
        thresholds = self.brand_profile.get("safety_thresholds", {})
        
        # Text Analysis Checks
        ta = results.get("text_analysis", {})
        
        # Check Averages
        if ta.get("avg_toxicity", 0) > thresholds.get("max_toxicity", 1.0):
            penalty = 30
            score -= penalty
            risks.append(f"High average toxicity ({ta['avg_toxicity']:.2f} > {thresholds['max_toxicity']})")
            
        # Check Specific Sub-scores (Critical for "sexist jokes")
        if ta.get("max_identity_attack", 0) > thresholds.get("max_identity_attack", 1.0):
            penalty = 40  # Strict penalty for identity attacks
            score -= penalty
            risks.append(f"Identity attack detected ({ta['max_identity_attack']:.2f} > {thresholds['max_identity_attack']})")
            
        if ta.get("max_insult", 0) > thresholds.get("max_insult", 1.0):
            penalty = 20
            score -= penalty
            risks.append(f"Insulting content detected ({ta['max_insult']:.2f} > {thresholds['max_insult']})")
            
        if ta.get("max_severe_toxicity", 0) > thresholds.get("max_severe_toxicity", 1.0):
            penalty = 50  # Very strict
            score -= penalty
            risks.append(f"Severe toxicity detected ({ta['max_severe_toxicity']:.2f} > {thresholds['max_severe_toxicity']})")
        
        # Check Image Analysis
        ia = results.get("image_analysis", {})
        if ia.get("avg_nsfw_score", 0) > thresholds.get("max_nsfw", 1.0):
            penalty = 40
            score -= penalty
            risks.append(f"NSFW content detected ({ia['avg_nsfw_score']:.2f})")
            
        if ia.get("nsfw_images_found", 0) > 0:
            penalty = 20 * ia["nsfw_images_found"]
            score -= penalty
            risks.append(f"Found {ia['nsfw_images_found']} NSFW images")

        return max(0.0, score), risks

    def _check_excluded_topics(self, results: Dict) -> (float, List[str]):
        """Check for excluded topics in text"""
        score = 100.0
        risks = []
        excluded = self.brand_profile.get("excluded_topics", [])
        
        # We need the full text to do this properly.
        # If the results JSON doesn't contain full text, we can't do deep scanning.
        # But we can check if 'spam_detection' or other metadata gives hints.
        
        # For now, let's assume we might not have full text in the summary JSON.
        # We will implement a basic check if 'top_keywords' exists (future feature)
        # or just return 100 if we can't check.
        
        # TODO: Enhance pipeline to pass top keywords or full text to this analyzer.
        
        return score, risks

    def _check_values_alignment(self, results: Dict) -> (float, List[str]):
        """Check alignment with brand values"""
        score = 0.0
        matches = []
        
        # Sentiment check
        ta = results.get("text_analysis", {})
        if ta.get("avg_sentiment", 0) > 0.5:
            score += 5
            matches.append("Positive sentiment")
            
        return score, matches
=======
"""
Brand Fit Analyzer
Matches influencers with brands based on safety, values, and content fit.
"""

import json
from pathlib import Path
from typing import Dict, List, Union, Optional
import logging

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class BrandFitAnalyzer:
    """Analyzes fit between influencer content and brand requirements"""
    
    def __init__(self, brand_profile_path: Union[str, Path]):
        self.brand_profile = self._load_brand_profile(brand_profile_path)
        logger.info(f"Initialized BrandFitAnalyzer for {self.brand_profile['name']}")
        
    def _load_brand_profile(self, path: Union[str, Path]) -> Dict:
        """Load brand profile from JSON"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load brand profile: {e}")
            raise

    def analyze_fit(self, influencer_results: Dict) -> Dict:
        """
        Analyze fit between influencer and brand.
        
        Args:
            influencer_results: The full output from run_full_pipeline
            
        Returns:
            Dict containing fit score, rating, and detailed report
        """
        logger.info(f"Analyzing brand fit for @{influencer_results['username']} with {self.brand_profile['name']}")
        
        score = 100.0
        reasons = []
        risk_factors = []
        
        # 1. Safety Check (Critical)
        safety_score, safety_risks = self._check_safety(influencer_results)
        if safety_risks:
            score -= (100 - safety_score)
            risk_factors.extend(safety_risks)
            reasons.append(f"Safety violations detected (-{100-safety_score:.1f})")
        
        # 2. Excluded Topics Check
        topic_score, topic_risks = self._check_excluded_topics(influencer_results)
        if topic_risks:
            score -= (100 - topic_score)
            risk_factors.extend(topic_risks)
            reasons.append(f"Excluded topics found (-{100-topic_score:.1f})")
            
        # 3. Values Alignment (Bonus)
        values_score, values_matches = self._check_values_alignment(influencer_results)
        if values_matches:
            score += values_score
            reasons.append(f"Values alignment bonus (+{values_score:.1f})")
            
        # Clamp score
        score = max(0.0, min(100.0, score))
        
        # Determine rating
        if score >= 90: rating = "Perfect Match"
        elif score >= 75: rating = "Good Fit"
        elif score >= 60: rating = "Moderate Risk"
        elif score >= 40: rating = "High Risk"
        else: rating = "Unsafe / Do Not Partner"
        
        return {
            "brand_name": self.brand_profile['name'],
            "fit_score": round(score, 1),
            "rating": rating,
            "risk_factors": risk_factors,
            "reasons": reasons,
            "details": {
                "safety_score": safety_score,
                "topic_score": topic_score,
                "values_score": values_score
            }
        }

    def _check_safety(self, results: Dict) -> (float, List[str]):
        """Check safety thresholds including sub-scores"""
        score = 100.0
        risks = []
        thresholds = self.brand_profile.get("safety_thresholds", {})
        
        # Text Analysis Checks
        ta = results.get("text_analysis", {})
        
        # Check Averages
        if ta.get("avg_toxicity", 0) > thresholds.get("max_toxicity", 1.0):
            penalty = 30
            score -= penalty
            risks.append(f"High average toxicity ({ta['avg_toxicity']:.2f} > {thresholds['max_toxicity']})")
            
        # Check Specific Sub-scores (Critical for "sexist jokes")
        if ta.get("max_identity_attack", 0) > thresholds.get("max_identity_attack", 1.0):
            penalty = 40  # Strict penalty for identity attacks
            score -= penalty
            risks.append(f"Identity attack detected ({ta['max_identity_attack']:.2f} > {thresholds['max_identity_attack']})")
            
        if ta.get("max_insult", 0) > thresholds.get("max_insult", 1.0):
            penalty = 20
            score -= penalty
            risks.append(f"Insulting content detected ({ta['max_insult']:.2f} > {thresholds['max_insult']})")
            
        if ta.get("max_severe_toxicity", 0) > thresholds.get("max_severe_toxicity", 1.0):
            penalty = 50  # Very strict
            score -= penalty
            risks.append(f"Severe toxicity detected ({ta['max_severe_toxicity']:.2f} > {thresholds['max_severe_toxicity']})")
        
        # Check Image Analysis
        ia = results.get("image_analysis", {})
        if ia.get("avg_nsfw_score", 0) > thresholds.get("max_nsfw", 1.0):
            penalty = 40
            score -= penalty
            risks.append(f"NSFW content detected ({ia['avg_nsfw_score']:.2f})")
            
        if ia.get("nsfw_images_found", 0) > 0:
            penalty = 20 * ia["nsfw_images_found"]
            score -= penalty
            risks.append(f"Found {ia['nsfw_images_found']} NSFW images")

        return max(0.0, score), risks

    def _check_excluded_topics(self, results: Dict) -> (float, List[str]):
        """Check for excluded topics in text"""
        score = 100.0
        risks = []
        excluded = self.brand_profile.get("excluded_topics", [])
        
        # We need the full text to do this properly.
        # If the results JSON doesn't contain full text, we can't do deep scanning.
        # But we can check if 'spam_detection' or other metadata gives hints.
        
        # For now, let's assume we might not have full text in the summary JSON.
        # We will implement a basic check if 'top_keywords' exists (future feature)
        # or just return 100 if we can't check.
        
        # TODO: Enhance pipeline to pass top keywords or full text to this analyzer.
        
        return score, risks

    def _check_values_alignment(self, results: Dict) -> (float, List[str]):
        """Check alignment with brand values"""
        score = 0.0
        matches = []
        
        # Sentiment check
        ta = results.get("text_analysis", {})
        if ta.get("avg_sentiment", 0) > 0.5:
            score += 5
            matches.append("Positive sentiment")
            
        return score, matches
>>>>>>> 8bf316f0f1e5a33d7051e28b6dde11854481b5fc
