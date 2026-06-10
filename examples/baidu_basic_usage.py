from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))


from src.crawlers.baidu_hot_crawler import BaiduHotCrawler


crawler = BaiduHotCrawler(
    top_n=10,
    save_mysql=True,
    save_csv=True
)

crawler.run()