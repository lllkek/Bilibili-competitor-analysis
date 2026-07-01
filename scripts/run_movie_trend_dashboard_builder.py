from pathlib import Path
import ast
import re

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"
OUTPUT_DIR = RESULTS_DIR / "dashboard"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DETAIL_PATH = RESULTS_DIR / "douban_rule_reason_analysis.csv"

MOVIE_CANDIDATES = [
    RESULTS_DIR / "douban_movie_top100.csv",
    RESULTS_DIR / "douban_movies_top100.csv",
    RESULTS_DIR / "douban_top100_movies.csv",
    RESULTS_DIR / "douban_movies.csv",
]

GENRE_PRIORITY = [
    "剧情", "爱情", "战争", "动画", "犯罪", "科幻", "喜剧", "悬疑",
    "动作", "纪录片", "奇幻", "冒险", "家庭", "历史", "传记", "音乐"
]


def read_csv_safely(path):
    if path is None or not path.exists():
        print(f"文件不存在：{path}")
        return pd.DataFrame()
    return pd.read_csv(path)


def save_csv(df, filename):
    path = OUTPUT_DIR / filename
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"已生成：{path}，shape={df.shape}")


def find_movie_file():
    for path in MOVIE_CANDIDATES:
        if path.exists():
            return path
    return None


def normalize_movie_columns(movie_df):
    if movie_df.empty:
        return movie_df

    rename_map = {}

    for col in movie_df.columns:
        low = col.lower()

        if col in ["电影名称", "title", "name", "movie_title"]:
            rename_map[col] = "movie_name"
        elif col in ["豆瓣评分", "score", "rating", "rating_num"]:
            rename_map[col] = "rating_score"
        elif col in ["评分人数", "评价人数", "votes", "rating_people", "rating_count"]:
            rename_map[col] = "rating_count"
        elif col in ["年份", "上映年份", "year"]:
            rename_map[col] = "release_year"
        elif col in ["类型", "电影类型", "genre", "genres"]:
            rename_map[col] = "genres"
        elif col in ["国家", "地区", "country", "countries"]:
            rename_map[col] = "country"
        elif col in ["导演", "director"]:
            rename_map[col] = "director"
        elif col in ["演员", "actors", "cast"]:
            rename_map[col] = "actors"
        elif "rating" in low and "count" not in low:
            rename_map[col] = "rating_score"
        elif "vote" in low:
            rename_map[col] = "rating_count"
        elif "genre" in low:
            rename_map[col] = "genres"
        elif "year" in low:
            rename_map[col] = "release_year"

    return movie_df.rename(columns=rename_map)


def parse_number(value):
    if pd.isna(value):
        return np.nan

    text = str(value)
    text = text.replace(",", "").replace("人评价", "").replace("人看过", "")
    match = re.search(r"\d+(\.\d+)?", text)

    if match:
        return float(match.group())

    return np.nan


def parse_year(value):
    if pd.isna(value):
        return np.nan

    match = re.search(r"(19|20)\d{2}", str(value))

    if match:
        return int(match.group())

    return np.nan


def make_decade(year):
    if pd.isna(year):
        return np.nan

    year = int(year)

    if year < 1980:
        return "1980年前"
    if year < 1990:
        return "1980s"
    if year < 2000:
        return "1990s"
    if year < 2010:
        return "2000s"
    if year < 2020:
        return "2010s"

    return "2020s"


def split_genres(value):
    if pd.isna(value):
        return []

    text = str(value)
    parts = re.split(r"[/,，、\s]+", text)
    return [p.strip() for p in parts if p.strip()]


def get_primary_genre(value):
    genres = split_genres(value)

    if not genres:
        return "未知类型"

    for genre in GENRE_PRIORITY:
        if genre in genres:
            return genre

    return genres[0]


def parse_keywords(value):
    if pd.isna(value):
        return []

    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]

    text = str(value).strip()

    if not text:
        return []

    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if str(x).strip()]
    except Exception:
        pass

    parts = re.split(r"[,，、\s|/]+", text)
    return [p.strip() for p in parts if p.strip()]


