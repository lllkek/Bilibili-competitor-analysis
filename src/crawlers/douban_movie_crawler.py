import csv
import math
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


class DoubanMovieCrawler:
    """
    豆瓣电影 Top250 爬虫类。

    支持功能：
    1. 通过 top_n 控制爬取电影数量
    2. 支持保存到 MySQL
    3. 支持保存到 CSV
    4. 支持通过 fields 参数选择保存哪些字段
    5. 保存电影详情页链接 movie_url，方便后续爬取电影评论
    """

    DEFAULT_FIELDS = [
        "rank_no",
        "movie_name",
        "movie_url",
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

    def __init__(self, top_n=100, save_mysql=True, save_csv=True, fields=None):
        self.top_n = top_n
        self.save_mysql = save_mysql
        self.save_csv = save_csv

        if fields is None:
            self.fields = self.DEFAULT_FIELDS
        else:
            self.fields = fields
            self._validate_fields()

        self.base_url = "https://movie.douban.com/top250"
        self.headers = DOUBAN_HEADERS

        self.min_sleep = CRAWLER_CONFIG.get("min_sleep", 1)
        self.max_sleep = CRAWLER_CONFIG.get("max_sleep", 2)
        self.timeout = CRAWLER_CONFIG.get("timeout", 10)

        self.project_root = Path(__file__).resolve().parents[2]
        self.result_path = self.project_root / "results" / "douban_movie_top100.csv"
        self.debug_path = self.project_root / "results" / "douban_debug.html"

    def _validate_fields(self):
        """
        检查用户传入的 fields 是否都属于允许字段。
        """

        invalid_fields = []

        for field in self.fields:
            if field not in self.DEFAULT_FIELDS:
                invalid_fields.append(field)

        if invalid_fields:
            raise ValueError(f"存在不支持的字段：{invalid_fields}")

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

    def parse_list_page(self, html):
        """
        解析豆瓣 Top250 列表页，提取排名和电影详情页链接。
        """

        soup = BeautifulSoup(html, "lxml")
        items = soup.select("div.item")

        movie_url_list = []

        for item in items:
            rank_tag = item.select_one("em")
            link_tag = item.select_one("div.hd a[href]")

            if not rank_tag or not link_tag:
                continue

            rank_no = int(rank_tag.get_text(strip=True))

            movie_url = link_tag.get("href")
            movie_url = urljoin(self.base_url, movie_url)

            movie_url_list.append(
                {
                    "rank_no": rank_no,
                    "movie_url": movie_url
                }
            )

        return movie_url_list

    def crawl_movie_urls(self):
        """
        根据 top_n 获取需要爬取的电影详情页链接。
        豆瓣 Top250 每页 25 条，所以根据 top_n 自动计算需要翻几页。
        """

        movie_url_list = []
        page_count = math.ceil(self.top_n / 25)

        for page_index in range(page_count):
            start = page_index * 25
            url = f"{self.base_url}?start={start}&filter="

            html = self.get_html(url)
            page_movie_urls = self.parse_list_page(html)

            movie_url_list.extend(page_movie_urls)

            print(f"已获取电影链接数量：{len(movie_url_list)}")

        movie_url_list = movie_url_list[:self.top_n]

        print(f"最终需要爬取的电影详情页数量：{len(movie_url_list)}")

        return movie_url_list

    def _extract_info_field(self, info_text, field_name):
        """
        从豆瓣详情页 info 文本中提取指定字段。

        兼容两种情况：
        1. 制片国家/地区: 美国
        2. 制片国家/地区:
           美国
        """

        lines = []

        for line in info_text.split("\n"):
            line = line.strip()
            if line:
                lines.append(line)

        stop_fields = [
            "导演",
            "编剧",
            "主演",
            "类型",
            "制片国家/地区",
            "语言",
            "上映日期",
            "片长",
            "又名",
            "IMDb"
        ]

        for index, line in enumerate(lines):
            if line.startswith(field_name):
                value = (
                    line
                    .replace(field_name, "", 1)
                    .replace(":", "", 1)
                    .replace("：", "", 1)
                    .strip()
                )

                if value:
                    return value

                next_values = []

                for next_line in lines[index + 1:]:
                    is_next_field = False

                    for stop_field in stop_fields:
                        if next_line.startswith(stop_field):
                            is_next_field = True
                            break

                    if is_next_field:
                        break

                    next_values.append(next_line)

                return " / ".join(next_values).strip()

        return ""

    def parse_detail_page(self, html, rank_no, movie_url):
        """
        解析电影详情页，提取电影字段。
        """

        soup = BeautifulSoup(html, "lxml")
        crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        movie_name_tag = soup.select_one("h1 span[property='v:itemreviewed']")
        movie_name = movie_name_tag.get_text(strip=True) if movie_name_tag else ""

        director_tags = soup.select("a[rel='v:directedBy']")
        director = ",".join([tag.get_text(strip=True) for tag in director_tags])

        actor_tags = soup.select("a[rel='v:starring']")
        actors = ",".join([tag.get_text(strip=True) for tag in actor_tags])

        rating_tag = soup.select_one("strong.rating_num")
        rating_score = rating_tag.get_text(strip=True) if rating_tag else ""

        rating_count_tag = soup.select_one("span[property='v:votes']")
        rating_count = rating_count_tag.get_text(strip=True) if rating_count_tag else ""

        year_tag = soup.select_one("span.year")
        release_year = ""

        if year_tag:
            year_text = year_tag.get_text(strip=True)
            year_match = re.search(r"\d{4}", year_text)

            if year_match:
                release_year = year_match.group()

        genre_tags = soup.select("span[property='v:genre']")
        genres = ",".join([tag.get_text(strip=True) for tag in genre_tags])

        runtime_tag = soup.select_one("span[property='v:runtime']")
        duration_minutes = ""

        if runtime_tag:
            runtime_text = runtime_tag.get("content") or runtime_tag.get_text(strip=True)
            duration_match = re.search(r"\d+", runtime_text)

            if duration_match:
                duration_minutes = duration_match.group()

        info_tag = soup.select_one("#info")
        country = ""

        if info_tag:
            info_text = info_tag.get_text("\n", strip=True)
            country = self._extract_info_field(info_text, "制片国家/地区")

        movie_data = {
            "rank_no": rank_no,
            "movie_name": movie_name,
            "movie_url": movie_url,
            "director": director,
            "actors": actors,
            "rating_score": rating_score,
            "rating_count": rating_count,
            "release_year": release_year,
            "genres": genres,
            "duration_minutes": duration_minutes,
            "country": country,
            "crawl_time": crawl_time
        }

        return movie_data

    def crawl(self):
        """
        执行豆瓣电影完整爬取流程，返回电影数据列表。
        """

        movie_url_list = self.crawl_movie_urls()
        movie_detail_list = []

        for index, movie_item in enumerate(movie_url_list, start=1):
            rank_no = movie_item["rank_no"]
            movie_url = movie_item["movie_url"]

            print(f"正在爬取第 {index}/{len(movie_url_list)} 部电影：{movie_url}")

            html = self.get_html(movie_url)

            movie_data = self.parse_detail_page(
                html=html,
                rank_no=rank_no,
                movie_url=movie_url
            )

            movie_detail_list.append(movie_data)

        print(f"成功解析豆瓣电影数据：{len(movie_detail_list)} 条")

        return movie_detail_list

    def filter_fields(self, data):
        """
        根据 fields 参数筛选需要保存的字段。
        """

        filtered_data = []

        for item in data:
            filtered_item = {}

            for field in self.fields:
                filtered_item[field] = item.get(field, "")

            filtered_data.append(filtered_item)

        return filtered_data

    def save_to_mysql(self, data):
        """
        将豆瓣电影数据保存到 MySQL。
        支持根据 fields 动态保存部分字段。
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

        columns = self.fields
        column_names = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))

        sql = f"""
        INSERT INTO douban_movie_top100
        ({column_names})
        VALUES ({placeholders})
        """

        data_list = []

        for item in data:
            row = []

            for field in columns:
                value = item.get(field, "")

                if field in ["rank_no", "rating_count", "release_year", "duration_minutes"]:
                    value = int(value) if value not in ["", None] else None

                elif field == "rating_score":
                    value = float(value) if value not in ["", None] else None

                row.append(value)

            data_list.append(tuple(row))

        db.executemany(sql, data_list)

        print("豆瓣电影数据已写入 MySQL")

    def save_to_csv(self, data):
        """
        将豆瓣电影数据保存到 CSV。
        支持根据 fields 参数动态保存部分字段。
        """

        if not data:
            print("没有数据需要保存为 CSV")
            return

        self.result_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.result_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fields)
            writer.writeheader()
            writer.writerows(data)

        print(f"豆瓣电影数据已保存为 CSV：{self.result_path}")

    def run(self):
        """
        豆瓣电影爬虫总入口。

        运行顺序：
        1. 获取电影详情页链接
        2. 进入详情页解析电影字段
        3. 根据 fields 参数筛选字段
        4. 写入 MySQL
        5. 保存 CSV
        6. 返回数据
        """

        data = self.crawl()
        filtered_data = self.filter_fields(data)

        if self.save_mysql:
            self.save_to_mysql(filtered_data)

        if self.save_csv:
            self.save_to_csv(filtered_data)

        print("豆瓣电影爬虫运行完成")

        return filtered_data