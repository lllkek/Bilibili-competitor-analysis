import pandas as pd
import streamlit as st
import plotly.express as px


# =========================
# 1. 页面基础设置
# =========================

st.set_page_config(
    page_title="豆瓣电影 Top100 可视化分析",
    page_icon="🎬",
    layout="wide"
)


# =========================
# 2. 读取 GitHub CSV
# =========================

CSV_URL = "https://raw.githubusercontent.com/lllkek/Bilibili-competitor-analysis/refs/heads/main/week3_douban_movie/douban_movie_top100.csv"


@st.cache_data
def load_data():
    """
    从 GitHub Raw CSV 链接读取豆瓣电影 Top100 数据。
    @st.cache_data 的作用是缓存数据，避免每次刷新页面都重新读取 CSV。
    """

    df = pd.read_csv(CSV_URL)

    return df


df = load_data()


# =========================
# 3. 数据类型处理
# =========================

df["rank_no"] = pd.to_numeric(df["rank_no"], errors="coerce")
df["rating_score"] = pd.to_numeric(df["rating_score"], errors="coerce")
df["rating_count"] = pd.to_numeric(df["rating_count"], errors="coerce")
df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce")
df["duration_minutes"] = pd.to_numeric(df["duration_minutes"], errors="coerce")


# =========================
# 4. 页面标题
# =========================

st.title("🎬 豆瓣电影 Top100 可视化分析")
st.caption("数据来源：Python 爬虫采集豆瓣电影 Top100，CSV 托管于 GitHub，使用 Streamlit + Plotly 构建交互式可视化网站。")


# =========================
# 5. 侧边栏筛选器
# =========================

st.sidebar.header("筛选条件")

min_score = float(df["rating_score"].min())
max_score = float(df["rating_score"].max())

score_range = st.sidebar.slider(
    "评分范围",
    min_value=min_score,
    max_value=max_score,
    value=(min_score, max_score),
    step=0.1
)

year_min = int(df["release_year"].min())
year_max = int(df["release_year"].max())

year_range = st.sidebar.slider(
    "上映年份范围",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
    step=1
)

keyword = st.sidebar.text_input("搜索电影名 / 导演", "")


filtered_df = df[
    (df["rating_score"] >= score_range[0]) &
    (df["rating_score"] <= score_range[1]) &
    (df["release_year"] >= year_range[0]) &
    (df["release_year"] <= year_range[1])
]

if keyword:
    filtered_df = filtered_df[
        filtered_df["movie_name"].astype(str).str.contains(keyword, case=False, na=False) |
        filtered_df["director"].astype(str).str.contains(keyword, case=False, na=False)
    ]


# =========================
# 6. 数据概览卡片
# =========================

movie_count = len(filtered_df)
avg_score = round(filtered_df["rating_score"].mean(), 2)
avg_duration = round(filtered_df["duration_minutes"].mean(), 1)
max_rating_count = int(filtered_df["rating_count"].max()) if movie_count > 0 else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("电影数量", movie_count)
col2.metric("平均评分", avg_score)
col3.metric("平均时长", f"{avg_duration} 分钟")
col4.metric("最高评分人数", f"{max_rating_count:,}")


st.divider()


# =========================
# 7. 电影列表
# =========================

st.subheader("电影列表")

show_columns = [
    "rank_no",
    "movie_name",
    "director",
    "rating_score",
    "rating_count",
    "release_year",
    "country",
    "genres",
    "duration_minutes"
]

st.dataframe(
    filtered_df[show_columns].sort_values("rank_no"),
    use_container_width=True,
    height=380
)


st.divider()


# =========================
# 8. 第一行图表：评分Top10 + 评分人数Top10
# =========================

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("评分 Top10")

    top_score_df = (
        filtered_df
        .sort_values(["rating_score", "rating_count"], ascending=[False, False])
        .head(10)
        .sort_values("rating_score", ascending=True)
    )

    fig_score = px.bar(
        top_score_df,
        x="rating_score",
        y="movie_name",
        orientation="h",
        text="rating_score",
        title="评分最高的10部电影",
        labels={
            "rating_score": "评分",
            "movie_name": "电影名称"
        },
        color="rating_score",
        color_continuous_scale="Blues"
    )

    fig_score.update_layout(
        height=520,
        yaxis_title=None,
        xaxis_range=[8.5, 10],
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig_score, use_container_width=True)