def prepare_detail(detail_df):
    df = detail_df.copy()

    if "main_aspect" in df.columns:
        df = df[df["main_aspect"].notna()]
        df = df[df["main_aspect"] != "未识别"]

    if "clean_review_text" not in df.columns and "review_text" in df.columns:
        df["clean_review_text"] = df["review_text"]

    if "clean_review_text" not in df.columns:
        df["clean_review_text"] = ""

    if "clean_text_length" not in df.columns:
        df["clean_text_length"] = df["clean_review_text"].fillna("").astype(str).str.len()

    if "review_like_count" in df.columns:
        df["review_like_count"] = pd.to_numeric(df["review_like_count"], errors="coerce").fillna(0)
    else:
        df["review_like_count"] = 0

    if "like_weight" not in df.columns:
        df["like_weight"] = np.log1p(df["review_like_count"]) + 1
    else:
        df["like_weight"] = pd.to_numeric(df["like_weight"], errors="coerce").fillna(1)

    if "review_star" in df.columns:
        df["review_star"] = pd.to_numeric(df["review_star"], errors="coerce")

    if "review_time" in df.columns:
        df["review_time"] = pd.to_datetime(df["review_time"], errors="coerce")
        df["review_year"] = df["review_time"].dt.year
    elif "review_year" in df.columns:
        df["review_year"] = pd.to_numeric(df["review_year"], errors="coerce")
    else:
        df["review_year"] = np.nan

    if "comment_sentiment_type" not in df.columns:
        df["comment_sentiment_type"] = None

    if "comment_sentiment_name" not in df.columns:
        sentiment_map = {
            "positive": "好评",
            "neutral": "中评",
            "negative": "差评"
        }
        df["comment_sentiment_name"] = df["comment_sentiment_type"].map(sentiment_map)

    if "main_reason" not in df.columns:
        df["main_reason"] = df["main_aspect"]

    return df


def prepare_movie_base(movie_df, detail_df):
    if movie_df.empty:
        base = detail_df[["movie_name"]].drop_duplicates().copy()
        base["rating_score"] = np.nan
        base["rating_count"] = np.nan
        base["release_year"] = np.nan
        base["genres"] = "未知类型"
    else:
        base = normalize_movie_columns(movie_df).copy()

    if "movie_name" not in base.columns:
        raise ValueError("电影基础表里没有 movie_name 或可识别的电影名称列。")

    keep_cols = [
        "movie_name", "rating_score", "rating_count", "release_year",
        "genres", "country", "director", "actors", "duration_minutes"
    ]

    for col in keep_cols:
        if col not in base.columns:
            base[col] = np.nan

    base = base[keep_cols].drop_duplicates(subset=["movie_name"])

    base["rating_score"] = base["rating_score"].apply(parse_number)
    base["rating_count"] = base["rating_count"].apply(parse_number)
    base["release_year"] = base["release_year"].apply(parse_year)
    base["release_decade"] = base["release_year"].apply(make_decade)
    base["genres"] = base["genres"].fillna("未知类型")
    base["primary_genre"] = base["genres"].apply(get_primary_genre)

    return base


def build_rating_distribution(movie_base):
    df = movie_base.dropna(subset=["rating_score"]).copy()

    bins = [0, 8.0, 8.5, 9.0, 9.5, 10.1]
    labels = ["8.0以下", "8.0-8.4", "8.5-8.9", "9.0-9.4", "9.5+"]

    df["rating_bin"] = pd.cut(df["rating_score"], bins=bins, labels=labels, right=False)

    result = (
        df.groupby("rating_bin", observed=False)
        .agg(movie_count=("movie_name", "nunique"))
        .reset_index()
    )

    return result


def build_genre_distribution(movie_base):
    df = movie_base[movie_base["primary_genre"] != "未知类型"].copy()

    result = (
        df.groupby("primary_genre")
        .agg(
            movie_count=("movie_name", "nunique"),
            avg_rating=("rating_score", "mean"),
            total_rating_count=("rating_count", "sum")
        )
        .reset_index()
        .sort_values("movie_count", ascending=False)
    )

    total = result["movie_count"].sum()
    result["movie_ratio"] = result["movie_count"] / total if total else 0
    result["avg_rating"] = result["avg_rating"].round(2)
    result["movie_ratio"] = result["movie_ratio"].round(4)

    return result


