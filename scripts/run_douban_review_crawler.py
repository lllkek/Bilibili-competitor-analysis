from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.crawlers.douban_review_crawler import DoubanReviewCrawler


crawler = DoubanReviewCrawler(
    movie_limit=100,
    comments_per_sentiment=30,
    sentiment_types=["positive", "neutral", "negative"],
    save_mysql=True,
    save_csv=True
)

crawler.run()