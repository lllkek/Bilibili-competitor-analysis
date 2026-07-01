import re
from pathlib import Path

import pandas as pd


class ReviewTextCleaner:
    """
    豆瓣电影短评文本清洗类。

    功能：
    1. 读取爬取下来的豆瓣短评 CSV
    2. 清洗 review_text
    3. 保留 comment_sentiment_type，也就是 positive / neutral / negative
    4. 删除空评论、重复评论、过短评论
    5. 保存清洗后的结果 CSV

    注意：
    这里不判断评论是好评还是差评。
    因为情绪类别已经由豆瓣筛选页面决定：
    positive = 好评
    neutral = 一般
    negative = 差评
    """

    def __init__(
        self,
        input_path=None,
        output_path=None,
        min_text_length=4
    ):
        self.project_root = Path(__file__).resolve().parents[2]

        if input_path is None:
            self.input_path = self.project_root / "results" / "douban_movie_reviews.csv"
        else:
            self.input_path = Path(input_path)

        if output_path is None:
            self.output_path = self.project_root / "results" / "douban_movie_reviews_cleaned.csv"
        else:
            self.output_path = Path(output_path)

        self.min_text_length = min_text_length

    def load_data(self):
        """
        读取原始评论 CSV。
        """

        if not self.input_path.exists():
            raise FileNotFoundError(f"找不到输入文件：{self.input_path}")

        df = pd.read_csv(self.input_path)

        print(f"读取原始评论数据：{len(df)} 条")
        print(f"字段：{df.columns.tolist()}")

        required_columns = [
            "movie_name",
            "comment_sentiment_type",
            "review_text"
        ]

        for column in required_columns:
            if column not in df.columns:
                raise ValueError(f"CSV 中找不到必要字段：{column}")

        return df

    def remove_html_tags(self, text):
        """
        去除 HTML 标签。
        """

        text = re.sub(r"<.*?>", "", text)

        return text

    def remove_url(self, text):
        """
        去除网址链接。
        """

        text = re.sub(r"http[s]?://\S+", "", text)
        text = re.sub(r"www\.\S+", "", text)

        return text

    def remove_extra_spaces(self, text):
        """
        去除多余空格、换行和制表符。
        """

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def remove_special_symbols(self, text):
        """
        去除部分无意义特殊符号。

        保留：
        1. 中文
        2. 英文
        3. 数字
        4. 常见中文标点
        5. 常见英文标点

        不完全删除标点，因为感叹号、省略号等可能表达情绪。
        """

        text = re.sub(
            r"[^\u4e00-\u9fa5a-zA-Z0-9，。！？、；：,.!?;:（）()《》“”\"'——\-… ]",
            "",
            text
        )

        return text

    def normalize_repeated_chars(self, text):
        """
        简单处理重复字符。

        例如：
        哈哈哈哈哈哈 -> 哈哈哈
        好好好好好 -> 好好好

        这样既能保留情绪强度，又不会让重复字符影响关键词统计。
        """

        text = re.sub(r"(.)\1{3,}", r"\1\1\1", text)

        return text

    def clean_text(self, text):
        """
        清洗单条评论文本。
        """

        if pd.isna(text):
            return ""

        text = str(text)

        text = self.remove_html_tags(text)
        text = self.remove_url(text)
        text = self.remove_special_symbols(text)
        text = self.normalize_repeated_chars(text)
        text = self.remove_extra_spaces(text)

        return text

    def add_text_length(self, df):
        """
        添加清洗后文本长度字段。
        """

        df["clean_text_length"] = df["clean_review_text"].apply(len)

        return df

    def filter_invalid_reviews(self, df):
        """
        过滤无效评论。

        包括：
        1. 空评论
        2. 清洗后过短评论
        3. 同一部电影、同一情绪类别下的重复评论
        """

        before_count = len(df)

        df = df[df["clean_review_text"].notna()]
        df = df[df["clean_review_text"] != ""]
        df = df[df["clean_text_length"] >= self.min_text_length]

        df = df.drop_duplicates(
            subset=[
                "movie_name",
                "comment_sentiment_type",
                "clean_review_text"
            ],
            keep="first"
        )

        after_count = len(df)

        print(f"过滤前评论数量：{before_count}")
        print(f"过滤后评论数量：{after_count}")
        print(f"删除评论数量：{before_count - after_count}")

        return df

    def add_sentiment_name(self, df):
        """
        添加中文情绪类别名称，方便后面看结果。
        """

        sentiment_name_map = {
            "positive": "好评",
            "neutral": "一般",
            "negative": "差评"
        }

        df["comment_sentiment_name"] = df["comment_sentiment_type"].map(
            sentiment_name_map
        )

        df["comment_sentiment_name"] = df["comment_sentiment_name"].fillna(
            df["comment_sentiment_type"]
        )

        return df

    def clean_dataframe(self, df):
        """
        清洗整个 DataFrame。
        """

        df = df.copy()

        df["clean_review_text"] = df["review_text"].apply(self.clean_text)

        df = self.add_text_length(df)
        df = self.add_sentiment_name(df)
        df = self.filter_invalid_reviews(df)

        return df

    def show_summary(self, df):
        """
        打印清洗结果概览。
        """

        print("\n清洗后评论类别分布：")
        print(df["comment_sentiment_type"].value_counts())

        print("\n每部电影每类评论数量：")
        summary = df.groupby(
            ["movie_name", "comment_sentiment_type"]
        ).size().reset_index(name="review_count")

        print(summary)

    def show_preview(self, df, n=10):
        """
        打印清洗效果预览。
        """

        preview_columns = [
            "movie_name",
            "comment_sentiment_type",
            "comment_sentiment_name",
            "review_star",
            "review_text",
            "clean_review_text",
            "clean_text_length",
            "review_like_count"
        ]

        existing_columns = []

        for column in preview_columns:
            if column in df.columns:
                existing_columns.append(column)

        print("\n清洗结果预览：")
        print(df[existing_columns].head(n))

    def save_to_csv(self, df):
        """
        保存清洗后的评论数据。
        """

        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(
            self.output_path,
            index=False,
            encoding="utf-8-sig"
        )

        print(f"清洗后评论数据已保存：{self.output_path}")

    def run(self):
        """
        评论清洗总入口。
        """

        df = self.load_data()
        cleaned_df = self.clean_dataframe(df)

        self.show_summary(cleaned_df)
        self.show_preview(cleaned_df)
        self.save_to_csv(cleaned_df)

        print("豆瓣短评文本清洗完成")

        return cleaned_df