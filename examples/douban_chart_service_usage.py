from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from web_app.backend.services.chart_service import DoubanChartService


# 创建豆瓣电影图表数据服务对象
service = DoubanChartService()


# 1. 获取评分分布数据
rating_data = service.get_rating_distribution()
print("评分分布数据预览：")
print(rating_data[:5])


# 2. 获取电影类型 Top10
genre_data = service.get_genre_distribution(top_n=10)
print("\n电影类型 Top10：")
print(genre_data)


# 3. 获取国家 / 地区 Top10
country_data = service.get_country_distribution(top_n=10)
print("\n国家 / 地区 Top10：")
print(country_data)


# 4. 获取年份趋势数据
year_trend_data = service.get_year_trend()
print("\n年份趋势数据预览：")
print(year_trend_data[:5])


# 5. 获取评分人数 Top10
rating_count_top = service.get_rating_count_top(top_n=10)
print("\n评分人数 Top10：")
print(rating_count_top)


# 6. 获取关键词 Top30
keyword_data = service.get_keywords(top_n=30)
print("\n关键词 Top30 预览：")
print(keyword_data[:10])


# 7. 一次性获取整个 Dashboard 需要的数据
dashboard_data = service.get_dashboard_data(
    top_n=10,
    keyword_top_n=30
)

print("\nDashboard 数据包含的模块：")
print(dashboard_data.keys())