with right_col:
    st.subheader("评分人数 Top10")

    top_count_df = (
        filtered_df
        .sort_values("rating_count", ascending=False)
        .head(10)
        .sort_values("rating_count", ascending=True)
    )

    fig_count = px.bar(
        top_count_df,
        x="rating_count",
        y="movie_name",
        orientation="h",
        text="rating_count",
        title="评分人数最多的10部电影",
        labels={
            "rating_count": "评分人数",
            "movie_name": "电影名称"
        },
        color="rating_count",
        color_continuous_scale="Viridis"
    )

    fig_count.update_layout(
        height=520,
        yaxis_title=None,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig_count, use_container_width=True)


st.divider()


# =========================
# 9. 第二行图表：国家饼图 + 类型柱状图
# =========================

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("国家 / 地区占比")

    country_df = filtered_df.copy()

    country_df["country_main"] = (
        country_df["country"]
        .astype(str)
        .str.replace("，", ",")
        .str.replace("/", ",")
        .str.split(",")
        .str[0]
        .str.strip()
    )

    country_count = (
        country_df
        .groupby("country_main")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    fig_country = px.pie(
        country_count,
        names="country_main",
        values="count",
        title="电影出品国家 / 地区占比",
        hole=0.42
    )

    fig_country.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig_country, use_container_width=True)


with right_col:
    st.subheader("电影类型分布")

    genre_list = []

    for genres in filtered_df["genres"].dropna():
        for genre in str(genres).replace("，", ",").split(","):
            genre = genre.strip()
            if genre:
                genre_list.append(genre)

    genre_df = pd.DataFrame(genre_list, columns=["genre"])

    genre_count = (
        genre_df
        .groupby("genre")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    fig_genre = px.bar(
        genre_count,
        x="genre",
        y="count",
        text="count",
        title="电影类型出现次数",
        labels={
            "genre": "电影类型",
            "count": "数量"
        },
        color="count",
        color_continuous_scale="Teal"
    )

    fig_genre.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig_genre, use_container_width=True)


st.divider()


# =========================
# 10. 第三行图表：年份趋势 + 散点图
# =========================

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("上映年份分布")

    year_count = (
        filtered_df
        .dropna(subset=["release_year"])
        .groupby("release_year")
        .size()
        .reset_index(name="count")
        .sort_values("release_year")
    )

    fig_year = px.line(
        year_count,
        x="release_year",
        y="count",
        markers=True,
        title="不同年份 Top100 电影数量分布",
        labels={
            "release_year": "上映年份",
            "count": "电影数量"
        }
    )

    fig_year.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig_year, use_container_width=True)


with right_col:
    st.subheader("评分与评分人数关系")

    fig_scatter = px.scatter(
        filtered_df,
        x="rating_count",
        y="rating_score",
        size="duration_minutes",
        color="release_year",
        hover_name="movie_name",
        title="评分、评分人数与电影时长关系",
        labels={
            "rating_count": "评分人数",
            "rating_score": "评分",
            "duration_minutes": "时长",
            "release_year": "年份"
        },
        color_continuous_scale="Plasma"
    )

    fig_scatter.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig_scatter, use_container_width=True)


st.divider()


# =========================
# 11. 关键词 / 类型词频
# =========================

st.subheader("关键词：电影类型词频 Top10")

keyword_top10 = genre_count.head(10)

fig_keyword = px.treemap(
    keyword_top10,
    path=["genre"],
    values="count",
    title="电影类型关键词热度",
    color="count",
    color_continuous_scale="Blues"
)

fig_keyword.update_layout(
    height=520,
    margin=dict(l=20, r=20, t=60, b=20)
)

st.plotly_chart(fig_keyword, use_container_width=True)


# =========================
# 12. 页面说明
# =========================

st.info(
    "说明：当前关键词基于 genres 字段统计，属于结构化关键词分析。"
    "如果后续采集电影简介或评论文本，可以进一步使用 jieba 做中文分词和词云分析。"
)