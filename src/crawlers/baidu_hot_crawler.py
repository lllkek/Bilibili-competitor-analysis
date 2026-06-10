import csv
import random
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config.config import BAIDU_HEADERS, CRAWLER_CONFIG, DB_CONFIG
from src.utils.mysql_helper import MySqlHelper


class BaiduHotCrawler:
    """
    百度热搜爬虫类。

    主要功能：
    1. 请求百度热搜页面
    2. 解析热搜排名、关键词、热度值、链接、爬取时间
    3. 保存到 MySQL
    4. 保存到 CSV
    """

    def __init__(self, top_n=10, save_mysql=True, save_csv=True):
        self.top_n = top_n
        self.save_mysql = save_mysql
        self.save_csv = save_csv

        self.base_url = "https://top.baidu.com/board?tab=realtime"
        self.headers = BAIDU_HEADERS

        self.min_sleep = CRAWLER_CONFIG.get("min_sleep", 1)
        self.max_sleep = CRAWLER_CONFIG.get("max_sleep", 2)
        self.timeout = CRAWLER_CONFIG.get("timeout", 10)

        self.project_root = Path(__file__).resolve().parents[2]
        self.result_path = self.project_root / "results" / "baidu_hot_search_top10.csv"
        self.debug_path = self.project_root / "results" / "baidu_debug.html"

    def get_html(self, url):
        """
        请求网页，返回 HTML 文本。
        """

        sleep_time = random.uniform(self.min_sleep, self.max_sleep)
        print(f"等待 {sleep_time:.2f} 秒后访问网页：{url}")
        time.sleep(sleep_time)

        response = requests.get(
            url,
            headers=self.headers,
            timeout=self.timeout
        )
        response.encoding = "utf-8"

        print("网页状态码:", response.status_code)

        if response.status_code != 200:
            self.debug_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.debug_path, "w", encoding="utf-8") as f:
                f.write(response.text)

            raise Exception(f"网页访问失败，状态码：{response.status_code}，调试文件已保存：{self.debug_path}")

        return response.text

    def parse_page(self, html):
        """
        解析百度热搜页面，返回热搜数据列表。
        """

        soup = BeautifulSoup(html, "lxml")
        items = soup.select("div[class*='category-wrap']")

        if not items:
            self.debug_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.debug_path, "w", encoding="utf-8") as f:
                f.write(html)

            raise Exception(f"没有解析到热搜数据，可能是网页结构变化，调试文件已保存：{self.debug_path}")

        hot_list = []
        crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for rank_no, item in enumerate(items[:self.top_n], start=1):
            title_tag = item.select_one("div[class*='c-single-text-ellipsis']")
            hot_tag = item.select_one("div[class*='hot-index']")
            link_tag = item.select_one("a[href]")

            keyword = title_tag.get_text(strip=True) if title_tag else ""
            hot_score = hot_tag.get_text(strip=True) if hot_tag else ""
            url = link_tag.get("href") if link_tag else ""

            hot_score = re.sub(r"\s+", "", hot_score)

            if url:
                url = urljoin(self.base_url, url)

            hot_list.append(
                {
                    "rank_no": rank_no,
                    "keyword": keyword,
                    "hot_score": hot_score,
                    "url": url,
                    "crawl_time": crawl_time
                }
            )

        return hot_list

    def crawl(self):
        """
        执行爬取和解析，返回数据列表。
        """

        html = self.get_html(self.base_url)
        hot_list = self.parse_page(html)

        print(f"成功解析百度热搜数据：{len(hot_list)} 条")

        return hot_list

    def save_to_mysql(self, data):
        """
        将百度热搜数据保存到 MySQL。
        """

        if not data:
            print("没有数据需要写入 MySQL")
            return

        db = MySqlHelper(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            charset=DB_CONFIG["charset"]
        )

        sql = """
        INSERT INTO baidu_hot_search
        (rank_no, keyword, hot_score, url, crawl_time)
        VALUES (%s, %s, %s, %s, %s)
        """

        data_list = []

        for item in data:
            data_list.append(
                (
                    item["rank_no"],
                    item["keyword"],
                    item["hot_score"],
                    item["url"],
                    item["crawl_time"]
                )
            )

        db.executemany(sql, data_list)

        print("百度热搜数据已写入 MySQL")

    def save_to_csv(self, data):
        """
        将百度热搜数据保存到 CSV。
        """

        if not data:
            print("没有数据需要保存为 CSV")
            return

        self.result_path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "rank_no",
            "keyword",
            "hot_score",
            "url",
            "crawl_time"
        ]

        with open(self.result_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        print(f"百度热搜数据已保存为 CSV：{self.result_path}")

    def run(self):
        """
        百度热搜爬虫总入口。

        运行顺序：
        1. 爬取网页
        2. 解析数据
        3. 写入 MySQL
        4. 保存 CSV
        5. 返回数据
        """

        data = self.crawl()

        if self.save_mysql:
            self.save_to_mysql(data)

        if self.save_csv:
            self.save_to_csv(data)

        print("百度热搜爬虫运行完成")

        return data