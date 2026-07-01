import math
import re
from pathlib import Path

import jieba
import jieba.analyse
import pandas as pd


class RuleBasedReasonAnalyzer:
    """
    豆瓣电影短评规则原因分析类。

    核心逻辑：
    1. 情绪类别来自豆瓣筛选：positive / neutral / negative
    2. 不再用 LLM，不再用 SnowNLP 判断情感
    3. 用规则词典识别评论中的原因大类和细分原因
    4. 用 jieba 提取关键词
    5. 用点赞数计算共鸣权重
    6. 输出可视化需要的多张汇总表
    """

    SENTIMENT_NAME_MAP = {
        "positive": "好评",
        "neutral": "一般",
        "negative": "差评"
    }

    ASPECT_REASON_DICT = {
    "整体观感": {
        "经典神作": [
            "经典", "神作", "封神", "伟大", "顶级", "满分", "五星", "必看",
            "影史", "佳作", "杰作", " masterpiece", "yyds", "YYDS"
        ],
        "好看推荐": [
            "好看", "推荐", "值得看", "值得一看", "值得", "喜欢", "爱了",
            "不错", "很棒", "太棒", "优秀", "惊喜", "赞", "牛", "牛逼"
        ],
        "一般还行": [
            "一般", "还行", "尚可", "凑合", "普通", "中规中矩", "及格",
            "没那么好", "还可以", "可以看", "说不上好"
        ],
        "失望难看": [
            "失望", "难看", "烂", "垃圾", "不好看", "浪费时间", "后悔",
            "离谱", "太差", "很差", "不行"
        ],
        "无感不喜欢": [
            "无感", "没感觉", "不喜欢", "欣赏不来", "不是我的菜",
            "不适合我", "get不到", "get 不到"
        ],
        "期待落差": [
            "期待太高", "期望太高", "不如预期", "没有想象", "落差",
            "名不副实", "虚高", "过誉", "吹过了"
        ]
    },
    "剧情内容": {
        "剧情完整": [
            "剧情完整", "故事完整", "结构完整", "完整", "扎实", "严谨",
            "圆满", "闭环", "自洽", "流畅"
        ],
        "剧情反转": [
            "反转", "转折", "意想不到", "出乎意料", "没想到", "惊喜",
            "悬念", "伏笔", "铺垫", "峰回路转"
        ],
        "结尾震撼": [
            "结尾", "结局", "最后", "收尾", "震撼", "泪目", "封神",
            "升华", "后劲", "余味"
        ],
        "剧情精彩": [
            "剧情", "故事", "情节", "精彩", "过瘾", "吸引", "引人入胜",
            "扣人心弦", "紧张", "刺激"
        ],
        "剧情老套": [
            "老套", "俗套", "套路", "模板", "公式化", "没新意",
            "老梗", "俗气"
        ],
        "剧情无聊": [
            "无聊", "平淡", "没意思", "乏味", "看困", "看不下去",
            "没劲", "没亮点"
        ],
        "逻辑问题": [
            "逻辑", "不合理", "硬伤", "漏洞", "牵强", "说不通",
            "bug", "BUG", "莫名其妙"
        ],
        "剧情理想化": [
            "理想化", "童话", "不真实", "太假", "脱离现实", "悬浮"
        ]
    },
    "人物表演": {
        "演技好": [
            "演技好", "演技炸裂", "演技", "表演好", "表演精彩", "自然",
            "细腻", "入戏", "感染力", "代入感"
        ],
        "角色鲜明": [
            "角色", "人物", "主角", "配角", "立体", "鲜明", "丰满",
            "塑造", "人设", "形象"
        ],
        "台词经典": [
            "台词", "对白", "金句", "经典台词", "旁白"
        ],
        "演员加分": [
            "演员", "主演", "男主", "女主", "配角", "阵容", "影帝", "影后"
        ],
        "表演尴尬": [
            "尴尬", "用力过猛", "做作", "浮夸", "僵硬", "出戏"
        ],
        "人物单薄": [
            "单薄", "脸谱化", "工具人", "人设崩", "不讨喜", "扁平"
        ]
    },
    "导演叙事": {
        "导演能力强": [
            "导演", "功力", "调度", "掌控", "大师", "成熟", "作者性"
        ],
        "叙事优秀": [
            "叙事", "讲故事", "铺垫", "结构", "多线", "节制", "层层推进"
        ],
        "镜头语言好": [
            "镜头", "长镜头", "构图", "调度", "摄影机", "视角", "运镜"
        ],
        "剪辑出色": [
            "剪辑", "转场", "节奏控制", "流畅"
        ],
        "表达晦涩": [
            "晦涩", "看不懂", "隐喻", "故弄玄虚", "装", "装逼",
            "云里雾里"
        ],
        "表达说教": [
            "说教", "灌输", "强行", "刻意", "端着", "用力"
        ]
    },
    "节奏体验": {
        "节奏紧凑": [
            "节奏紧凑", "紧凑", "不拖沓", "流畅", "一气呵成", "爽快"
        ],
        "节奏拖沓": [
            "拖沓", "冗长", "节奏慢", "太慢", "慢热", "拖拉", "磨叽"
        ],
        "时长过长": [
            "太长", "时长", "两个小时", "三个小时", "片长"
        ],
        "观看疲劳": [
            "看困", "疲劳", "困", "睡着", "看不下去", "坐不住"
        ],
        "节奏平淡": [
            "平淡", "寡淡", "没高潮", "没起伏", "平铺直叙", "平"
        ]
    },
    "画面声音": {
        "画面优秀": [
            "画面", "摄影", "构图", "色彩", "美术", "视觉", "场景",
            "质感", "审美"
        ],
        "配乐优秀": [
            "配乐", "音乐", "原声", "bgm", "BGM", "声音", "音效",
            "主题曲"
        ],
        "氛围感强": [
            "氛围", "沉浸", "压迫感", "仪式感", "电影感"
        ],
        "特效优秀": [
            "特效", "视效", "大场面", "震撼"
        ],
        "画面一般": [
            "廉价", "粗糙", "五毛", "质感差", "不好看"
        ]
    },
    "情绪共鸣": {
        "感动": [
            "感动", "泪目", "哭", "哭了", "催泪", "动容", "破防"
        ],
        "震撼": [
            "震撼", "冲击", "惊艳", "震惊", "久久不能平静", "后劲"
        ],
        "治愈": [
            "治愈", "温暖", "舒服", "美好", "温情"
        ],
        "压抑": [
            "压抑", "难受", "窒息", "沉重", "心疼", "绝望", "堵"
        ],
        "热血": [
            "热血", "燃", "激动", "振奋", "鼓舞"
        ],
        "缺少共鸣": [
            "没共鸣", "无感", "感受不到", "不感动", "没感觉"
        ]
    },
    "主题价值": {
        "自由希望": [
            "自由", "希望", "救赎", "信念", "坚持", "梦想", "信仰"
        ],
        "人性思考": [
            "人性", "善恶", "道德", "选择", "尊严", "灵魂", "欲望"
        ],
        "现实社会": [
            "现实", "社会", "阶级", "制度", "权力", "压迫", "讽刺"
        ],
        "时代命运": [
            "时代", "历史", "命运", "宿命", "变迁", "年代"
        ],
        "人生意义": [
            "人生", "意义", "成长", "活着", "生命", "价值", "死亡"
        ],
        "价值观争议": [
            "价值观", "不认同", "不适", "三观", "冒犯"
        ]
    },
    "争议感受": {
        "过誉": [
            "过誉", "吹过了", "神作", "虚高", "名不副实", "不至于",
            "被高估"
        ],
        "期待落差": [
            "失望", "期望太高", "没有想象", "不如预期", "落差"
        ],
        "难以理解": [
            "看不懂", "不理解", "没懂", "云里雾里", "莫名其妙"
        ],
        "审美不合": [
            "不喜欢", "不是我的菜", "欣赏不来", "无感", "get不到"
        ],
        "评价两极": [
            "争议", "两极", "褒贬不一", "有人喜欢有人不喜欢"
        ]
    },
    "情怀记忆": {
        "童年回忆": [
        "童年", "小时候", "儿时", "小时候看", "童年回忆", "童年阴影"
         ],
        "怀旧情怀": [
      "回忆", "记忆", "怀旧", "情怀", "青春", "当年", "以前",
        "那时候", "年代感"
         ],
    "多年重看": [
        "重看", "二刷", "三刷", "再看", "重温", "补完", "多年以后",
        "长大后", "现在再看"
         ],
    "个人经历共鸣": [
        "经历", "自己的", "我自己", "想起", "回想", "人生阶段"
         ]
},

     "类型题材": {
        "爱情题材": [
        "爱情", "恋爱", "爱人", "情侣", "初恋", "暗恋", "相爱",
        "分手", "婚姻", "浪漫"
         ],
        "动画题材": [
        "动画", "动漫", "宫崎骏", "吉卜力", "皮克斯", "迪士尼",
        "童话", "想象力"
         ],
        "喜剧效果": [
        "搞笑", "好笑", "幽默", "笑死", "笑点", "喜剧", "荒诞",
        "黑色幽默"
         ],
        "犯罪悬疑": [
        "犯罪", "悬疑", "推理", "凶手", "案件", "黑帮", "警察",
        "反派", "悬念"
         ],
        "科幻设定": [
        "科幻", "宇宙", "太空", "时间", "穿越", "未来", "维度",
        "机器人", "人工智能"
         ],
        "战争历史": [
        "战争", "历史", "纳粹", "犹太人", "二战", "集中营", "屠杀",
        "革命"
         ],
        "原著改编": [
        "原著", "改编", "小说", "漫画", "书", "原作", "还原"
         ]
},

"人物关系": {
    "爱情关系": [
        "男人", "女人", "爱情", "爱", "背叛", "陪伴", "相守",
        "关系", "感情"
    ],
    "家庭亲情": [
        "家庭", "父亲", "母亲", "爸爸", "妈妈", "孩子", "儿子",
        "女儿", "亲情", "家人"
    ],
    "友情关系": [
        "朋友", "友情", "兄弟", "伙伴", "陪伴", "信任"
    ],
    "人物命运": [
        "命运", "一生", "人生", "成功", "失败", "努力", "工作",
        "选择"
    ],
    "性别表达": [
        "男性", "女性", "男人", "女人", "女性主义", "性别"
    ]
},

"文化背景": {
    "中国语境": [
        "中国", "国产", "内地", "大陆", "香港", "台湾", "中文",
        "东方"
    ],
    "美国语境": [
        "美国", "好莱坞", "西方", "资本主义", "美国人"
    ],
    "日本语境": [
        "日本", "日式", "宫崎骏", "动漫", "日本人"
    ],
    "历史文化": [
        "文化", "民族", "宗教", "犹太人", "奥斯卡", "政治",
        "意识形态"
    ],
    "社会群体": [
        "人类", "社会", "群体", "底层", "普通人", "阶级"
    ]
},

"观看体验": {
    "影院体验": [
        "电影院", "影院", "大银幕", "IMAX", "现场", "观影体验"
    ],
    "推荐观看": [
        "推荐", "安利", "必看", "值得看", "值得一看"
    ],
    "补标记录": [
        "补标", "标记", "看过", "记录一下"
    ],
    "重复观看": [
        "二刷", "三刷", "多刷", "重看", "再看", "每次看"
    ],
    "观看门槛": [
        "门槛", "看不进去", "需要耐心", "需要理解", "适合"
    ]
}
}
    STOPWORDS = {
        "电影", "一个", "真的", "还是", "就是", "觉得", "没有", "不是", "但是",
        "非常", "可以", "因为", "所以", "这个", "那个", "什么", "已经", "一部",
        "这么", "那么", "有点", "特别", "其实", "可能", "比较", "虽然", "如果",
        "时候", "这种", "一种", "看到", "看完", "感觉", "豆瓣", "这部", "片子",
        "世界", "知道", "为什么", "这样", "怎么", "一样", "完全", "现在",
        "不要", "只有", "为了", "看过", "东西", "明白", "不会", "一直",
        "所有", "无法", "应该", "那些", "如此", "不如", "出来", "不过",
        "理解", "作品", "时间", "别人", "原来", "需要", "不了", "有些",
        "这是", "居然", "开始", "终于", "两个", "一切", "以为", "之后",
        "一次", "小时", "真正", "里面", "后来", "十年", "相信", "每个",
        "好像", "以后", "除了", "只能", "告诉", "那样", "才能", "唯一",
        "有人", "如何", "发现", "观众", "地方", "哪里", "也许", "总是",

        "the", "of", "you", "is", "it", "and", "to", "in", "not", "can",
        "hold", "good", "thing", "maybe", "best", "all", "hope"  
    }

    def __init__(
        self,
        input_path=None,
        output_detail_path=None,
        aspect_summary_path=None,
        reason_summary_path=None,
        keyword_summary_path=None,
        time_reason_summary_path=None,
        heatmap_path=None,
        top_keywords_count=8
    ):
        self.project_root = Path(__file__).resolve().parents[2]

        self.input_path = Path(input_path) if input_path else self.project_root / "results" / "douban_movie_reviews_cleaned.csv"

        self.output_detail_path = Path(output_detail_path) if output_detail_path else self.project_root / "results" / "douban_rule_reason_analysis.csv"
        self.aspect_summary_path = Path(aspect_summary_path) if aspect_summary_path else self.project_root / "results" / "douban_aspect_summary.csv"
        self.reason_summary_path = Path(reason_summary_path) if reason_summary_path else self.project_root / "results" / "douban_reason_summary.csv"
        self.keyword_summary_path = Path(keyword_summary_path) if keyword_summary_path else self.project_root / "results" / "douban_keyword_summary.csv"
        self.time_reason_summary_path = Path(time_reason_summary_path) if time_reason_summary_path else self.project_root / "results" / "douban_time_reason_summary.csv"
        self.heatmap_path = Path(heatmap_path) if heatmap_path else self.project_root / "results" / "douban_movie_aspect_heatmap.csv"

        self.top_keywords_count = top_keywords_count

    def load_data(self):
        if not self.input_path.exists():
            raise FileNotFoundError(f"找不到输入文件：{self.input_path}")

        df = pd.read_csv(self.input_path)

        print(f"读取清洗后评论数据：{len(df)} 条")
        print(f"字段：{df.columns.tolist()}")

        required_columns = [
            "movie_name",
            "comment_sentiment_type",
            "clean_review_text"
        ]

        for column in required_columns:
            if column not in df.columns:
                raise ValueError(f"缺少必要字段：{column}")

        return df

    def get_sentiment_name(self, sentiment_type):
        return self.SENTIMENT_NAME_MAP.get(sentiment_type, sentiment_type)

    def get_like_weight(self, like_count):
        if pd.isna(like_count):
            like_count = 0

        try:
            like_count = float(like_count)
        except Exception:
            like_count = 0

        if like_count < 0:
            like_count = 0

        return round(math.log(like_count + 1) + 1, 4)

    def extract_time_features(self, df):
        df = df.copy()

        if "review_time" not in df.columns:
            df["review_year"] = None
            df["review_month"] = None
            df["review_period"] = "未知时间"
            return df

        df["review_datetime"] = pd.to_datetime(df["review_time"], errors="coerce")
        df["review_year"] = df["review_datetime"].dt.year
        df["review_month"] = df["review_datetime"].dt.to_period("M").astype(str)
        df["review_period"] = df["review_year"].apply(self.convert_year_to_period)

        return df

    def convert_year_to_period(self, year):
        if pd.isna(year):
            return "未知时间"

        year = int(year)

        if year <= 2010:
            return "2010年及以前"

        if year <= 2015:
            return "2011-2015"

        if year <= 2020:
            return "2016-2020"

        return "2021年及以后"

    def match_reasons(self, text):
        if pd.isna(text):
            text = ""

        text = str(text)

        matched_rows = []

        for aspect_name, reason_dict in self.ASPECT_REASON_DICT.items():
            for reason_name, keywords in reason_dict.items():
                for keyword in keywords:
                    if keyword in text:
                        matched_rows.append({
                            "aspect_name": aspect_name,
                            "reason_name": reason_name,
                            "matched_keyword": keyword
                        })
                        break

        return matched_rows

    def get_main_reason(self, matched_rows):
        if not matched_rows:
            return {
                "main_aspect": "未识别",
                "main_reason": "未识别",
                "matched_reasons": "未识别",
                "matched_aspects": "未识别",
                "matched_keywords": ""
            }

        aspect_list = []
        reason_list = []
        keyword_list = []

        for item in matched_rows:
            aspect_list.append(item["aspect_name"])
            reason_list.append(item["reason_name"])
            keyword_list.append(item["matched_keyword"])

        main_item = matched_rows[0]

        return {
            "main_aspect": main_item["aspect_name"],
            "main_reason": main_item["reason_name"],
            "matched_reasons": "，".join(list(dict.fromkeys(reason_list))),
            "matched_aspects": "，".join(list(dict.fromkeys(aspect_list))),
            "matched_keywords": "，".join(list(dict.fromkeys(keyword_list)))
        }

    def extract_keywords(self, text):
        if pd.isna(text):
            return []

        text = str(text).strip()

        if not text:
            return []

        keywords = jieba.analyse.extract_tags(
            sentence=text,
            topK=self.top_keywords_count,
            withWeight=False
        )

        clean_keywords = []

        for keyword in keywords:
            keyword = str(keyword).strip()

            if not keyword:
                continue

            if keyword in self.STOPWORDS:
                continue

            if len(keyword) < 2:
                continue

            clean_keywords.append(keyword)

        return clean_keywords

    def analyze_dataframe(self, df):
        df = df.copy()

        df["comment_sentiment_name"] = df["comment_sentiment_type"].apply(
            self.get_sentiment_name
        )

        if "review_like_count" in df.columns:
            df["like_weight"] = df["review_like_count"].apply(self.get_like_weight)
        else:
            df["review_like_count"] = 0
            df["like_weight"] = 1

        df = self.extract_time_features(df)

        matched_info_list = []
        keyword_list = []

        print("正在进行规则原因识别和关键词提取...")

        for _, row in df.iterrows():
            text = row.get("clean_review_text", "")

            matched_rows = self.match_reasons(text)
            main_info = self.get_main_reason(matched_rows)
            matched_info_list.append(main_info)

            keywords = self.extract_keywords(text)
            keyword_list.append("，".join(keywords))

        matched_df = pd.DataFrame(matched_info_list)

        df = pd.concat(
            [
                df.reset_index(drop=True),
                matched_df.reset_index(drop=True)
            ],
            axis=1
        )

        df["top_keywords"] = keyword_list
        df["reason_count"] = df["matched_reasons"].apply(
            lambda x: 0 if x == "未识别" else len(str(x).split("，"))
        )

        return df

    def build_reason_long_table(self, df):
        rows = []

        for _, row in df.iterrows():
            matched_rows = self.match_reasons(row.get("clean_review_text", ""))

            for item in matched_rows:
                rows.append({
                    "movie_name": row.get("movie_name", ""),
                    "movie_url": row.get("movie_url", ""),
                    "comment_sentiment_type": row.get("comment_sentiment_type", ""),
                    "comment_sentiment_name": row.get("comment_sentiment_name", ""),
                    "review_star": row.get("review_star", None),
                    "review_time": row.get("review_time", ""),
                    "review_year": row.get("review_year", None),
                    "review_period": row.get("review_period", "未知时间"),
                    "review_like_count": row.get("review_like_count", 0),
                    "like_weight": row.get("like_weight", 1),
                    "clean_review_text": row.get("clean_review_text", ""),
                    "aspect_name": item["aspect_name"],
                    "reason_name": item["reason_name"],
                    "matched_keyword": item["matched_keyword"]
                })

        reason_long_df = pd.DataFrame(rows)

        print(f"原因长表记录数：{len(reason_long_df)}")

        return reason_long_df

    def build_keyword_long_table(self, df):
        rows = []

        for _, row in df.iterrows():
            keywords_text = row.get("top_keywords", "")

            if pd.isna(keywords_text) or not str(keywords_text).strip():
                continue

            keywords = str(keywords_text).split("，")

            for keyword in keywords:
                keyword = keyword.strip()

                if not keyword:
                    continue

                rows.append({
                    "movie_name": row.get("movie_name", ""),
                    "comment_sentiment_type": row.get("comment_sentiment_type", ""),
                    "comment_sentiment_name": row.get("comment_sentiment_name", ""),
                    "review_period": row.get("review_period", "未知时间"),
                    "keyword": keyword,
                    "review_like_count": row.get("review_like_count", 0),
                    "like_weight": row.get("like_weight", 1)
                })

        keyword_long_df = pd.DataFrame(rows)

        print(f"关键词长表记录数：{len(keyword_long_df)}")

        return keyword_long_df

    def build_aspect_summary(self, reason_long_df):
        if reason_long_df.empty:
            return pd.DataFrame()

        group_cols = [
            "movie_name",
            "comment_sentiment_type",
            "comment_sentiment_name",
            "aspect_name"
        ]

        summary_df = reason_long_df.groupby(group_cols).agg(
            review_count=("clean_review_text", "count"),
            total_like_count=("review_like_count", "sum"),
            weighted_score=("like_weight", "sum")
        ).reset_index()

        total_df = reason_long_df.groupby(
            ["movie_name", "comment_sentiment_type", "comment_sentiment_name"]
        ).agg(
            total_reason_mentions=("aspect_name", "count")
        ).reset_index()

        summary_df = summary_df.merge(
            total_df,
            on=["movie_name", "comment_sentiment_type", "comment_sentiment_name"],
            how="left"
        )

        summary_df["aspect_ratio"] = summary_df["review_count"] / summary_df["total_reason_mentions"]
        summary_df["aspect_ratio"] = summary_df["aspect_ratio"].round(4)
        summary_df["weighted_score"] = summary_df["weighted_score"].round(4)

        summary_df = summary_df.sort_values(
            by=["movie_name", "comment_sentiment_type", "weighted_score"],
            ascending=[True, True, False]
        )

        return summary_df

    def build_reason_summary(self, reason_long_df):
        if reason_long_df.empty:
            return pd.DataFrame()

        group_cols = [
            "movie_name",
            "comment_sentiment_type",
            "comment_sentiment_name",
            "aspect_name",
            "reason_name"
        ]

        summary_df = reason_long_df.groupby(group_cols).agg(
            review_count=("clean_review_text", "count"),
            total_like_count=("review_like_count", "sum"),
            weighted_score=("like_weight", "sum")
        ).reset_index()

        total_df = reason_long_df.groupby(
            ["movie_name", "comment_sentiment_type", "comment_sentiment_name", "aspect_name"]
        ).agg(
            total_reason_mentions=("reason_name", "count")
        ).reset_index()

        summary_df = summary_df.merge(
            total_df,
            on=["movie_name", "comment_sentiment_type", "comment_sentiment_name", "aspect_name"],
            how="left"
        )

        summary_df["reason_ratio"] = summary_df["review_count"] / summary_df["total_reason_mentions"]
        summary_df["reason_ratio"] = summary_df["reason_ratio"].round(4)
        summary_df["weighted_score"] = summary_df["weighted_score"].round(4)

        summary_df = summary_df.sort_values(
            by=["movie_name", "comment_sentiment_type", "aspect_name", "weighted_score"],
            ascending=[True, True, True, False]
        )

        return summary_df

    def build_keyword_summary(self, keyword_long_df):
        if keyword_long_df.empty:
            return pd.DataFrame()

        group_cols = [
            "movie_name",
            "comment_sentiment_type",
            "comment_sentiment_name",
            "keyword"
        ]

        summary_df = keyword_long_df.groupby(group_cols).agg(
            keyword_count=("keyword", "count"),
            total_like_count=("review_like_count", "sum"),
            weighted_score=("like_weight", "sum"),
            avg_like_count=("review_like_count", "mean")
        ).reset_index()

        summary_df["weighted_score"] = summary_df["weighted_score"].round(4)
        summary_df["avg_like_count"] = summary_df["avg_like_count"].round(2)

        summary_df = summary_df.sort_values(
            by=["movie_name", "comment_sentiment_type", "weighted_score"],
            ascending=[True, True, False]
        )

        return summary_df

    def build_time_reason_summary(self, reason_long_df):
        if reason_long_df.empty:
            return pd.DataFrame()

        group_cols = [
            "review_period",
            "comment_sentiment_type",
            "comment_sentiment_name",
            "aspect_name",
            "reason_name"
        ]

        summary_df = reason_long_df.groupby(group_cols).agg(
            review_count=("clean_review_text", "count"),
            total_like_count=("review_like_count", "sum"),
            weighted_score=("like_weight", "sum")
        ).reset_index()

        summary_df["weighted_score"] = summary_df["weighted_score"].round(4)

        period_order = {
            "2010年及以前": 1,
            "2011-2015": 2,
            "2016-2020": 3,
            "2021年及以后": 4,
            "未知时间": 5
        }

        summary_df["period_order"] = summary_df["review_period"].map(period_order).fillna(99)

        summary_df = summary_df.sort_values(
            by=["period_order", "comment_sentiment_type", "weighted_score"],
            ascending=[True, True, False]
        )

        return summary_df

    def build_heatmap_summary(self, aspect_summary_df):
        if aspect_summary_df.empty:
            return pd.DataFrame()

        heatmap_df = aspect_summary_df[
            [
                "movie_name",
                "comment_sentiment_type",
                "comment_sentiment_name",
                "aspect_name",
                "review_count",
                "weighted_score",
                "aspect_ratio"
            ]
        ].copy()

        return heatmap_df

    def save_outputs(
        self,
        detail_df,
        aspect_summary_df,
        reason_summary_df,
        keyword_summary_df,
        time_reason_summary_df,
        heatmap_df
    ):
        self.output_detail_path.parent.mkdir(parents=True, exist_ok=True)

        detail_df.to_csv(self.output_detail_path, index=False, encoding="utf-8-sig")
        aspect_summary_df.to_csv(self.aspect_summary_path, index=False, encoding="utf-8-sig")
        reason_summary_df.to_csv(self.reason_summary_path, index=False, encoding="utf-8-sig")
        keyword_summary_df.to_csv(self.keyword_summary_path, index=False, encoding="utf-8-sig")
        time_reason_summary_df.to_csv(self.time_reason_summary_path, index=False, encoding="utf-8-sig")
        heatmap_df.to_csv(self.heatmap_path, index=False, encoding="utf-8-sig")

        print("\n分析结果已保存：")
        print(f"1. {self.output_detail_path}")
        print(f"2. {self.aspect_summary_path}")
        print(f"3. {self.reason_summary_path}")
        print(f"4. {self.keyword_summary_path}")
        print(f"5. {self.time_reason_summary_path}")
        print(f"6. {self.heatmap_path}")

    def show_summary(
        self,
        detail_df,
        aspect_summary_df,
        reason_summary_df,
        keyword_summary_df
    ):
        print("\n===== 规则分析概览 =====")
        print("明细数据量：", len(detail_df))

        print("\n评论级别分布：")
        print(detail_df["comment_sentiment_type"].value_counts())

        print("\n主原因大类分布：")
        print(detail_df["main_aspect"].value_counts().head(20))

        print("\n原因大类汇总预览：")
        print(aspect_summary_df.head(20))

        print("\n细分原因汇总预览：")
        print(reason_summary_df.head(20))

        print("\n关键词汇总预览：")
        print(keyword_summary_df.head(20))

    def run(self):
        df = self.load_data()

        detail_df = self.analyze_dataframe(df)

        reason_long_df = self.build_reason_long_table(detail_df)
        keyword_long_df = self.build_keyword_long_table(detail_df)

        aspect_summary_df = self.build_aspect_summary(reason_long_df)
        reason_summary_df = self.build_reason_summary(reason_long_df)
        keyword_summary_df = self.build_keyword_summary(keyword_long_df)
        time_reason_summary_df = self.build_time_reason_summary(reason_long_df)
        heatmap_df = self.build_heatmap_summary(aspect_summary_df)

        self.show_summary(
            detail_df=detail_df,
            aspect_summary_df=aspect_summary_df,
            reason_summary_df=reason_summary_df,
            keyword_summary_df=keyword_summary_df
        )

        self.save_outputs(
            detail_df=detail_df,
            aspect_summary_df=aspect_summary_df,
            reason_summary_df=reason_summary_df,
            keyword_summary_df=keyword_summary_df,
            time_reason_summary_df=time_reason_summary_df,
            heatmap_df=heatmap_df
        )

        print("豆瓣短评规则原因分析完成")

        return {
            "detail_df": detail_df,
            "aspect_summary_df": aspect_summary_df,
            "reason_summary_df": reason_summary_df,
            "keyword_summary_df": keyword_summary_df,
            "time_reason_summary_df": time_reason_summary_df,
            "heatmap_df": heatmap_df
        }