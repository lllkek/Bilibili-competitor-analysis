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
    rank_no INT NOT NULL,
    movie_name VARCHAR(255) NOT NULL,
    director VARCHAR(255),
    rating_score DECIMAL(3,1),
    rating_count INT,
    release_year INT,
    country VARCHAR(255),
    genres VARCHAR(255),
    duration_minutes INT
);