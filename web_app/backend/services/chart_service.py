from pathlib import Path
import sys
import re


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from config.config import DB_CONFIG
from src.utils.mysql_helper import MySqlHelper


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
        self.db = MySqlHelper(**self.db_config)

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

        rows = self.db.query(sql)

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

        rows = self.db.query(sql)

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

        rows = self.db.query(sql)

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

        rows = self.db.query(sql)

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

        rows = self.db.query(sql, (top_n,))

        data = []
        for row in rows:
            data.append({
                "movie_name": row["movie_name"],
                "rating_score": float(row["rating_score"]) if row["rating_score"] is not None else None,
                "rating_count": int(row["rating_count"])
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

        rows = self.db.query(sql)

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
            "keywords": self.get_keywords(top_n=keyword_top_n)
        }