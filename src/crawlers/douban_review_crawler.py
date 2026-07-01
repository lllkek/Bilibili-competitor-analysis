import csv
import random
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config.config import DOUBAN_HEADERS, CRAWLER_CONFIG, DB_CONFIG
from src.utils.mysql_helper import MySqlHelper


class DoubanReviewCrawler:
    """
    豆瓣电影短评爬虫类。

    现在的核心目标不是简单判断情感正负面，
    而是分别爬取豆瓣已经筛选好的：
    1. 好评短评 positive
    2. 一般短评 neutral
    3. 差评短评 negative

    后续再分析不同情绪类别下，用户为什么产生这种评价。
    """

    DEFAULT_FIELDS = [
        "movie_name",
        "movie_url",
        "comment_url",
        "comment_sentiment_type",
        "user_name",
        "review_text",
        "review_star",
        "review_time",
        "review_like_count",
        "crawl_time"
    ]

    SENTIMENT_FILTERS = {
        "positive": {
            "percent_type": "h",
            "label": "好评"
        },
        "neutral": {
            "percent_type": "m",
            "label": "一般"
        },
        "negative": {
            "percent_type": "l",
            "label": "差评"
        }
    }

    def __init__(
        self,
        movie_limit=5,
        comments_per_sentiment=20,
        sentiment_types=None,
        save_mysql=True,
        save_csv=True
    ):
        """
        movie_limit:
            爬取多少部电影。测试阶段先用 5。

        comments_per_sentiment:
            每部电影每种情绪类别爬多少条。
            例如 20 表示：
            每部电影爬 20 条好评 + 20 条一般 + 20 条差评。

        sentiment_types:
            控制爬哪些类别。
            默认爬 positive、neutral、negative 三类。
        """

        self.movie_limit = movie_limit
        self.comments_per_sentiment = comments_per_sentiment
        self.save_mysql = save_mysql
        self.save_csv = save_csv

        if sentiment_types is None:
            self.sentiment_types = ["positive", "neutral", "negative"]
        else:
            self.sentiment_types = sentiment_types

        self.fields = self.DEFAULT_FIELDS
        self.headers = DOUBAN_HEADERS

        self.min_sleep = CRAWLER_CONFIG.get("min_sleep", 1)
        self.max_sleep = CRAWLER_CONFIG.get("max_sleep", 2)
        self.timeout = CRAWLER_CONFIG.get("timeout", 10)

        self.project_root = Path(__file__).resolve().parents[2]
        self.result_path = self.project_root / "results" / "douban_movie_reviews.csv"
        self.debug_path = self.project_root / "results" / "douban_review_debug.html"

    def _get_database(self):
        """
        创建 MySQL 工具对象。
        """

        db = MySqlHelper(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            charset=DB_CONFIG["charset"]
        )

        return db

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

            raise Exception(
                f"网页访问失败，状态码：{response.status_code}，"
                f"调试文件已保存：{self.debug_path}"
            )

        return response.text

    def load_movies_from_mysql(self):
        """
        从 douban_movie_top100 表读取电影名称和电影详情页链接。
        """

        db = self._get_database()

        sql = """
            SELECT
                movie_name,
                movie_url
            FROM douban_movie_top100
            WHERE movie_url IS NOT NULL
              AND movie_url != ''
            ORDER BY rank_no
            LIMIT %s;
        """

        movies = db.query(sql, (self.movie_limit,))

        print(f"从 MySQL 读取到电影数量：{len(movies)}")

        return movies

    def build_comment_url(self, movie_url, sentiment_type, start=0):
        """
        根据电影详情页 URL 拼接短评页 URL。

        豆瓣短评里的 percent_type 通常表示：
        h：好评
        m：一般
        l：差评

        例如：
        https://movie.douban.com/subject/1292052/comments?percent_type=h&start=0&limit=20&status=P&sort=new_score
        """

        if sentiment_type not in self.SENTIMENT_FILTERS:
            raise ValueError(f"不支持的 sentiment_type：{sentiment_type}")

        percent_type = self.SENTIMENT_FILTERS[sentiment_type]["percent_type"]

        base_comment_url = urljoin(movie_url, "comments")

        comment_url = (
            f"{base_comment_url}"
            f"?percent_type={percent_type}"
            f"&start={start}"
            f"&limit=20"
            f"&status=P"
            f"&sort=new_score"
        )

        return comment_url

    def parse_review_star(self, star_class_list):
        """
        从豆瓣星级 class 中提取星级。

        例如：
        allstar50 rating → 5
        allstar40 rating → 4
        allstar30 rating → 3
        """

        if not star_class_list:
            return None

        class_text = " ".join(star_class_list)

        match = re.search(r"allstar(\d+)", class_text)

        if not match:
            return None

        star_value = int(match.group(1))

        return star_value // 10

    def parse_like_count(self, like_text):
        """
        提取点赞数。
        """

        if not like_text:
            return 0

        match = re.search(r"\d+", like_text)

        if not match:
            return 0

        return int(match.group())

    def parse_review_time(self, time_text):
        """
        解析评论时间。

        豆瓣短评时间常见格式：
        2008-02-27 21:43:23
        2008-02-27 21:43
        2008-02-27
        """

        if not time_text:
            return None

        time_text = time_text.strip()
        time_text = re.sub(r"\s+", " ", time_text)

        possible_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d"
        ]

        for time_format in possible_formats:
            try:
                parsed_time = datetime.strptime(time_text, time_format)
                return parsed_time.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

        return None

    def parse_comment_page(
        self,
        html,
        movie_name,
        movie_url,
        comment_url,
        sentiment_type
    ):
        """
        解析短评页面，提取短评数据。
        """

        soup = BeautifulSoup(html, "lxml")

        comment_items = soup.select("div.comment-item")

        review_list = []
        crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sentiment_label = self.SENTIMENT_FILTERS[sentiment_type]["label"]

        print(f"页面中找到 comment-item 数量：{len(comment_items)}")
        print(f"当前评论类别：{sentiment_label} / {sentiment_type}")

        for item in comment_items:
            user_tag = item.select_one("span.comment-info a")
            user_name = user_tag.get_text(strip=True) if user_tag else ""

            review_tag = item.select_one("span.short")
            review_text = review_tag.get_text(strip=True) if review_tag else ""

            star_tag = item.select_one("span.comment-info span[class*='allstar']")
            review_star = None

            if star_tag:
                review_star = self.parse_review_star(star_tag.get("class"))

            time_tag = item.select_one(".comment-time")
            review_time = None

            if time_tag:
                review_time_text = time_tag.get("title") or time_tag.get_text(strip=True)
                review_time = self.parse_review_time(review_time_text)

            like_tag = item.select_one("span.votes")
            review_like_count = 0

            if like_tag:
                review_like_count = self.parse_like_count(like_tag.get_text(strip=True))

            if not review_text:
                continue

            review_data = {
                "movie_name": movie_name,
                "movie_url": movie_url,
                "comment_url": comment_url,
                "comment_sentiment_type": sentiment_type,
                "user_name": user_name,
                "review_text": review_text,
                "review_star": review_star,
                "review_time": review_time,
                "review_like_count": review_like_count,
                "crawl_time": crawl_time
            }

            review_list.append(review_data)

        return review_list

    def crawl_reviews_for_movie_and_sentiment(self, movie, sentiment_type):
        """
        爬取单部电影某一种情绪类别的短评。
        """

        movie_name = movie["movie_name"]
        movie_url = movie["movie_url"]

        sentiment_label = self.SENTIMENT_FILTERS[sentiment_type]["label"]

        print(f"\n正在爬取电影：{movie_name}")
        print(f"评论类别：{sentiment_label} / {sentiment_type}")

        all_reviews = []
        start = 0

        while len(all_reviews) < self.comments_per_sentiment:
            comment_url = self.build_comment_url(
                movie_url=movie_url,
                sentiment_type=sentiment_type,
                start=start
            )

            print(f"短评页：{comment_url}")

            html = self.get_html(comment_url)

            reviews = self.parse_comment_page(
                html=html,
                movie_name=movie_name,
                movie_url=movie_url,
                comment_url=comment_url,
                sentiment_type=sentiment_type
            )

            if not reviews:
                print(f"{movie_name} - {sentiment_label} 没有解析到更多短评，停止当前类别。")
                break

            all_reviews.extend(reviews)

            print(f"{movie_name} - {sentiment_label} 当前累计短评数量：{len(all_reviews)}")

            if len(reviews) < 20:
                print(f"{movie_name} - {sentiment_label} 当前页不足 20 条，可能已经到最后一页。")
                break

            start += 20

        all_reviews = all_reviews[:self.comments_per_sentiment]

        print(f"{movie_name} - {sentiment_label} 最终保留短评数量：{len(all_reviews)}")

        if all_reviews:
            print("第一条短评时间检查：", all_reviews[0].get("review_time"))
            print("第一条短评星级检查：", all_reviews[0].get("review_star"))

        return all_reviews

    def crawl_reviews_for_movie(self, movie):
        """
        爬取单部电影的好评、一般、差评短评。
        """

        movie_name = movie["movie_name"]

        print(f"\n开始处理电影：{movie_name}")

        movie_reviews = []

        for sentiment_type in self.sentiment_types:
            try:
                sentiment_reviews = self.crawl_reviews_for_movie_and_sentiment(
                    movie=movie,
                    sentiment_type=sentiment_type
                )

                movie_reviews.extend(sentiment_reviews)

            except Exception as error:
                sentiment_label = self.SENTIMENT_FILTERS.get(
                    sentiment_type,
                    {}
                ).get("label", sentiment_type)

                print(f"{movie_name} - {sentiment_label} 短评爬取失败")
                print(error)

        print(f"{movie_name} 三类短评合计数量：{len(movie_reviews)}")

        return movie_reviews

    def crawl(self):
        """
        执行完整短评爬取流程。
        """

        movies = self.load_movies_from_mysql()
        all_reviews = []

        for index, movie in enumerate(movies, start=1):
            print(f"\n正在处理第 {index}/{len(movies)} 部电影")

            try:
                reviews = self.crawl_reviews_for_movie(movie)
                all_reviews.extend(reviews)

            except Exception as error:
                print(f"电影短评爬取失败：{movie.get('movie_name')}")
                print(error)

        print(f"\n本次共爬取短评数量：{len(all_reviews)}")

        return all_reviews

    def save_to_csv(self, data):
        """
        保存短评数据到 CSV。
        """

        if not data:
            print("没有短评数据需要保存到 CSV")
            return

        self.result_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.result_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fields)
            writer.writeheader()
            writer.writerows(data)

        print(f"豆瓣电影短评已保存到 CSV：{self.result_path}")

    def save_to_mysql(self, data):
        """
        保存短评数据到 MySQL。
        """

        if not data:
            print("没有短评数据需要写入 MySQL")
            return

        db = self._get_database()

        columns = self.fields
        column_names = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))

        sql = f"""
        INSERT INTO douban_movie_reviews
        ({column_names})
        VALUES ({placeholders})
        """

        data_list = []

        for item in data:
            row = []

            for field in columns:
                value = item.get(field)

                if field in ["review_star", "review_like_count"]:
                    value = int(value) if value not in ["", None] else None

                row.append(value)

            data_list.append(tuple(row))

        db.executemany(sql, data_list)

        print("豆瓣电影短评已写入 MySQL")

    def run(self):
        """
        豆瓣短评爬虫总入口。
        """

        data = self.crawl()

        if self.save_mysql:
            self.save_to_mysql(data)

        if self.save_csv:
            self.save_to_csv(data)

        print("豆瓣电影短评爬虫运行完成")

        return data