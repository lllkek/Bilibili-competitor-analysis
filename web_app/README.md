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
├── backend/
│   ├── app.py
│   └── services/
│       ├── __init__.py
│       └── chart_service.py
│
└── frontend/
    ├── package.json
    ├── package-lock.json
    ├── index.html
    └── src/
        ├── App.jsx
        ├── App.css
        ├── index.css
        ├── main.jsx
        ├── api/
        │   └── chartApi.js
        └── components/
            └── DoubanDashboard.jsx
```

## Backend Explanation

后端使用 Flask 搭建，主要文件为：

```text
web_app/backend/app.py
```

数据库查询逻辑被单独放在：

```text
web_app/backend/services/chart_service.py
```


后端复用项目已有的公共数据库工具：

```text
src/utils/mysql_helper.py
```

并读取项目配置文件：

```text
config/config.py
```



## Backend API

当前后端提供以下接口：

```text
GET /api/charts/douban-rating
```

返回豆瓣电影评分分布数据，用于绘制评分分布条形图。

```text
GET /api/charts/douban-genres?top_n=10
```

返回豆瓣电影类型分布数据，用于绘制类型占比饼图。

```text
GET /api/charts/douban-country?top_n=10
```

返回豆瓣电影国家 / 地区分布数据，用于绘制地区占比饼图。

```text
GET /api/charts/douban-year-trend
```

返回不同上映年份的电影数量和平均评分，用于绘制年份趋势折线图。

```text
GET /api/charts/douban-rating-count-top?top_n=10
```

返回评分人数最高的电影，用于绘制热度排行条形图。

```text
GET /api/charts/douban-keywords?top_n=30
```

返回基于电影类型、导演和演员字段统计出的高频关键词。

## Frontend Explanation

前端使用 React 和 Vite 构建，主要负责页面展示、用户交互和图表绘制。

主要文件包括：

```text
frontend/src/App.jsx
frontend/src/components/DoubanDashboard.jsx
frontend/src/api/chartApi.js
frontend/src/App.css
```

`App.jsx` 是前端主入口组件。

`DoubanDashboard.jsx` 是核心可视化页面，包含多个图表和交互逻辑。

`chartApi.js` 负责统一管理前端请求后端接口的代码。

`App.css` 和 `index.css` 负责页面样式。

## Visualization Design

本项目使用 ECharts 绘制图表，结合 Ant Design 实现页面布局和交互组件。

当前图表设计包括：

```text
Bar Chart：评分分布、评分人数 TopN、关键词 TopN
Pie Chart：电影类型占比、国家 / 地区占比
Line Chart：上映年份趋势、平均评分趋势
Interactive Controls：TopN 选择器、Tabs 切换、tooltip 悬停提示、dataZoom 缩放
```

这些图表可以帮助用户从多个角度理解豆瓣高分电影的结构特征，例如哪些类型更常见、哪些国家/地区电影占比较高、哪些年份电影数量较多、哪些电影获得了更高关注度。

## How to Run

### 1. Start Flask Backend

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

### 2. Start React Frontend

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

### React Frontend

前端依赖主要由 `package.json` 管理，包括：

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

## Notes

运行本项目之前，需要确保 MySQL 中已经存在豆瓣电影数据表：

```text
douban_movie_top100
```

该表由前期爬虫模块生成，相关建表 SQL 位于：

```text
sql/create_douban_movie_table.sql
```

数据库连接配置位于：

```text
config/config.py
```

```text
config/config_example.py
```

