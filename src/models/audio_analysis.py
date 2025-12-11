<<<<<<< HEAD
"""
Audio analysis using Whisper for speech-to-text transcription.
Transcribes audio and passes to text analysis models.
"""

import warnings
warnings.filterwarnings('ignore')

from typing import Dict, Union, Optional
from pathlib import Path
import whisper
import torch

from src.config import AUDIO_WHISPER_MODEL, DEVICE, get_model_cache_path
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class AudioAnalyzer:
    """Audio transcription and analysis using Whisper"""
    
    def __init__(self, model_size: str = None):
        """
        Initialize Whisper model.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size or AUDIO_WHISPER_MODEL
        self.device = DEVICE
        
        logger.info(f"Loading Whisper model: {self.model_size} on {self.device}")
        
        try:
            self.model = whisper.load_model(self.model_size, device=self.device)
            logger.info(f"Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe_audio(
        self,
        audio_path: Union[str, Path],
        language: str = None
    ) -> Dict[str, Union[str, float, Dict]]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)
            language: Language code (e.g., 'en', 'es') or None for auto-detect
        
        Returns:
            Dictionary with transcription results
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            logger.error(f"Audio file not found: {audio_path}")
            return self._default_result()
        
        try:
            logger.info(f"Transcribing {audio_path.name}...")
            
            # Transcribe
            result = self.model.transcribe(
                str(audio_path),
                language=language,
                fp16=False  # Use FP32 for CPU compatibility
            )
            
            text = result.get("text", "").strip()
            detected_language = result.get("language", "unknown")
            
            # Extract segments with timestamps
            segments = []
            if "segments" in result:
                for seg in result["segments"]:
                    segments.append({
                        "start": seg.get("start", 0),
                        "end": seg.get("end", 0),
                        "text": seg.get("text", "").strip()
                    })
            
            logger.info(f"Transcription complete: {len(text)} characters, {len(segments)} segments")
            
            return {
                "audio_path": str(audio_path),
                "transcription": text,
                "language": detected_language,
                "segments": segments,
                "segment_count": len(segments),
                "character_count": len(text),
                "word_count": len(text.split()) if text else 0,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio {audio_path}: {e}")
            return self._default_result()
    
    def detect_language(self, audio_path: Union[str, Path]) -> str:
        """
        Detect language in audio file.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Language code (e.g., 'en', 'es')
        """
        try:
            # Load audio
            audio = whisper.load_audio(str(audio_path))
            audio = whisper.pad_or_trim(audio)
            
            # Make log-Mel spectrogram
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            
            # Detect language
            _, probs = self.model.detect_language(mel)
            detected_lang = max(probs, key=probs.get)
            
            logger.info(f"Detected language: {detected_lang} (confidence: {probs[detected_lang]:.2f})")
            
            return detected_lang
            
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return "unknown"
    
    def _default_result(self) -> Dict:
        """Return default result for failed transcription"""
        return {
            "audio_path": None,
            "transcription": "",
            "language": "unknown",
            "segments": [],
            "segment_count": 0,
            "character_count": 0,
            "word_count": 0,
            "success": False
        }
    
    def analyze_audio_with_text_model(self, audio_path: Union[str, Path]) -> Dict:
        """
        Transcribe audio and analyze with text models.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Combined audio + text analysis results
        """
        # Transcribe
        transcription_result = self.transcribe_audio(audio_path)
        
        if not transcription_result["success"] or not transcription_result["transcription"]:
            logger.warning(f"No transcription for {audio_path}, skipping text analysis")
            return transcription_result
        
        # Analyze transcribed text
        try:
            from src.models.text_toxicity import get_text_analyzer
            text_analyzer = get_text_analyzer()
            
            text_analysis = text_analyzer.analyze_text(transcription_result["transcription"])
            spam_detection = text_analyzer.detect_spam_patterns(transcription_result["transcription"])
            
            # Combine results
            combined = {
                **transcription_result,
                "text_analysis": text_analysis,
                "spam_detection": spam_detection
            }
            
            return combined
            
        except Exception as e:
            logger.error(f"Error in text analysis of transcription: {e}")
            return transcription_result


# Global instance for reuse
_audio_analyzer_instance = None


def get_audio_analyzer() -> AudioAnalyzer:
    """Get or create global AudioAnalyzer instance"""
    global _audio_analyzer_instance
    if _audio_analyzer_instance is None:
        _audio_analyzer_instance = AudioAnalyzer()
    return _audio_analyzer_instance


if __name__ == "__main__":
    # Test the analyzer
    import sys
    
    if len(sys.argv) > 1:
        audio_file = Path(sys.argv[1])
        if audio_file.exists():
            analyzer = AudioAnalyzer()
            
            print("\n" + "="*70)
            print(f"AUDIO ANALYSIS TEST: {audio_file.name}")
            print("="*70)
            
            # Transcribe
            result = analyzer.transcribe_audio(audio_file)
            
            print(f"\nTranscription:")
            print(f"  Language: {result['language']}")
            print(f"  Words: {result['word_count']}")
            print(f"  Segments: {result['segment_count']}")
            print(f"\nText:")
            print(f"  {result['transcription'][:200]}{'...' if len(result['transcription']) > 200 else ''}")
            
            # Show segments
            if result['segments']:
                print(f"\nSegments:")
                for i, seg in enumerate(result['segments'][:3]):
                    print(f"  [{seg['start']:.1f}s - {seg['end']:.1f}s]: {seg['text']}")
            
        else:
            print(f"Audio file not found: {audio_file}")
    else:
        print("Usage: python audio_analysis.py <audio_file>")
=======
"""
Audio analysis using Whisper for speech-to-text transcription.
Transcribes audio and passes to text analysis models.
"""

import warnings
warnings.filterwarnings('ignore')

from typing import Dict, Union, Optional
from pathlib import Path
import whisper
import torch

from src.config import AUDIO_WHISPER_MODEL, DEVICE, get_model_cache_path
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class AudioAnalyzer:
    """Audio transcription and analysis using Whisper"""
    
    def __init__(self, model_size: str = None):
        """
        Initialize Whisper model.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size or AUDIO_WHISPER_MODEL
        self.device = DEVICE
        
        logger.info(f"Loading Whisper model: {self.model_size} on {self.device}")
        
        try:
            self.model = whisper.load_model(self.model_size, device=self.device)
            logger.info(f"Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe_audio(
        self,
        audio_path: Union[str, Path],
        language: str = None
    ) -> Dict[str, Union[str, float, Dict]]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)
            language: Language code (e.g., 'en', 'es') or None for auto-detect
        
        Returns:
            Dictionary with transcription results
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            logger.error(f"Audio file not found: {audio_path}")
            return self._default_result()
        
        try:
            logger.info(f"Transcribing {audio_path.name}...")
            
            # Transcribe
            result = self.model.transcribe(
                str(audio_path),
                language=language,
                fp16=False  # Use FP32 for CPU compatibility
            )
            
            text = result.get("text", "").strip()
            detected_language = result.get("language", "unknown")
            
            # Extract segments with timestamps
            segments = []
            if "segments" in result:
                for seg in result["segments"]:
                    segments.append({
                        "start": seg.get("start", 0),
                        "end": seg.get("end", 0),
                        "text": seg.get("text", "").strip()
                    })
            
            logger.info(f"Transcription complete: {len(text)} characters, {len(segments)} segments")
            
            return {
                "audio_path": str(audio_path),
                "transcription": text,
                "language": detected_language,
                "segments": segments,
                "segment_count": len(segments),
                "character_count": len(text),
                "word_count": len(text.split()) if text else 0,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio {audio_path}: {e}")
            return self._default_result()
    
    def detect_language(self, audio_path: Union[str, Path]) -> str:
        """
        Detect language in audio file.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Language code (e.g., 'en', 'es')
        """
        try:
            # Load audio
            audio = whisper.load_audio(str(audio_path))
            audio = whisper.pad_or_trim(audio)
            
            # Make log-Mel spectrogram
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            
            # Detect language
            _, probs = self.model.detect_language(mel)
            detected_lang = max(probs, key=probs.get)
            
            logger.info(f"Detected language: {detected_lang} (confidence: {probs[detected_lang]:.2f})")
            
            return detected_lang
            
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return "unknown"
    
    def _default_result(self) -> Dict:
        """Return default result for failed transcription"""
        return {
            "audio_path": None,
            "transcription": "",
            "language": "unknown",
            "segments": [],
            "segment_count": 0,
            "character_count": 0,
            "word_count": 0,
            "success": False
        }
    
    def analyze_audio_with_text_model(self, audio_path: Union[str, Path]) -> Dict:
        """
        Transcribe audio and analyze with text models.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Combined audio + text analysis results
        """
        # Transcribe
        transcription_result = self.transcribe_audio(audio_path)
        
        if not transcription_result["success"] or not transcription_result["transcription"]:
            logger.warning(f"No transcription for {audio_path}, skipping text analysis")
            return transcription_result
        
        # Analyze transcribed text
        try:
            from src.models.text_toxicity import get_text_analyzer
            text_analyzer = get_text_analyzer()
            
            text_analysis = text_analyzer.analyze_text(transcription_result["transcription"])
            spam_detection = text_analyzer.detect_spam_patterns(transcription_result["transcription"])
            
            # Combine results
            combined = {
                **transcription_result,
                "text_analysis": text_analysis,
                "spam_detection": spam_detection
            }
            
            return combined
            
        except Exception as e:
            logger.error(f"Error in text analysis of transcription: {e}")
            return transcription_result


# Global instance for reuse
_audio_analyzer_instance = None


def get_audio_analyzer() -> AudioAnalyzer:
    """Get or create global AudioAnalyzer instance"""
    global _audio_analyzer_instance
    if _audio_analyzer_instance is None:
        _audio_analyzer_instance = AudioAnalyzer()
    return _audio_analyzer_instance


if __name__ == "__main__":
    # Test the analyzer
    import sys
    
    if len(sys.argv) > 1:
        audio_file = Path(sys.argv[1])
        if audio_file.exists():
            analyzer = AudioAnalyzer()
            
            print("\n" + "="*70)
            print(f"AUDIO ANALYSIS TEST: {audio_file.name}")
            print("="*70)
            
            # Transcribe
            result = analyzer.transcribe_audio(audio_file)
            
            print(f"\nTranscription:")
            print(f"  Language: {result['language']}")
            print(f"  Words: {result['word_count']}")
            print(f"  Segments: {result['segment_count']}")
            print(f"\nText:")
            print(f"  {result['transcription'][:200]}{'...' if len(result['transcription']) > 200 else ''}")
            
            # Show segments
            if result['segments']:
                print(f"\nSegments:")
                for i, seg in enumerate(result['segments'][:3]):
                    print(f"  [{seg['start']:.1f}s - {seg['end']:.1f}s]: {seg['text']}")
            
        else:
            print(f"Audio file not found: {audio_file}")
    else:
        print("Usage: python audio_analysis.py <audio_file>")
>>>>>>> 8bf316f0f1e5a33d7051e28b6dde11854481b5fc
