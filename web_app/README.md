# Douban Movie Visualization Web App

本项目是一个基于 React + Flask + MySQL + ECharts 的豆瓣电影可视化分析网站。项目以前期爬取并存储的豆瓣电影 Top100 数据为基础，通过 Flask 后端查询 MySQL 数据库，并将结果以 JSON 形式返回给 React 前端，最终使用 ECharts 绘制交互式可视化图表。

## Demo

### Demo Video

[View Demo Video](../docs/videos/douban_dashboard_demo.mp4)

## Project Overview

本可视化系统主要用于分析豆瓣电影 Top100 数据，关注电影评分、类型、国家/地区、上映年份、评分人数和关键词等维度。

整体流程如下：

```text
豆瓣电影数据爬取
↓
数据清洗并存入 MySQL
↓
Flask 后端查询数据库
↓
后端返回 JSON 数据
↓
React 前端请求接口
↓
ECharts 绘制交互式图表
```

## Main Features

本项目目前实现了以下可视化功能：

```text
1. 评分分布条形图：展示不同评分区间的电影数量
2. 类型占比饼图：展示电影类型分布情况
3. 国家 / 地区占比饼图：展示电影来源地区分布
4. 年份趋势折线图：展示不同上映年份的电影数量和平均评分变化
5. 评分人数 TopN 条形图：展示关注度最高的电影
6. 关键词 TopN 图表：基于类型、导演、演员字段统计高频关键词
7. 交互功能：支持菜单切换、TopN 选择、图表悬停提示、图例筛选和趋势图缩放
```

## Project Structure

```text
web_app/
├── __init__.py
│
├── backend/
│   ├── __init__.py
│   ├── app.py
│   ├── dashboard_app.py
│   └── services/
│       ├── __init__.py
│       └── chart_service.py
│
└── frontend/
    ├── package.json
    ├── package-lock.json
    ├── index.html
    ├── vite.config.js
    ├── eslint.config.js
    ├── public/
    └── src/
        ├── App.jsx
        ├── App.css
        ├── index.css
        ├── main.jsx
        ├── api/
        │   └── chartApi.js
        └── components/
            └── DoubanDashboard.jsx

项目根目录中还包含两个与本模块相关的 example：

examples/
├── douban_chart_service_usage.py
└── run_douban_dashboard_usage.py
```

## Backend Design

后端采用面向对象方式组织核心逻辑，主要包含两个类：

```text
DoubanChartService
DoubanDashboardApp
```

### 1. DoubanChartService

文件位置：

```text
web_app/backend/services/chart_service.py
```

`DoubanChartService` 是豆瓣电影图表数据服务类，负责连接 MySQL、查询 `douban_movie_top100` 表，并将数据库结果整理成前端图表可以直接使用的数据结构。

该类提供以下方法：

```text
get_rating_distribution()
get_genre_distribution(top_n=10)
get_country_distribution(top_n=10)
get_year_trend()
get_rating_count_top(top_n=10)
get_keywords(top_n=30)
get_dashboard_data(top_n=10, keyword_top_n=30)
```

示例用法：

```python
service = DoubanChartService()

genre_data = service.get_genre_distribution(top_n=10)

dashboard_data = service.get_dashboard_data(
    top_n=10,
    keyword_top_n=30
)
```


---

### 2. DoubanDashboardApp

文件位置：

```text
web_app/backend/dashboard_app.py
```

`DoubanDashboardApp` 是网站启动类，负责检查数据、启动 Flask 后端、启动 React 前端，并打开可视化网页。

该类提供以下方法：

```text
check_data()
start_backend()
start_frontend()
open_dashboard()
run()
stop()
```

示例用法：

```python
dashboard = DoubanDashboardApp(
    top_n=10,
    keyword_top_n=30
)

dashboard.run()
```

其中，`run()` 会按顺序执行：

```text
检查 MySQL 中的豆瓣电影数据
↓
启动 Flask 后端
↓
启动 React 前端
↓
打开 Dashboard 网页
```

---

## Backend API

Flask 后端文件为：

```text
web_app/backend/app.py
```

该文件主要负责接收前端请求，并调用 `DoubanChartService` 中的方法返回 JSON 数据。

当前提供的接口包括：

```text
GET /api/charts/douban-rating
```

返回评分分布数据，用于绘制评分分布条形图。

```text
GET /api/charts/douban-genres?top_n=10
```

返回电影类型 TopN 分布数据，用于绘制类型占比饼图。

```text
GET /api/charts/douban-country?top_n=10
```

返回国家 / 地区 TopN 分布数据，用于绘制地区占比饼图。

```text
GET /api/charts/douban-year-trend
```

返回上映年份、电影数量和平均评分数据，用于绘制年份趋势折线图。

```text
GET /api/charts/douban-rating-count-top?top_n=10
```

返回评分人数 TopN 电影数据，用于绘制电影热度排行条形图。

```text
GET /api/charts/douban-keywords?top_n=30
```

返回基于类型、导演、演员字段统计出的高频关键词。

```text
GET /api/charts/douban-dashboard?top_n=10&keyword_top_n=30
```

一次性返回 Dashboard 所需的全部图表数据。

---

## Frontend Design

前端使用 React + Vite 构建，主要负责页面展示、用户交互和图表绘制。

核心文件包括：

```text
frontend/src/App.jsx
frontend/src/components/DoubanDashboard.jsx
frontend/src/api/chartApi.js
frontend/src/App.css
frontend/src/index.css
```

### chartApi.js

文件位置：

```text
web_app/frontend/src/api/chartApi.js
```

该文件统一管理前端对 Flask 后端接口的请求。

例如：

