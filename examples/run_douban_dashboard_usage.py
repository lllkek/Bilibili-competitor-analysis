from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from web_app.backend.dashboard_app import DoubanDashboardApp


# 创建豆瓣电影可视化网站启动对象
dashboard = DoubanDashboardApp(
    top_n=10,
    keyword_top_n=30
)


# 方式 1：一键启动完整网站
# 会检查数据、启动 Flask 后端、启动 React 前端，并自动打开网页
dashboard.run()


# 方式 2：如果想一步一步运行，可以改用下面这种写法：
# dashboard.check_data()
# dashboard.start_backend()
# dashboard.start_frontend()
# dashboard.open_dashboard()