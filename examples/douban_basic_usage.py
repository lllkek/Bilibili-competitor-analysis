from pathlib import Path
import sys


# 找到项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 把项目根目录加入 Python 搜索路径
sys.path.append(str(PROJECT_ROOT))


from src.crawlers.douban_movie_crawler import DoubanMovieCrawler


# 示例：爬取豆瓣电影 Top100，并保存到 MySQL 和 CSV
# top_n：控制爬取多少部电影
# save_mysql：是否保存到 MySQL
# save_csv：是否保存为 CSV
# fields：控制需要保存哪些字段

crawler = DoubanMovieCrawler(
    top_n=100,
    save_mysql=True,
    save_csv=False,
    fields=[
        "rank_no",
        "movie_name",
        "director",
        "actors",
        "rating_score",
        "rating_count",
        "release_year",
        "genres",
        "duration_minutes",
        "country",
        "crawl_time"
        
    ]
)

data = crawler.run()

print("豆瓣电影爬取结果预览：")
for item in data[:5]:
    print(item)