```javascript
fetchDoubanGenreDistribution(topN)
fetchDoubanRatingCountTop(topN)
fetchDoubanKeywords(topN)
```

这些函数不会直接访问 MySQL，而是请求 Flask API。

---

### DoubanDashboard.jsx

文件位置：

```text
web_app/frontend/src/components/DoubanDashboard.jsx
```

该文件是核心可视化页面，负责：

```text
1. 调用 chartApi.js 获取后端 JSON 数据
2. 根据数据生成 ECharts 图表配置
3. 使用 Ant Design 实现 Tabs、Card、Select 等页面交互
4. 根据用户选择的 TopN 动态更新图表
```

---

## Visualization Design

本项目使用 ECharts 绘制图表，结合 Ant Design 实现页面布局和交互。

当前图表类型包括：

```text
Bar Chart：评分分布、评分人数 TopN、关键词 TopN
Pie Chart：电影类型占比、国家 / 地区占比
Line Chart：上映年份趋势、平均评分趋势
Interactive Controls：TopN 选择器、Tabs 切换、tooltip 悬停提示、dataZoom 缩放
```

这些图表可以帮助用户从多个维度理解豆瓣高分电影的结构特征，例如：

```text
哪些评分区间电影数量更多
哪些类型更常见
哪些国家 / 地区电影占比较高
哪些年份电影数量较多
哪些电影获得了更高关注度
哪些导演、演员、类型关键词出现频率较高
```

---

## How to Run

### Method 1：一键启动 Dashboard

在项目根目录下运行：

```bash
python3 examples/run_douban_dashboard_usage.py
```

该脚本会调用：

```text
DoubanDashboardApp
```

并自动执行：

```text
检查数据
启动 Flask 后端
启动 React 前端
打开 Dashboard 网页
```

如果运行成功，浏览器会自动打开：

```text
http://localhost:5173
```

---

### Method 2：手动启动后端和前端

#### 1. Start Flask Backend

在项目根目录下运行：

```bash
cd web_app/backend
python3 app.py
```

如果后端启动成功，会看到：

```text
Running on http://127.0.0.1:5000
```

可以在浏览器中访问：

```text
http://127.0.0.1:5000/
```

如果返回 Flask 启动信息，说明后端运行正常。

---

#### 2. Start React Frontend

打开另一个 terminal，在项目根目录下运行：

```bash
cd web_app/frontend
npm install
npm run dev
```

如果前端启动成功，会看到：

```text
Local: http://localhost:5173/
```

然后在浏览器中打开：

```text
http://localhost:5173/
```

即可查看豆瓣电影可视化 Dashboard。

---

## Usage Examples

### 1. Directly Use DoubanChartService

文件位置：

```text
examples/douban_chart_service_usage.py
```

运行：

```bash
python3 examples/douban_chart_service_usage.py
```

该 example 展示如何直接调用 `DoubanChartService` 类获取图表数据，例如：

```python
service = DoubanChartService()

rating_data = service.get_rating_distribution()
genre_data = service.get_genre_distribution(top_n=10)
dashboard_data = service.get_dashboard_data(top_n=10, keyword_top_n=30)
```

这个 example 主要用于说明：后端图表数据处理逻辑已经封装成一个可复用的服务类，不依赖网页也可以直接调用。

---

### 2. Start the Dashboard with DoubanDashboardApp

文件位置：

```text
examples/run_douban_dashboard_usage.py
```

运行：

```bash
python3 examples/run_douban_dashboard_usage.py
```

该 example 展示如何通过 `DoubanDashboardApp` 一键启动完整网站，例如：

```python
dashboard = DoubanDashboardApp(
    top_n=10,
    keyword_top_n=30
)

dashboard.run()
```

这个 example 主要用于说明：开发者可以通过一个启动类快速运行整个豆瓣电影可视化网站。

---

## Dependencies

### Python Backend

后端依赖主要包括：

```text
Flask
flask-cors
pymysql
```

其中：

```text
Flask：用于搭建后端接口
flask-cors：用于解决 React 前端访问 Flask 后端时的跨域问题
pymysql：用于连接 MySQL 数据库
```

Python 依赖可以通过项目根目录的 `requirements.txt` 安装。

---

### React Frontend

前端依赖由：

```text
web_app/frontend/package.json
```

管理，主要包括：

```text
React
Vite
ECharts
echarts-for-react
Ant Design
```

其中：

```text
ECharts：用于绘制图表
echarts-for-react：用于在 React 中使用 ECharts
Ant Design：用于页面布局、卡片、Tabs、选择器等组件
```

前端依赖安装方式：

```bash
cd web_app/frontend
npm install
```

---

## Data Source

本网站使用的数据来自前期豆瓣电影爬虫模块。爬虫结果主要保存到两个位置：

```text
results/douban_movie_top100.csv
```

该文件是豆瓣电影数据的 CSV 结果备份。

```text
MySQL table: douban_movie_top100
```

该表是网站运行时真正查询的数据源。

建表 SQL 位于：

```text
sql/create_douban_movie_table.sql
```

数据库连接配置位于：

```text
config/config.py
```

该文件包含本地 MySQL 账号密码，不应上传到 GitHub。GitHub 中只保留配置模板：

```text
config/config_example.py
```

---

## Notes

运行本网站前，需要确保：

```text
1. MySQL 服务已启动
2. 数据库中已经创建 douban_movie_top100 表
3. 豆瓣电影数据已经成功写入 MySQL
4. config/config.py 中的数据库连接信息正确
5. React 前端依赖已经通过 npm install 安装
```

如果数据库中没有数据，Dashboard 页面无法正常展示图表。

---