def build_year_trend(movie_base):
    df = movie_base.dropna(subset=["release_year"]).copy()
    df["release_year"] = df["release_year"].astype(int)

    result = (
        df.groupby("release_year")
        .agg(
            movie_count=("movie_name", "nunique"),
            avg_rating=("rating_score", "mean"),
            total_rating_count=("rating_count", "sum")
        )
        .reset_index()
        .sort_values("release_year")
    )

    result["avg_rating"] = result["avg_rating"].round(2)

    return result


def build_movie_overview(enriched):
    df = enriched.copy()

    base_cols = [
        "movie_name", "rating_score", "rating_count", "release_year",
        "release_decade", "genres", "primary_genre"
    ]

    profile = (
        df.groupby(base_cols, dropna=False)
        .agg(
            review_count=("clean_review_text", "count"),
            avg_like_count=("review_like_count", "mean"),
            total_like_count=("review_like_count", "sum")
        )
        .reset_index()
    )

    aspect_top = (
        df.groupby(["movie_name", "main_aspect"])
        .size()
        .reset_index(name="count")
        .sort_values(["movie_name", "count"], ascending=[True, False])
    )

    aspect_map = (
        aspect_top.groupby("movie_name")["main_aspect"]
        .apply(lambda x: " / ".join(x.head(3)))
        .reset_index(name="top_aspects")
    )

    reason_top = (
        df.groupby(["movie_name", "main_reason"])
        .size()
        .reset_index(name="count")
        .sort_values(["movie_name", "count"], ascending=[True, False])
    )

    reason_map = (
        reason_top.groupby("movie_name")["main_reason"]
        .apply(lambda x: " / ".join(x.head(3)))
        .reset_index(name="top_reasons")
    )

    profile = profile.merge(aspect_map, on="movie_name", how="left")
    profile = profile.merge(reason_map, on="movie_name", how="left")
    profile["avg_like_count"] = profile["avg_like_count"].round(2)

    return profile.sort_values(["rating_score", "rating_count"], ascending=[False, False])


def build_aspect_reason(enriched):
    df = enriched.copy()

    result = (
        df.groupby(
            ["comment_sentiment_type", "comment_sentiment_name", "main_aspect", "main_reason"],
            dropna=False
        )
        .agg(
            review_count=("clean_review_text", "count"),
            weighted_score=("like_weight", "sum"),
            avg_like_count=("review_like_count", "mean")
        )
        .reset_index()
    )

    sentiment_total = result.groupby("comment_sentiment_type")["review_count"].transform("sum")
    overall_total = result["review_count"].sum()

    result["within_sentiment_ratio"] = result["review_count"] / sentiment_total
    result["overall_ratio"] = result["review_count"] / overall_total if overall_total else 0

    result["weighted_score"] = result["weighted_score"].round(4)
    result["avg_like_count"] = result["avg_like_count"].round(2)
    result["within_sentiment_ratio"] = result["within_sentiment_ratio"].round(4)
    result["overall_ratio"] = result["overall_ratio"].round(4)

    return result.sort_values("weighted_score", ascending=False)


def build_genre_preference(enriched):
    df = enriched[enriched["primary_genre"] != "未知类型"].copy()

    result = (
        df.groupby(["primary_genre", "main_aspect", "main_reason"], dropna=False)
        .agg(
            review_count=("clean_review_text", "count"),
            weighted_score=("like_weight", "sum"),
            avg_like_count=("review_like_count", "mean")
        )
        .reset_index()
    )

    genre_total = result.groupby("primary_genre")["review_count"].transform("sum")
    result["within_genre_ratio"] = result["review_count"] / genre_total

    result["weighted_score"] = result["weighted_score"].round(4)
    result["avg_like_count"] = result["avg_like_count"].round(2)
    result["within_genre_ratio"] = result["within_genre_ratio"].round(4)

    return result.sort_values(["primary_genre", "weighted_score"], ascending=[True, False])


