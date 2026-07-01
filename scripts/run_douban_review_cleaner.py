from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.analyzers.review_text_cleaner import ReviewTextCleaner


cleaner = ReviewTextCleaner(
    min_text_length=4
)

cleaner.run()