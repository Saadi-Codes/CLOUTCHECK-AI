# Image Analysis Model Replacement Plan

## Goal
Replace the "Fallback Heuristic Analyzer" (placeholder) with a functional AI model for NSFW detection that runs natively in Python without Windows DLL conflicts.

## 1. Model Selection
- **Model**: `Falconsai/nsfw_image_detection` (Hugging Face)
- **Architecture**: Vision Transformer (ViT)
- **Library**: `transformers` + `torch` (Already installed and working for text)

## 2. Implementation (`src/models/image_nsfw.py`)
- Remove `Basic Heuristics` logic.
- Implement `transformers.pipeline("image-classification")`.
- Map model outputs (Normal vs NSFW) to our score format (0.0 to 1.0).

## 3. Benefits
- **No DLL Hell**: Uses pure PyTorch/Transformers.
- **Accuracy**: Real AI detection instead of a placeholder.
- **Compatibility**: Works on Windows/Linux/Mac.

## 4. Verification
- Run `python src/models/image_nsfw.py` on a sample image.
- Verify it returns a real confidence score.
