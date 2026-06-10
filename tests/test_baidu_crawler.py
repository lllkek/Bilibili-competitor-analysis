from pathlib import Path
import sys


# 找到项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 把项目根目录加入 Python 搜索路径
sys.path.append(str(PROJECT_ROOT))


from src.crawlers.baidu_hot_crawler import BaiduHotCrawler


def test_baidu_crawler_init():
    """
    测试 BaiduHotCrawler 能不能正常创建对象。
    """

    crawler = BaiduHotCrawler(
        top_n=5,
        save_mysql=False,
        save_csv=False
    )

    assert crawler.top_n == 5
    assert crawler.save_mysql is False
    assert crawler.save_csv is False


def test_baidu_crawler_crawl():
    """
    测试百度热搜爬虫能不能正常返回数据。
    """

    crawler = BaiduHotCrawler(
        top_n=5,
        save_mysql=False,
        save_csv=False
    )

    data = crawler.crawl()

    assert isinstance(data, list)
    assert len(data) > 0
    assert len(data) <= 5

    first_item = data[0]

    required_fields = [
        "rank_no",
        "keyword",
        "hot_score",
        "url",
        "crawl_time"
    ]

    for field in required_fields:
        assert field in first_item

    assert first_item["rank_no"] == 1
    assert first_item["keyword"] != ""
    assert first_item["crawl_time"] != ""


if __name__ == "__main__":
    test_baidu_crawler_init()
    test_baidu_crawler_crawl()

    print("百度热搜爬虫测试通过")