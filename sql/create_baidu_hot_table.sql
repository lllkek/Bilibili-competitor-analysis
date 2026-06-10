-- 创建数据库
CREATE DATABASE IF NOT EXISTS web_crawler_db
DEFAULT CHARACTER SET utf8mb4;

-- 使用数据库
USE web_crawler_db;

-- 如果旧表存在，先删除
DROP TABLE IF EXISTS baidu_hot_search;

-- 创建百度热搜表
CREATE TABLE baidu_hot_search (
    id int PRIMARY KEY AUTO_INCREMENT ,
    rank_no int NOT NULL,
    keyword VARCHAR(255) NOT NULL,
    hot_score VARCHAR(100),
    url VARCHAR(500),
    crawl_time DATETIME
);