def build_year_preference_trend(enriched):
    df = enriched.dropna(subset=["review_year"]).copy()
    df["review_year"] = df["review_year"].astype(int)

    result = (
        df.groupby(["review_year", "main_aspect"])
        .agg(
            review_count=("clean_review_text", "count"),
            weighted_score=("like_weight", "sum"),
            avg_like_count=("review_like_count", "mean")
        )
        .reset_index()
        .sort_values("review_year")
    )

    year_total = result.groupby("review_year")["review_count"].transform("sum")
    result["year_ratio"] = result["review_count"] / year_total

    result["weighted_score"] = result["weighted_score"].round(4)
    result["avg_like_count"] = result["avg_like_count"].round(2)
    result["year_ratio"] = result["year_ratio"].round(4)

    return result


def build_keyword_summary(enriched):
    keyword_col = None

    for col in ["top_keywords", "matched_keywords"]:
        if col in enriched.columns:
            keyword_col = col
            break

    columns = [
        "movie_name", "primary_genre", "comment_sentiment_type",
        "comment_sentiment_name", "keyword", "keyword_count",
        "weighted_score", "avg_like_count"
    ]

    if keyword_col is None:
        return pd.DataFrame(columns=columns)

    rows = []

    for _, row in enriched.iterrows():
        keywords = parse_keywords(row.get(keyword_col))

        for keyword in keywords:
            rows.append({
                "movie_name": row.get("movie_name"),
                "primary_genre": row.get("primary_genre"),
                "comment_sentiment_type": row.get("comment_sentiment_type"),
                "comment_sentiment_name": row.get("comment_sentiment_name"),
                "keyword": keyword,
                "review_like_count": row.get("review_like_count", 0),
                "like_weight": row.get("like_weight", 1)
            })

    kw = pd.DataFrame(rows)

    if kw.empty:
        return pd.DataFrame(columns=columns)

    result = (
        kw.groupby(
            ["movie_name", "primary_genre", "comment_sentiment_type", "comment_sentiment_name", "keyword"],
            dropna=False
        )
        .agg(
            keyword_count=("keyword", "count"),
            weighted_score=("like_weight", "sum"),
            avg_like_count=("review_like_count", "mean")
        )
        .reset_index()
    )

    result["weighted_score"] = result["weighted_score"].round(4)
    result["avg_like_count"] = result["avg_like_count"].round(2)

    return result.sort_values("weighted_score", ascending=False)


def main():
    detail_df = read_csv_safely(DETAIL_PATH)

    if detail_df.empty:
        raise FileNotFoundError(f"没有找到评论原因分析文件：{DETAIL_PATH}")

    detail_df = prepare_detail(detail_df)

    movie_path = find_movie_file()
    movie_df = read_csv_safely(movie_path) if movie_path else pd.DataFrame()

    if movie_path:
        print(f"已识别电影基础信息文件：{movie_path}")
    else:
        print("没有找到电影基础信息表，将只使用评论表中的 movie_name。")

    movie_base = prepare_movie_base(movie_df, detail_df)

    enriched = detail_df.merge(movie_base, on="movie_name", how="left")
    enriched["primary_genre"] = enriched["primary_genre"].fillna("未知类型")
    enriched["genres"] = enriched["genres"].fillna("未知类型")
    enriched["release_decade"] = enriched["release_year"].apply(make_decade)

    save_csv(enriched, "douban_review_analysis_enriched.csv")
    save_csv(build_movie_overview(enriched), "summary_movie_overview.csv")
    save_csv(build_rating_distribution(movie_base), "summary_rating_distribution.csv")
    save_csv(build_genre_distribution(movie_base), "summary_genre_distribution.csv")
    save_csv(build_year_trend(movie_base), "summary_year_trend.csv")
    save_csv(build_aspect_reason(enriched), "summary_aspect_reason.csv")
    save_csv(build_genre_preference(enriched), "summary_genre_preference.csv")
    save_csv(build_year_preference_trend(enriched), "summary_year_preference_trend.csv")
    save_csv(build_keyword_summary(enriched), "summary_keyword.csv")

    print("\nDashboard 汇总数据生成完成。")


if __name__ == "__main__":
    main()