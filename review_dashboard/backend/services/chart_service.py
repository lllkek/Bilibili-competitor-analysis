from pathlib import Path
import sys
import re
import csv
from collections import defaultdict


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

try:
    from config.config import DB_CONFIG
    from src.utils.mysql_helper import MySqlHelper
except Exception:
    DB_CONFIG = None
    MySqlHelper = None


class DoubanChartService:
    """
    豆瓣电影可视化数据服务类。

    这个类专门负责：
    1. 连接 MySQL 数据库
    2. 查询 douban_movie_top100 表
    3. 按不同图表需求整理数据
    4. 返回前端可以直接使用的图表数据结构
    """

    def __init__(self, db_config=None):
        """
        初始化数据库连接工具。

        db_config:
            可选数据库配置。如果不传，默认使用 config/config.py 中的 DB_CONFIG。
        """
        self.db_config = db_config or DB_CONFIG
        self.db = MySqlHelper(**self.db_config) if MySqlHelper and self.db_config else None
        self.project_root = PROJECT_ROOT
        self.dashboard_results_dir = self.project_root / "results" / "dashboard"
        self.movie_csv_path = self.project_root / "results" / "douban_movie_top100.csv"

    def _query(self, sql, params=None):
        if not self.db:
            return None

        try:
            return self.db.query(sql, params)
        except Exception:
            return None

    def _read_movie_csv(self):
        if not self.movie_csv_path.exists():
            return []

        with self.movie_csv_path.open("r", encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file))

    def _read_dashboard_csv(self, filename):
        path = self.dashboard_results_dir / filename

        if not path.exists():
            return []

        with path.open("r", encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file))

    def _to_float(self, value, default=0.0):
        try:
            if value in (None, ""):
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    def _to_int(self, value, default=0):
        try:
            if value in (None, ""):
                return default
            return int(float(value))
        except (TypeError, ValueError):
            return default

    def _split_text_items(self, text):
        """
        拆分数据库中的多值字段。

        例如：
        '剧情 / 犯罪' -> ['剧情', '犯罪']
        '美国 / 英国' -> ['美国', '英国']
        """
        if text is None:
            return []

        text = str(text).strip()

        if not text:
            return []

        items = re.split(r"[/,，、\s]+", text)

        return [item.strip() for item in items if item.strip()]

    def _count_items(self, rows, field_name, top_n=10):
        """
        通用字段统计方法。

        用于统计 genres、country 等多值字段的 TopN 分布。
        返回格式适合饼图或条形图使用：
        [
            {"name": "剧情", "value": 20},
            {"name": "犯罪", "value": 10}
        ]
        """
        item_count = {}

        for row in rows:
            items = self._split_text_items(row.get(field_name))

            for item in items:
                item_count[item] = item_count.get(item, 0) + 1

        sorted_items = sorted(
            item_count.items(),
            key=lambda x: x[1],
            reverse=True
        )

        data = []
        for name, value in sorted_items[:top_n]:
            data.append({
                "name": name,
                "value": value
            })

        return data

    def get_rating_distribution(self):
        """
        获取豆瓣电影评分分布数据。

        图表用途：
        评分分布条形图。
        """
        sql = """
            SELECT
                rating_score,
                COUNT(*) AS movie_count
            FROM douban_movie_top100
            WHERE rating_score IS NOT NULL
            GROUP BY rating_score
            ORDER BY rating_score;
        """

        rows = self._query(sql)

        if rows is None:
            rows = self._read_movie_csv()
            rating_count = {}

            for row in rows:
                score = row.get("rating_score")
                if score in (None, ""):
                    continue
                score = str(float(score))
                rating_count[score] = rating_count.get(score, 0) + 1

            return [
                {
                    "rating_score": float(score),
                    "movie_count": count
                }
                for score, count in sorted(rating_count.items(), key=lambda x: float(x[0]))
            ]

        data = []
        for row in rows:
            data.append({
                "rating_score": float(row["rating_score"]),
                "movie_count": int(row["movie_count"])
            })

        return data

    def get_genre_distribution(self, top_n=10):
        """
        获取电影类型 TopN 分布数据。

        参数：
        top_n: 返回出现次数最多的前 N 个类型。

        图表用途：
        类型占比饼图 / 类型分布条形图。
        """
        sql = """
            SELECT genres
            FROM douban_movie_top100
            WHERE genres IS NOT NULL AND genres != '';
        """

        rows = self._query(sql)

        if rows is None:
            rows = self._read_movie_csv()

        return self._count_items(
            rows=rows,
            field_name="genres",
            top_n=top_n
        )

    def get_country_distribution(self, top_n=10):
        """
        获取国家 / 地区 TopN 分布数据。

        参数：
        top_n: 返回出现次数最多的前 N 个国家或地区。

        图表用途：
        国家 / 地区占比饼图。
        """
        sql = """
            SELECT country
            FROM douban_movie_top100
            WHERE country IS NOT NULL AND country != '';
        """

        rows = self._query(sql)

        if rows is None:
            rows = self._read_movie_csv()

        return self._count_items(
            rows=rows,
            field_name="country",
            top_n=top_n
        )

    def get_year_trend(self):
        """
        获取上映年份趋势数据。

        图表用途：
        年份趋势折线图，展示每年电影数量和平均评分。
        """
        sql = """
            SELECT
                release_year,
                COUNT(*) AS movie_count,
                ROUND(AVG(rating_score), 2) AS avg_rating
            FROM douban_movie_top100
            WHERE release_year IS NOT NULL
              AND rating_score IS NOT NULL
            GROUP BY release_year
            ORDER BY release_year;
        """

        rows = self._query(sql)

        if rows is None:
            rows = self._read_movie_csv()
            grouped = {}

            for row in rows:
                year = self._to_int(row.get("release_year"))
                rating = self._to_float(row.get("rating_score"))
                rating_count = self._to_int(row.get("rating_count"))

                if year <= 0 or rating <= 0:
                    continue

                if year not in grouped:
                    grouped[year] = {
                        "movie_count": 0,
                        "rating_total": 0.0,
                        "total_rating_count": 0
                    }

                grouped[year]["movie_count"] += 1
                grouped[year]["rating_total"] += rating
                grouped[year]["total_rating_count"] += rating_count

            return [
                {
                    "release_year": year,
                    "movie_count": item["movie_count"],
                    "avg_rating": round(item["rating_total"] / item["movie_count"], 2)
                }
                for year, item in sorted(grouped.items())
            ]

        data = []
        for row in rows:
            data.append({
                "release_year": int(row["release_year"]),
                "movie_count": int(row["movie_count"]),
                "avg_rating": float(row["avg_rating"])
            })

        return data

    def get_rating_count_top(self, top_n=10):
        """
        获取评分人数 TopN 电影数据。

        参数：
        top_n: 返回评分人数最高的前 N 部电影。

        图表用途：
        电影热度排行横向条形图。
        """
        sql = """
            SELECT
                movie_name,
                rating_score,
                rating_count
            FROM douban_movie_top100
            WHERE rating_count IS NOT NULL
            ORDER BY rating_count DESC
            LIMIT %s;
        """

        rows = self._query(sql, (top_n,))

        if rows is None:
            rows = sorted(
                self._read_movie_csv(),
                key=lambda row: self._to_int(row.get("rating_count")),
                reverse=True
            )[:top_n]

        data = []
        for row in rows:
            data.append({
                "movie_name": row["movie_name"],
                "rating_score": self._to_float(row.get("rating_score")) if row.get("rating_score") is not None else None,
                "rating_count": self._to_int(row.get("rating_count"))
            })

        return data

    def get_keywords(self, top_n=30):
        """
        获取豆瓣电影高频关键词。

        当前版本基于 genres、director、actors 三类字段统计关键词。
        后续如果加入评论数据，可以扩展为评论关键词分析。

        参数：
        top_n: 返回出现次数最多的前 N 个关键词。
        """
        sql = """
            SELECT
                genres,
                director,
                actors
            FROM douban_movie_top100;
        """

        rows = self._query(sql)

        if rows is None:
            rows = self._read_movie_csv()

        keyword_count = {}

        for row in rows:
            fields = [
                row.get("genres"),
                row.get("director"),
                row.get("actors")
            ]

            for field in fields:
                items = self._split_text_items(field)

                for item in items:
                    if len(item) >= 2:
                        keyword_count[item] = keyword_count.get(item, 0) + 1

        sorted_keywords = sorted(
            keyword_count.items(),
            key=lambda x: x[1],
            reverse=True
        )

        data = []
        for name, value in sorted_keywords[:top_n]:
            data.append({
                "name": name,
                "value": value
            })

        return data

    def get_review_keywords(self, top_n=30, sentiment_type=None):
        """
        获取评论关键词热度。

        数据来自 results/dashboard/summary_keyword.csv：
        - keyword_count 表示出现次数
        - weighted_score 表示结合点赞后的热度
        - avg_like_count 表示平均点赞
        """
        rows = self._read_dashboard_csv("summary_keyword.csv")
        grouped = {}

        for row in rows:
            if sentiment_type and row.get("comment_sentiment_type") != sentiment_type:
                continue

            keyword = (row.get("keyword") or "").strip()

            if not keyword:
                continue

            if keyword not in grouped:
                grouped[keyword] = {
                    "name": keyword,
                    "value": 0,
                    "keyword_count": 0,
                    "weighted_score": 0.0,
                    "avg_like_total": 0.0,
                    "row_count": 0
                }

            item = grouped[keyword]
            item["keyword_count"] += self._to_int(row.get("keyword_count"))
            item["weighted_score"] += self._to_float(row.get("weighted_score"))
            item["avg_like_total"] += self._to_float(row.get("avg_like_count"))
            item["row_count"] += 1

        data = []

        for item in grouped.values():
            row_count = max(item.pop("row_count"), 1)
            item["avg_like_count"] = round(item.pop("avg_like_total") / row_count, 2)
            item["weighted_score"] = round(item["weighted_score"], 4)
            item["value"] = item["keyword_count"]
            data.append(item)

        data.sort(key=lambda x: x["weighted_score"], reverse=True)

        return data[:top_n]

    def get_review_wordcloud(self, top_n=80, sentiment_type=None):
        """
        获取评论关键词云数据。

        前端使用 name/value 渲染标签云，value 使用加权热度，
        可以按好评 / 中评 / 差评筛选。
        """
        keywords = self.get_review_keywords(
            top_n=top_n,
            sentiment_type=sentiment_type
        )

        return [
            {
                "name": item["name"],
                "value": round(item["weighted_score"], 2),
                "keyword_count": item["keyword_count"],
                "avg_like_count": item["avg_like_count"]
            }
            for item in keywords
        ]

    def get_year_genre_share(self, top_n=6):
        """
        获取不同上映年份中各类型电影占比。

        使用去重后的 movie_name + release_year + primary_genre，
        避免评论数较多的电影重复放大类型占比。
        """
        rows = self._read_dashboard_csv("douban_review_analysis_enriched.csv")
        movie_seen = set()
        genre_total = defaultdict(int)
        year_genre_count = defaultdict(int)
        year_total = defaultdict(int)

        for row in rows:
            movie_name = row.get("movie_name")
            release_year = row.get("release_year")
            genre = row.get("primary_genre") or "未知类型"

            if not movie_name or not release_year or genre == "未知类型":
                continue

            year = self._to_int(release_year)

            if year <= 0:
                continue

            key = (movie_name, year, genre)

            if key in movie_seen:
                continue

            movie_seen.add(key)
            genre_total[genre] += 1
            year_genre_count[(year, genre)] += 1
            year_total[year] += 1

        top_genres = [
            genre
            for genre, _ in sorted(genre_total.items(), key=lambda x: x[1], reverse=True)[:top_n]
        ]

        data = []

        for year in sorted(year_total.keys()):
            total = year_total[year]

            for genre in top_genres:
                count = year_genre_count.get((year, genre), 0)

                data.append({
                    "release_year": year,
                    "genre": genre,
                    "movie_count": count,
                    "year_total": total,
                    "share": round(count / total, 4) if total else 0
                })

        return data

    def get_dashboard_data(self, top_n=10, keyword_top_n=30):
        """
        一次性获取 Dashboard 所需的全部图表数据。

        参数：
        top_n:
            控制类型分布、国家 / 地区分布、评分人数排行的数量。
        keyword_top_n:
            控制关键词图展示的关键词数量。

        这个方法适合 example 或外部系统一次性调用。
        """
        return {
            "rating_distribution": self.get_rating_distribution(),
            "genre_distribution": self.get_genre_distribution(top_n=top_n),
            "country_distribution": self.get_country_distribution(top_n=top_n),
            "year_trend": self.get_year_trend(),
            "rating_count_top": self.get_rating_count_top(top_n=top_n),
            "keywords": self.get_keywords(top_n=keyword_top_n),
            "review_keywords": self.get_review_keywords(top_n=keyword_top_n),
            "review_wordcloud": self.get_review_wordcloud(top_n=80),
            "year_genre_share": self.get_year_genre_share(top_n=6)
        }
