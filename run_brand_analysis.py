"""
Standalone script to run Brand Fit Analysis on existing results.
Usage: python run_brand_analysis.py
"""

import json
from pathlib import Path
from src.brand_fit.brand_analyzer import BrandFitAnalyzer
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    print("\n" + "="*70)
    print("  CLOUTCHECK AI - BRAND FIT ANALYZER")
    print("="*70)

    # 1. Find existing analysis results
    results_dir = Path("results")
    if not results_dir.exists():
        print("No results found. Please run the full pipeline first.")
        return

    analysis_files = list(results_dir.glob("*_analysis.json"))
    if not analysis_files:
        print("No analysis files found in results/ directory.")
        return

    # 2. Find brand profiles
    brands_dir = Path("brands")
    if not brands_dir.exists():
        print("No brands/ directory found.")
        return

    brand_files = list(brands_dir.glob("*.json"))
    if not brand_files:
        print("No brand profiles found in brands/ directory.")
        return

    print(f"Found {len(analysis_files)} influencer reports and {len(brand_files)} brand profiles.\n")

    # 3. Run Analysis
    for analysis_file in analysis_files:
        with open(analysis_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        username = results.get("username", "unknown")
        print(f"Analyzing fit for @{username}...")

        brand_fits = []
        for brand_file in brand_files:
            try:
                analyzer = BrandFitAnalyzer(brand_file)
                fit_result = analyzer.analyze_fit(results)
                brand_fits.append(fit_result)
                
                # Print Result
                print(f"   -> {fit_result['brand_name']}: {fit_result['fit_score']}/100 ({fit_result['rating']})")
                if fit_result['risk_factors']:
                    print(f"      Risks: {', '.join(fit_result['risk_factors'])}")
            
            except Exception as e:
                print(f"   Error analyzing {brand_file.name}: {e}")
        
        # Update the JSON file with new brand fits
        results["brand_fits"] = brand_fits
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"   Updated {analysis_file.name}\n")

    print("="*70)
    print("Done! You can add more brands to 'brands/' and run this script again.")

if __name__ == "__main__":
    main()
