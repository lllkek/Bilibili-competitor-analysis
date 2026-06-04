-- 创建爬虫项目数据库
CREATE DATABASE IF NOT EXISTS web_crawler_db
DEFAULT CHARACTER SET utf8mb4;

-- 使用数据库
USE web_crawler_db;

-- 如果之前已经存在同名表，先删除，方便重新练习
DROP TABLE IF EXISTS douban_movie_top100;

-- 创建豆瓣电影 Top100 表
CREATE TABLE douban_movie_top100 (
    id INT PRIMARY KEY AUTO_INCREMENT,
    -- 榜单排名，例如 1, 2, 3
    rank_no INT NOT NULL,
    -- 电影名称
    movie_name VARCHAR(255) NOT NULL,
    -- 导演
    director VARCHAR(255),

    -- 豆瓣评分，例如 9.7
    rating_score DECIMAL(3,1),

    -- 评分人数，例如 3045678
    rating_count INT,

    -- 上映年份，例如 1994
    release_year INT,

    -- 国家/地区，例如 美国、中国大陆、日本；多个地区先用逗号分隔
    country VARCHAR(255),

    -- 电影类型，例如 剧情、犯罪、爱情；多个类型先用逗号分隔
    genres VARCHAR(255),

    -- 电影时长，单位：分钟
    duration_minutes INT,

    -- 豆瓣详情页链接
    detail_url VARCHAR(500),

    -- 爬取时间，具体到年月日时分秒
    crawl_time DATETIME,

    -- 防止同一个电影链接重复插入
    UNIQUE KEY unique_detail_url (detail_url)
);