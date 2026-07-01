from flask import Flask, jsonify, request
from flask_cors import CORS

from services.review_reason_service import ReviewReasonService


app = Flask(__name__)
CORS(app)

review_reason_service = ReviewReasonService()


@app.route("/")
def index():
    return jsonify({
        "message": "Douban Movie Review Reason Analysis API is running."
    })


@app.route("/api/review-reason/overview", methods=["GET"])
def get_review_reason_overview():
    data = review_reason_service.get_overview()

    return jsonify({
        "success": True,
        "data": data
    })


@app.route("/api/review-reason/movies", methods=["GET"])
def get_review_reason_movies():
    data = review_reason_service.get_movie_options()

    return jsonify({
        "success": True,
        "data": data
    })


@app.route("/api/review-reason/movie-sentiment-summary", methods=["GET"])
def get_movie_sentiment_summary():
    movie_name = request.args.get("movie_name")

    data = review_reason_service.get_movie_sentiment_summary(
        movie_name=movie_name
    )

    return jsonify({
        "success": True,
        "data": data
    })


@app.route("/api/review-reason/aspect-summary", methods=["GET"])
def get_aspect_summary():
    movie_name = request.args.get("movie_name")
    sentiment_type = request.args.get("sentiment_type")
    review_period = request.args.get("review_period")

    data = review_reason_service.get_aspect_summary(
        movie_name=movie_name,
        sentiment_type=sentiment_type,
        review_period=review_period
    )

    return jsonify({
        "success": True,
        "data": data
    })


@app.route("/api/review-reason/top-aspects", methods=["GET"])
def get_top_aspects_by_movie():
    movie_name = request.args.get("movie_name")
    sentiment_type = request.args.get("sentiment_type")
    top_n = request.args.get("top_n", default=8, type=int)

    if not movie_name:
        return jsonify({
            "success": False,
            "message": "movie_name is required.",
            "data": []
        }), 400

    data = review_reason_service.get_top_aspects_by_movie(
        movie_name=movie_name,
        sentiment_type=sentiment_type,
        top_n=top_n
    )

    return jsonify({
        "success": True,
        "data": data
    })


@app.route("/api/review-reason/reason-details", methods=["GET"])
def get_reason_detail_summary():
    movie_name = request.args.get("movie_name")
    sentiment_type = request.args.get("sentiment_type")
    aspect_name = request.args.get("aspect_name")
    top_n = request.args.get("top_n", default=20, type=int)

    data = review_reason_service.get_reason_detail_summary(
        movie_name=movie_name,
        sentiment_type=sentiment_type,
        aspect_name=aspect_name,
        top_n=top_n
    )

    return jsonify({
        "success": True,
        "data": data
    })


@app.route("/api/review-reason/time-aspect-summary", methods=["GET"])
def get_time_aspect_summary():
    sentiment_type = request.args.get("sentiment_type")
    aspect_name = request.args.get("aspect_name")

    data = review_reason_service.get_time_aspect_summary(
        sentiment_type=sentiment_type,
        aspect_name=aspect_name
    )

    return jsonify({
        "success": True,
        "data": data
    })


@app.route("/api/review-reason/review-examples", methods=["GET"])
def get_review_examples():
    movie_name = request.args.get("movie_name")
    sentiment_type = request.args.get("sentiment_type")
    aspect_name = request.args.get("aspect_name")
    top_n = request.args.get("top_n", default=10, type=int)

    data = review_reason_service.get_review_examples(
        movie_name=movie_name,
        sentiment_type=sentiment_type,
        aspect_name=aspect_name,
        top_n=top_n
    )

    return jsonify({
        "success": True,
        "data": data
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )