from pathlib import Path
import sys


# 找到项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 把项目根目录加入 Python 的搜索路径
# 这样才能正常 import src 和 config 里面的文件
sys.path.append(str(PROJECT_ROOT))


from src.crawlers.baidu_hot_crawler import BaiduHotCrawler


def main():
    """
    百度热搜爬虫运行入口。

    这里不写具体爬虫逻辑，只负责调用 BaiduHotCrawler 这个类。
    """

    crawler = BaiduHotCrawler(
        top_n=10,
        save_mysql=True,
        save_csv=True
    )

    data = crawler.run()

    print("本次爬取结果预览：")
    for item in data:
        print(item)


if __name__ == "__main__":
    main()