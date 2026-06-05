import time
import random
import re
import requests
from bs4 import BeautifulSoup
from config import cookie

url = "https://movie.douban.com/top250"  
# 1. 设置请求头

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/148.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Cookie": cookie
}

# ====================
#Step 1：定义访问网页函数
# ====================
def get_html(url):
    """
    输入一个网页 URL，返回网页 HTML 源码。
    如果访问失败，返回 None。
    """

    sleep_time = random.uniform(1, 2)
    print(f"等待 {sleep_time:.2f} 秒后访问网页：{url}")
    time.sleep(sleep_time)

    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = "utf-8"

    print("网页状态码:", response.status_code)

    if response.status_code != 200:
        print("网页访问失败:", url)

        with open("douban_debug.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        print("已保存返回内容到 douban_debug.html")
        return None

    return response.text

# ====================
#Step 2：定义解析列表页函数
# ====================
def parse_list_page(html):
    """
    解析豆瓣 Top250 列表页。
    返回当前页面的电影排名和详情页 URL。
    """

    soup = BeautifulSoup(html, "lxml")

    # 每个 li 是一部电影
    movie_items = soup.select("ol.grid_view > li")

    current_page_movie_urls = []

    for item in movie_items:
        # 排名
        rank_tag = item.select_one("em")

        # 详情页链接
        link_tag = item.select_one("div.hd a")

        if rank_tag is None or link_tag is None:
            continue

        rank_no = int(rank_tag.get_text(strip=True))
        detail_url = link_tag.get("href")

        current_page_movie_urls.append({
            "rank_no": rank_no,
            "detail_url": detail_url
        })

    return current_page_movie_urls

# ====================
# Step 3：循环获取 Top100 的排名和详情页 URL，保存到 movie_url_list
# ====================


movie_url_list = []


for start in [0, 25, 50, 75]:
    page_url = f"https://movie.douban.com/top250?start={start}&filter="

    print("\n正在处理列表页:", page_url)

    html = get_html(page_url)

    if html is None:
        continue

    current_page_urls = parse_list_page(html)

    print("当前页面解析到:", len(current_page_urls), "条")

    movie_url_list.extend(current_page_urls)


# 只保留前100条
movie_url_list = movie_url_list[:100]


print("\nTop100 详情页 URL 获取完成")
print("总数量:", len(movie_url_list))

print("\n前5条检查：")
for movie in movie_url_list[:5]:
    print(movie)

print("\n最后5条检查：")
for movie in movie_url_list[-5:]:
    print(movie)

# ====================
#Step 4：定义详情页解析函数
# ====================
def extract_info_by_label(info_text, label):
    """
    从详情页 #info 文本中提取字段。
    例如：提取 制片国家/地区、语言 等。
    """

    pattern = rf"{label}:\s*(.*)"
    match = re.search(pattern, info_text)

    if match:
        return match.group(1).strip()

    return ""


def parse_detail_page(html, rank_no, detail_url):
    """
    解析电影详情页，提取目标字段：
    排名、电影名、导演、演员、评分、评分人数、年份、国家、类型、时长、详情页链接。
    """

    soup = BeautifulSoup(html, "lxml")

    # 电影名
    title_tag = soup.select_one("h1 span[property='v:itemreviewed']")
    movie_name = title_tag.get_text(strip=True) if title_tag else ""

    # 导演
    director_tags = soup.select("a[rel='v:directedBy']")
    director = ",".join([tag.get_text(strip=True) for tag in director_tags])

    # 演员
    actor_tags = soup.select("a[rel='v:starring']")
    actors = ",".join([tag.get_text(strip=True) for tag in actor_tags])

    # 评分
    rating_tag = soup.select_one("strong[property='v:average']")
    rating_score = rating_tag.get_text(strip=True) if rating_tag else ""

    # 评分人数
    votes_tag = soup.select_one("span[property='v:votes']")
    rating_count = votes_tag.get_text(strip=True) if votes_tag else ""

    # 年份
    release_date_tag = soup.select_one("span[property='v:initialReleaseDate']")
    release_date = release_date_tag.get_text(strip=True) if release_date_tag else ""

    release_year = ""
    year_match = re.search(r"\d{4}", release_date)
    if year_match:
        release_year = year_match.group()

    # 类型
    genre_tags = soup.select("span[property='v:genre']")
    genres = ",".join([tag.get_text(strip=True) for tag in genre_tags])

    # 时长
    runtime_tag = soup.select_one("span[property='v:runtime']")
    duration_text = runtime_tag.get_text(strip=True) if runtime_tag else ""

    duration_minutes = ""
    duration_match = re.search(r"\d+", duration_text)
    if duration_match:
        duration_minutes = duration_match.group()

    # 国家/地区：通常在 #info 文本中
    info_tag = soup.select_one("#info")
    info_text = info_tag.get_text("\n", strip=True) if info_tag else ""

    country = extract_info_by_label(info_text, "制片国家/地区")

    # 爬取时间
    #crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    movie_data = {
        "rank_no": rank_no,
        "movie_name": movie_name,
        "director": director,
        #"actors": actors,
        "rating_score": rating_score,
        "rating_count": rating_count,
        "release_year": release_year,
        "country": country,
        "genres": genres,
        "duration_minutes": duration_minutes
        #"detail_url": detail_url
        #"crawl_time": crawl_time
    }

    return movie_data


