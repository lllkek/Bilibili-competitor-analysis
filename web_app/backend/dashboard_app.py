from pathlib import Path
import subprocess
import sys
import time
import urllib.request
import webbrowser


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "web_app" / "backend"
FRONTEND_DIR = PROJECT_ROOT / "web_app" / "frontend"

# 确保 Python 可以找到 backend/services 和项目根目录
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(BACKEND_DIR))

from services.chart_service import DoubanChartService


class DoubanDashboardApp:
    """
    豆瓣电影可视化网站启动类。

    这个类负责：
    1. 检查 MySQL 中的豆瓣电影数据是否可用
    2. 启动 Flask 后端服务
    3. 启动 React 前端服务
    4. 打开 Dashboard 网页地址

    注意：
    具体的数据查询和图表数据整理仍然由 DoubanChartService 负责。
    DoubanDashboardApp 只负责“运行网站”。
    """

    def __init__(
        self,
        top_n=10,
        keyword_top_n=30,
        backend_url="http://127.0.0.1:5000",
        frontend_url="http://localhost:5173"
    ):
        self.top_n = top_n
        self.keyword_top_n = keyword_top_n
        self.backend_url = backend_url
        self.frontend_url = frontend_url

        self.chart_service = DoubanChartService()

        self.backend_process = None
        self.frontend_process = None

    def _is_url_available(self, url):
        """
        检查某个网址是否已经可以访问。
        """
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                return response.status == 200
        except Exception:
            return False

    def _wait_for_url(self, url, service_name, timeout=30):
        """
        等待某个服务启动完成。
        """
        print(f"正在等待 {service_name} 启动：{url}")

        start_time = time.time()

        while time.time() - start_time < timeout:
            if self._is_url_available(url):
                print(f"{service_name} 已启动：{url}")
                return True

            time.sleep(1)

        raise RuntimeError(f"{service_name} 启动超时，请检查 terminal 报错。")

    def check_data(self):
        """
        检查数据库和 Dashboard 数据是否可用。

        这一步会调用 DoubanChartService，
        确认 MySQL 可以连接，douban_movie_top100 表可以查询。
        """
        print("正在检查豆瓣电影数据...")

        dashboard_data = self.chart_service.get_dashboard_data(
            top_n=self.top_n,
            keyword_top_n=self.keyword_top_n
        )

        print("数据检查完成，Dashboard 包含以下数据模块：")
        for key in dashboard_data.keys():
            print(f"- {key}")

        return dashboard_data

    def start_backend(self):
        """
        启动 Flask 后端服务。
        如果后端已经在运行，则不会重复启动。
        """
        if self._is_url_available(self.backend_url):
            print(f"Flask 后端已经在运行：{self.backend_url}")
            return

        print("正在启动 Flask 后端...")

        self.backend_process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=BACKEND_DIR
        )

        self._wait_for_url(
            url=self.backend_url,
            service_name="Flask 后端"
        )

    def start_frontend(self):
        """
        启动 React 前端服务。
        如果前端已经在运行，则不会重复启动。
        """
        if self._is_url_available(self.frontend_url):
            print(f"React 前端已经在运行：{self.frontend_url}")
            return

        print("正在启动 React 前端...")

        self.frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=FRONTEND_DIR
        )

        self._wait_for_url(
            url=self.frontend_url,
            service_name="React 前端"
        )

    def open_dashboard(self):
        """
        打开豆瓣电影可视化网页。
        """
        print(f"正在打开 Dashboard：{self.frontend_url}")
        webbrowser.open(self.frontend_url)

    def stop(self):
        """
        停止由本类启动的后端和前端进程。
        如果后端或前端原本已经在其他 terminal 运行，则不会关闭那些已有进程。
        """
        if self.frontend_process:
            print("正在停止 React 前端...")
            self.frontend_process.terminate()

        if self.backend_process:
            print("正在停止 Flask 后端...")
            self.backend_process.terminate()

    def run(self):
        """
        一键运行完整 Dashboard。

        执行顺序：
        1. 检查数据
        2. 启动 Flask 后端
        3. 启动 React 前端
        4. 打开网页
        5. 保持服务运行，直到用户按 Ctrl + C
        """
        try:
            self.check_data()
            self.start_backend()
            self.start_frontend()
            self.open_dashboard()

            print("\n豆瓣电影可视化 Dashboard 已启动。")
            print(f"后端地址：{self.backend_url}")
            print(f"前端地址：{self.frontend_url}")
            print("按 Ctrl + C 可以停止由本脚本启动的服务。")

            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n收到停止指令。")
            self.stop()

        except Exception as error:
            print("Dashboard 启动失败：")
            print(error)
            self.stop()
            raise