from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
import jieba
from collections import Counter


input_path = PROJECT_ROOT / "results" / "douban_rule_reason_analysis.csv"
output_path = PROJECT_ROOT / "results" / "unrecognized_reviews_sample.csv"
keyword_output_path = PROJECT_ROOT / "results" / "unrecognized_keywords.csv"

df = pd.read_csv(input_path)

unknown_df = df[df["main_aspect"] == "未识别"].copy()

print("总评论数：", len(df))
print("未识别评论数：", len(unknown_df))
print("未识别比例：", round(len(unknown_df) / len(df), 4))

print("\n未识别评论按评论级别分布：")
print(unknown_df["comment_sentiment_type"].value_counts())

print("\n未识别评论样例：")
preview_columns = [
    "movie_name",
    "comment_sentiment_name",
    "review_star",
    "clean_review_text",
    "review_like_count"
]

print(unknown_df[preview_columns].head(50))

unknown_df[preview_columns].head(300).to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)

stopwords = {
    "电影", "一个", "真的", "还是", "就是", "觉得", "没有", "不是", "但是",
    "非常", "可以", "因为", "所以", "这个", "那个", "什么", "已经", "一部",
    "这么", "那么", "有点", "特别", "其实", "可能", "比较", "虽然", "如果",
    "时候", "这种", "一种", "看到", "看完", "感觉", "豆瓣", "这部", "片子",
    "自己", "最后", "还有", "很多", "第一次", "第二次", "不是", "不能",
    "我们", "他们", "你们", "它们", "然后", "只是", "真是"
}

word_counter = Counter()

for text in unknown_df["clean_review_text"].dropna():
    words = jieba.lcut(str(text))

    for word in words:
        word = word.strip()

        if len(word) < 2:
            continue

        if word in stopwords:
            continue

        if word.isdigit():
            continue

        word_counter[word] += 1

keyword_df = pd.DataFrame(
    word_counter.most_common(200),
    columns=["keyword", "count"]
)

keyword_df.to_csv(
    keyword_output_path,
    index=False,
    encoding="utf-8-sig"
)

print("\n未识别评论高频词 Top 100：")
print(keyword_df.head(100))

print("\n已保存未识别评论样例：", output_path)
print("已保存未识别高频词：", keyword_output_path)