# ====================
#  step 5：循环爬取 Top100 详情页，解析并保存到
# ====================
movie_detail_list = []


for movie in movie_url_list:
    rank_no = movie["rank_no"]
    detail_url = movie["detail_url"]

    print(f"\n正在爬取第 {rank_no} 名电影详情页：{detail_url}")

    detail_html = get_html(detail_url)

    if detail_html is None:
        print("该详情页访问失败，跳过")
        continue

    movie_data = parse_detail_page(
        html=detail_html,
        rank_no=rank_no,
        detail_url=detail_url
    )

    movie_detail_list.append(movie_data)

    print("已保存:", movie_data["rank_no"], movie_data["movie_name"])


print("\n详情页爬取完成")

print("最终电影数量:", len(movie_detail_list))

print("\n前5条电影数据：")
for movie in movie_detail_list[:5]:
    print(movie)
    print("-" * 80)

print("\n最后5条电影数据：")
for movie in movie_detail_list[-5:]:
    print(movie)
    print("-" * 80)

# ====================
# Step 6：把 movie_detail_list 写入 MySQL
# ====================

from mysqlhelper import MySqlHelper
from config import DB_CONFIG

# 1. 创建 MySQLHelper 对象
db = MySqlHelper(
    host=DB_CONFIG["host"],
    port=DB_CONFIG["port"],
    user=DB_CONFIG["user"],
    password=DB_CONFIG["password"],
    database=DB_CONFIG["database"],
    charset=DB_CONFIG["charset"]
)

# 2. 准备 INSERT SQL
sql = """
INSERT INTO douban_movie_top100
(rank_no, movie_name, director, rating_score, rating_count, release_year, country, genres, duration_minutes)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# 3. 把 movie_detail_list 转成 tuple list
data = []

for movie in movie_detail_list:
    data.append((
        int(movie["rank_no"]) if movie["rank_no"] else None,
        movie["movie_name"],
        movie["director"],
        float(movie["rating_score"]) if movie["rating_score"] else None,
        int(movie["rating_count"]) if movie["rating_count"] else None,
        int(movie["release_year"]) if movie["release_year"] else None,
        movie["country"],
        movie["genres"],
        int(movie["duration_minutes"]) if movie["duration_minutes"] else None
    ))


# 4. 批量插入 MySQL
if len(data) > 0:
    db.executemany(sql, data)
    print("豆瓣电影 Top100 数据已写入 MySQL")
else:
    print("movie_detail_list 为空，没有数据可插入")

# =====================
# step 7：把 movie_detail_list 保存为 CSV 文件
# =====================

if len(movie_detail_list) > 0:
    # 把字典列表转换成 DataFrame
    df = pd.DataFrame(movie_detail_list)

    # 按照想要的字段顺序整理列
    df = df[
        [
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
    ]

    # 保存为 CSV
    # encoding="utf-8-sig" 可以避免 Excel 打开中文乱码
    df.to_csv("/Users/lllkek/Desktop/Bilibili-Project/week3_douban_movie/douban_movie_top100.csv", index=False, encoding="utf-8-sig")

    print("豆瓣电影 Top100 数据已保存为 CSV 文件：douban_movie_top100.csv")
else:
    print("movie_detail_list 为空，没有数据可保存为 CSV")