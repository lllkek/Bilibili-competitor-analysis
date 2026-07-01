from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.analyzers.rule_based_reason_analyzer import RuleBasedReasonAnalyzer


analyzer = RuleBasedReasonAnalyzer(
    top_keywords_count=8
)

analyzer.run()