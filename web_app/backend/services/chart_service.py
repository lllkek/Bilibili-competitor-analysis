from pathlib import Path
import sys
import re


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from config.config import DB_CONFIG
from src.utils.mysql_helper import MySqlHelper


def get_db():
    """
    创建数据库连接工具。
    这里复用项目已有的 MySqlHelper，不在 web_app 里重复写数据库连接代码。
    """
    return MySqlHelper(**DB_CONFIG)


def split_text_items(text):
    """
    把数据库里保存的多个值拆开。
    兼容这些格式：
    剧情 / 犯罪
    剧情,犯罪
    剧情 犯罪
    美国 / 英国
    """
    if text is None:
        return []

    text = str(text).strip()

    if not text:
        return []

    items = re.split(r"[/,，、\s]+", text)

    return [item.strip() for item in items if item.strip()]


def get_douban_rating_distribution():
    """
    豆瓣电影评分分布：条形图。
    例如：8.5 分有多少部电影，9.0 分有多少部电影。
    """
    db = get_db()

    sql = """
        SELECT 
            rating_score,
            COUNT(*) AS movie_count
        FROM douban_movie_top100
        WHERE rating_score IS NOT NULL
        GROUP BY rating_score
        ORDER BY rating_score;
    """

    rows = db.query(sql)

    data = []
    for row in rows:
        data.append({
            "rating_score": float(row["rating_score"]),
            "movie_count": int(row["movie_count"])
        })

    return data


def get_douban_genre_distribution(top_n=10):
    """
    豆瓣电影类型分布：饼图 / 条形图。
    一部电影可能有多个类型，所以先取出 genres 字段，再用 Python 拆分统计。
    """
    db = get_db()

    sql = """
        SELECT genres
        FROM douban_movie_top100
        WHERE genres IS NOT NULL AND genres != '';
    """

    rows = db.query(sql)

    genre_count = {}

    for row in rows:
        genres = split_text_items(row["genres"])

        for genre in genres:
            genre_count[genre] = genre_count.get(genre, 0) + 1

    sorted_genres = sorted(
        genre_count.items(),
        key=lambda x: x[1],
        reverse=True
    )

    data = []
    for genre, count in sorted_genres[:top_n]:
        data.append({
            "name": genre,
            "value": count
        })

    return data


def get_douban_country_distribution(top_n=10):
    """
    豆瓣电影国家/地区分布：饼图。
    country 字段可能包含多个地区，所以也需要拆分统计。
    """
    db = get_db()

    sql = """
        SELECT country
        FROM douban_movie_top100
        WHERE country IS NOT NULL AND country != '';
    """

    rows = db.query(sql)

    country_count = {}

    for row in rows:
        countries = split_text_items(row["country"])

        for country in countries:
            country_count[country] = country_count.get(country, 0) + 1

    sorted_countries = sorted(
        country_count.items(),
        key=lambda x: x[1],
        reverse=True
    )

    data = []
    for country, count in sorted_countries[:top_n]:
        data.append({
            "name": country,
            "value": count
        })

    return data


def get_douban_year_trend():
    """
    豆瓣电影年份趋势：折线图。
    展示不同上映年份的电影数量和平均评分。
    """
    db = get_db()

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

    rows = db.query(sql)

    data = []
    for row in rows:
        data.append({
            "release_year": int(row["release_year"]),
            "movie_count": int(row["movie_count"]),
            "avg_rating": float(row["avg_rating"])
        })

    return data


def get_douban_rating_count_top(top_n=10):
    """
    豆瓣电影评分人数 TopN：横向条形图。
    评分人数越高，说明电影关注度越高。
    """
    db = get_db()

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

    rows = db.query(sql, (top_n,))

    data = []
    for row in rows:
        data.append({
            "movie_name": row["movie_name"],
            "rating_score": float(row["rating_score"]) if row["rating_score"] is not None else None,
            "rating_count": int(row["rating_count"])
        })

    return data


def get_douban_keywords(top_n=30):
    """
    豆瓣电影关键词统计。
    当前没有评论文本，所以先基于 genres、director、actors 三类字段生成高频关键词。
    后续如果爬取评论，可以升级为评论关键词分析。
    """
    db = get_db()

    sql = """
        SELECT
            genres,
            director,
            actors
        FROM douban_movie_top100;
    """

    rows = db.query(sql)

    keyword_count = {}

    for row in rows:
        fields = [
            row.get("genres"),
            row.get("director"),
            row.get("actors")
        ]

        for field in fields:
            items = split_text_items(field)

            for item in items:
                if len(item) >= 2:
                    keyword_count[item] = keyword_count.get(item, 0) + 1

    sorted_keywords = sorted(
        keyword_count.items(),
        key=lambda x: x[1],
        reverse=True
    )

    data = []
    for keyword, count in sorted_keywords[:top_n]:
        data.append({
            "name": keyword,
            "value": count
        })

    return data


def get_baidu_hot_top10():
    """
    百度热搜 Top10。
    这个作为补充功能保留，不作为主线。
    """
    db = get_db()

    sql = """
        SELECT 
            rank_no,
            keyword,
            hot_score,
            url,
            crawl_time
        FROM baidu_hot_search
        ORDER BY rank_no
        LIMIT 10;
    """

    rows = db.query(sql)

    data = []

    for row in rows:
        raw_hot_score = row["hot_score"]

        if raw_hot_score is None:
            hot_score_num = 0
        else:
            score_text = str(raw_hot_score)
            score_text = re.sub(r"[^\d]", "", score_text)
            hot_score_num = int(score_text) if score_text else 0

        data.append({
            "rank_no": int(row["rank_no"]),
            "keyword": row["keyword"],
            "hot_score": hot_score_num,
            "url": row["url"],
            "crawl_time": str(row["crawl_time"]) if row["crawl_time"] else None
        })

    return data