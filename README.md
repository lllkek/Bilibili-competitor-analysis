# Bilibili Competitor Analysis Training

本项目是围绕后续 Bilibili 竞品分析任务展开的 Python 数据采集、数据库存储与可视化练习项目。

## 在线可视化网站
https://douban-movie-visualization.streamlit.app/

## 项目结构

### Week 1：MySQL 基础练习

`week1_mysql` 文件夹主要完成 MySQL 数据库、数据表和基础 SQL 操作练习。

主要内容包括：

* 使用 SQL 创建学生数据库和学生表
* 学生表字段包括学生编号、姓名、身高
* 练习 SQL 基础增删改查操作
* 通过 DBeaver 检查数据库表结构和查询结果

主要文件：

* `Week1_Create_Student_db.sql`：创建学生数据库、学生表，并完成基础数据插入与查询练习


## Week 2：百度热搜数据爬取与 MySQL 入库

`week2_baidu_hot` 文件夹主要完成百度热搜 Top10 的网页爬取、数据解析、MySQL 表设计与数据存储。

主要内容包括：

* 使用 `requests` 请求百度热搜网页
* 使用 `BeautifulSoup` 解析网页 HTML
* 提取百度热搜名称、热度值、链接和爬取时间
* 创建百度热搜数据表
* 使用 Python 将爬取结果写入 MySQL
* 封装 `mysqlhelper.py`，减少重复的数据库连接和写入代码

主要文件：

* `crawl_baidu.py`：百度热搜爬虫代码
* `mysqlhelper.py`：MySQL 数据库操作封装类
* `create-db-template.sql`：百度热搜相关数据库表创建 SQL
* `baidu_hot_search.csv`：百度热搜数据表格

## Week 3：豆瓣电影 Top100 爬取、入库与可视化

`week3_douban_movie` 文件夹主要完成豆瓣电影 Top100 的两级爬虫、MySQL 数据存储、CSV 导出和 Streamlit 可视化网站。

主要内容包括：

* 从豆瓣电影 Top250 页面循环获取 Top100 电影列表
* 提取每部电影的排名和详情页 URL
* 进入每个电影详情页继续爬取具体字段
* 采集字段包括：排名、电影名、导演、评分、评分人数、年份、国家、类型、时长
* 将电影数据批量写入 MySQL
* 将电影数据导出为 CSV
* 使用 Streamlit + Plotly 构建交互式可视化网站

主要文件：

* `crawl_douban_movie.py`：豆瓣电影 Top100 爬虫、数据解析与入库代码
* `create_douban_movie_table.sql`：豆瓣电影数据表创建 SQL
* `douban_movie_top100.csv`：豆瓣电影 Top100 数据结果文件
* `mysqlhelper.py`：MySQL 数据库操作封装类
* `app_douban_streamlit.py`：Streamlit 可视化网站代码
* `requirements.txt`：Streamlit 部署所需 Python 依赖包

当前可视化网站包含以下模块：

* 电影数据总览
* 电影列表展示
* 评分 Top10 柱状图
* 评分人数 Top10 柱状图
* 国家 / 地区电影占比饼图
* 电影类型分布柱状图
* 上映年份趋势折线图
* 评分与评分人数关系散点图
* 电影类型关键词分析

## 技术栈

本项目使用的主要技术包括：

* Python：数据采集、数据清洗与自动化处理
* Requests：网页请求
* BeautifulSoup：HTML 解析
* MySQL：结构化数据存储
* DBeaver：数据库可视化管理工具
* PyMySQL：Python 连接 MySQL
* Pandas：数据整理与统计分析
* Streamlit：交互式数据可视化网站搭建
* Plotly：交互式图表绘制
* GitHub：代码管理与项目提交
* Streamlit Community Cloud：可视化网站部署



## 当前成果

目前已完成：

* Week 1 MySQL 基础练习
* Week 2 百度热搜爬虫与 MySQL 入库
* Week 3 豆瓣电影 Top100 爬虫、MySQL 入库、CSV 保存
* Streamlit 可视化网站部署



