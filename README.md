# Bilibili Competitor Analysis Training

本项目是围绕后续 Bilibili 竞品分析任务展开的 Python 数据采集、数据库存储与可视化练习项目。

## 文件夹说明

`src/` 是项目核心源代码目录，存放可以被复用的正式代码。

`src/utils/mysql_helper.py` 是公共 MySQL 工具类，百度爬虫和豆瓣爬虫都通过它写入 MySQL。

`src/crawlers/` 存放爬虫类。百度热搜爬虫对应 `BaiduHotCrawler`，豆瓣电影爬虫对应 `DoubanMovieCrawler`。

`scripts/` 存放正式运行入口。想直接运行百度热搜top10或豆瓣电影top100爬虫时，可以运行这里的文件。

`examples/` 存放使用示例，展示如何 import 爬虫 class 并传入参数使用。

`sql/` 存放 MySQL 建表语句。

`results/` 存放爬虫运行后导出的 CSV 结果文件。

`config_example.py` 是配置模板。

## 安装依赖

在项目根目录运行：

```bash
pip3 install -r requirements.txt
```

## 配置文件

首次使用时，需要复制配置模板：

```bash
cp config/config_example.py config/config.py
```

然后在 `config/config.py` 中填写本地真实配置。



## 创建 MySQL 数据表

运行百度爬虫前，需要先在 MySQL 中执行：

```text
sql/create_baidu_hot_table.sql
```

运行豆瓣爬虫前，需要先在 MySQL 中执行：

```text
sql/create_douban_movie_table.sql
```

执行成功后，数据库中会生成：

```text
web_crawler_db.baidu_hot_search
web_crawler_db.douban_movie_top100
```

## 百度热搜爬虫使用方法

### 方式一：通过 scripts 直接运行

```bash
python3 scripts/run_baidu_crawler.py
```

该方式会按照 `scripts/run_baidu_crawler.py` 中设置的参数运行百度热搜爬虫。

### 方式二：通过 class 自定义调用

```python
from src.crawlers.baidu_hot_crawler import BaiduHotCrawler

crawler = BaiduHotCrawler(
    top_n=10,
    save_mysql=True,
    save_csv=True
)

data = crawler.run()
```

参数说明：

```text
top_n       控制爬取多少条百度热搜
save_mysql  是否保存到 MySQL
save_csv    是否保存为 CSV
```

百度热搜默认字段包括：

```text
rank_no
keyword
hot_score
url
crawl_time
```

## 豆瓣电影爬虫使用方法

### 方式一：通过 scripts 直接运行

```bash
python3 scripts/run_douban_crawler.py
```

该方式会按照 `scripts/run_douban_crawler.py` 中设置的参数运行豆瓣电影爬虫。

### 方式二：通过 class 自定义调用

```python
from src.crawlers.douban_movie_crawler import DoubanMovieCrawler

crawler = DoubanMovieCrawler(
    top_n=100,
    save_mysql=True,
    save_csv=True
)

data = crawler.run()
```

参数说明：

```text
top_n       控制爬取多少部电影
save_mysql  是否保存到 MySQL
save_csv    是否保存为 CSV
fields      控制保存哪些字段
```

豆瓣电影默认字段包括：

```text
rank_no
movie_name
director
actors
rating_score
rating_count
release_year
genres
duration_minutes
country
crawl_time
```

如果只想保存部分字段，可以传入 `fields` 参数：

```python
from src.crawlers.douban_movie_crawler import DoubanMovieCrawler

crawler = DoubanMovieCrawler(
    top_n=20,
    save_mysql=False,
    save_csv=True,
    fields=[
        "rank_no",
        "movie_name",
        "director",
        "actors",
        "rating_score"
    ]
)

data = crawler.run()
```

## 示例文件

百度热搜使用示例：

```bash
python3 examples/baidu_basic_usage.py
```

豆瓣电影使用示例：

```bash
python3 examples/douban_basic_usage.py
```

`examples/` 文件夹的作用是展示如何调用爬虫 class。正式代码逻辑仍然放在 `src/crawlers/` 中。

## 输出结果

运行百度热搜爬虫后，会生成：

```text
results/baidu_hot_search.csv
```

运行豆瓣电影爬虫后，会生成：

```text
results/douban_movie_top100.csv
```

如果设置 `save_mysql=True`，数据也会同步写入 MySQL。

