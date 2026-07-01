from flask import Flask, request, jsonify
from flask_cors import CORS

from services.chart_service import DoubanChartService


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

douban_chart_service = DoubanChartService()


@app.route("/")
def home():
    return jsonify({
        "message": "Flask 后端服务已启动",
        "project": "Douban movie visualization review dashboard backup"
    })


@app.route("/api/charts/douban-rating", methods=["GET"])
def douban_rating_chart():
    data = douban_chart_service.get_rating_distribution()

    return jsonify({
        "chart_name": "douban_rating_distribution",
        "data": data
    })


@app.route("/api/charts/douban-genres", methods=["GET"])
def douban_genre_chart():
    top_n = request.args.get("top_n", 10, type=int)
    data = douban_chart_service.get_genre_distribution(top_n=top_n)

    return jsonify({
        "chart_name": "douban_genre_distribution",
        "params": {"top_n": top_n},
        "data": data
    })


@app.route("/api/charts/douban-country", methods=["GET"])
def douban_country_chart():
    top_n = request.args.get("top_n", 10, type=int)
    data = douban_chart_service.get_country_distribution(top_n=top_n)

    return jsonify({
        "chart_name": "douban_country_distribution",
        "params": {"top_n": top_n},
        "data": data
    })


@app.route("/api/charts/douban-year-trend", methods=["GET"])
def douban_year_trend_chart():
    data = douban_chart_service.get_year_trend()

    return jsonify({
        "chart_name": "douban_year_trend",
        "data": data
    })


@app.route("/api/charts/douban-rating-count-top", methods=["GET"])
def douban_rating_count_top_chart():
    top_n = request.args.get("top_n", 10, type=int)
    data = douban_chart_service.get_rating_count_top(top_n=top_n)

    return jsonify({
        "chart_name": "douban_rating_count_top",
        "params": {"top_n": top_n},
        "data": data
    })


@app.route("/api/charts/douban-keywords", methods=["GET"])
def douban_keywords_chart():
    top_n = request.args.get("top_n", 30, type=int)
    data = douban_chart_service.get_keywords(top_n=top_n)

    return jsonify({
        "chart_name": "douban_keywords",
        "params": {"top_n": top_n},
        "data": data
    })


@app.route("/api/charts/douban-review-keywords", methods=["GET"])
def douban_review_keywords_chart():
    top_n = request.args.get("top_n", 30, type=int)
    sentiment_type = request.args.get("sentiment_type")
    data = douban_chart_service.get_review_keywords(
        top_n=top_n,
        sentiment_type=sentiment_type
    )

    return jsonify({
        "chart_name": "douban_review_keywords",
        "params": {
            "top_n": top_n,
            "sentiment_type": sentiment_type
        },
        "data": data
    })


@app.route("/api/charts/douban-review-wordcloud", methods=["GET"])
def douban_review_wordcloud_chart():
    top_n = request.args.get("top_n", 80, type=int)
    sentiment_type = request.args.get("sentiment_type")
    data = douban_chart_service.get_review_wordcloud(
        top_n=top_n,
        sentiment_type=sentiment_type
    )

    return jsonify({
        "chart_name": "douban_review_wordcloud",
        "params": {
            "top_n": top_n,
            "sentiment_type": sentiment_type
        },
        "data": data
    })


@app.route("/api/charts/douban-year-genre-share", methods=["GET"])
def douban_year_genre_share_chart():
    top_n = request.args.get("top_n", 6, type=int)
    data = douban_chart_service.get_year_genre_share(top_n=top_n)

    return jsonify({
        "chart_name": "douban_year_genre_share",
        "params": {"top_n": top_n},
        "data": data
    })


@app.route("/api/charts/douban-dashboard", methods=["GET"])
def douban_dashboard_chart():
    top_n = request.args.get("top_n", 10, type=int)
    keyword_top_n = request.args.get("keyword_top_n", 30, type=int)

    data = douban_chart_service.get_dashboard_data(
        top_n=top_n,
        keyword_top_n=keyword_top_n
    )

    return jsonify({
        "chart_name": "douban_dashboard",
        "params": {
            "top_n": top_n,
            "keyword_top_n": keyword_top_n
        },
        "data": data
    })


if __name__ == "__main__":
    app.run(debug=True, port=5010)
