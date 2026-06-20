from flask import Flask, request, jsonify
from flask_cors import CORS

from services.chart_service import (
    get_douban_rating_distribution,
    get_douban_genre_distribution,
    get_douban_country_distribution,
    get_douban_year_trend,
    get_douban_rating_count_top,
    get_douban_keywords,
    get_baidu_hot_top10
)


app = Flask(__name__)

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173"
            ]
        }
    }
)


@app.route("/")
def home():
    return jsonify({
        "message": "Flask 后端服务已启动",
        "project": "Douban movie visualization web app"
    })


@app.route("/api/charts/douban-rating", methods=["GET"])
def douban_rating_chart():
    data = get_douban_rating_distribution()

    return jsonify({
        "chart_name": "douban_rating_distribution",
        "data": data
    })


@app.route("/api/charts/douban-genres", methods=["GET"])
def douban_genre_chart():
    top_n = request.args.get("top_n", 10, type=int)

    data = get_douban_genre_distribution(top_n=top_n)

    return jsonify({
        "chart_name": "douban_genre_distribution",
        "data": data
    })


@app.route("/api/charts/douban-country", methods=["GET"])
def douban_country_chart():
    top_n = request.args.get("top_n", 10, type=int)

    data = get_douban_country_distribution(top_n=top_n)

    return jsonify({
        "chart_name": "douban_country_distribution",
        "data": data
    })


@app.route("/api/charts/douban-year-trend", methods=["GET"])
def douban_year_trend_chart():
    data = get_douban_year_trend()

    return jsonify({
        "chart_name": "douban_year_trend",
        "data": data
    })


@app.route("/api/charts/douban-rating-count-top", methods=["GET"])
def douban_rating_count_top_chart():
    top_n = request.args.get("top_n", 10, type=int)

    data = get_douban_rating_count_top(top_n=top_n)

    return jsonify({
        "chart_name": "douban_rating_count_top",
        "data": data
    })


@app.route("/api/charts/douban-keywords", methods=["GET"])
def douban_keywords_chart():
    top_n = request.args.get("top_n", 30, type=int)

    data = get_douban_keywords(top_n=top_n)

    return jsonify({
        "chart_name": "douban_keywords",
        "data": data
    })


@app.route("/api/charts/baidu-hot", methods=["GET"])
def baidu_hot_chart():
    data = get_baidu_hot_top10()

    return jsonify({
        "chart_name": "baidu_hot_top10",
        "data": data
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)