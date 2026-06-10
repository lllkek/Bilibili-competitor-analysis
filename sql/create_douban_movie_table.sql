CREATE DATABASE IF NOT EXISTS web_crawler_db DEFAULT CHARACTER SET utf8mb4;

USE web_crawler_db;

DROP TABLE IF EXISTS douban_movie_top100;

CREATE TABLE douban_movie_top100(
    id INT PRIMARY KEY AUTO_INCREMENT,
    rank_no INT ,
    movie_name VARCHAR(255),
    director VARCHAR(255),
    actors TEXT,
    rating_score DECIMAL(3,1),
    rating_count INT,
    release_year INT,
    genres VARCHAR(255),
    duration_minutes INT,
    country VARCHAR(255),
    crawl_time DATETIME
);