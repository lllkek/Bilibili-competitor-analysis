CREATE DATABASE IF NOT EXISTS web_crawler_db DEFAULT CHARACTER SET utf8mb4;

USE web_crawler_db;

DROP TABLE IF EXISTS douban_movie_reviews;

CREATE TABLE douban_movie_reviews (
    id INT PRIMARY KEY AUTO_INCREMENT,
    movie_name VARCHAR(255),
    movie_url VARCHAR(255),
    comment_url VARCHAR(255),
    comment_sentiment_type VARCHAR(50),
    user_name VARCHAR(255),
    review_text TEXT,
    review_star INT,
    review_time DATETIME,
    review_like_count INT,
    crawl_time DATETIME
);
