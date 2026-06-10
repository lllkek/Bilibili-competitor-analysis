from pathlib import Path
import sys


# 找到项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 把项目根目录加入 Python 搜索路径
sys.path.append(str(PROJECT_ROOT))


from src.crawlers.douban_movie_crawler import DoubanMovieCrawler


def main():
    """
    豆瓣电影 Top100 爬虫运行入口。

    这里不写具体爬虫逻辑，只负责调用 DoubanMovieCrawler 这个类。
    """

    crawler = DoubanMovieCrawler(
        top_n=100,
        save_mysql=True,
        save_csv=True
    )

    data = crawler.run()

    print("本次爬取结果预览：")
    for item in data[:5]:
        print(item)


if __name__ == "__main__":
    main()