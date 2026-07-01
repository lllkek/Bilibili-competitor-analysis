const BASE_URL = "http://127.0.0.1:5010";

async function request(url) {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error("请求后端接口失败");
  }

  return await response.json();
}

export async function fetchDoubanRatingDistribution() {
  return await request(`${BASE_URL}/api/charts/douban-rating`);
}

export async function fetchDoubanGenreDistribution(topN = 10) {
  return await request(`${BASE_URL}/api/charts/douban-genres?top_n=${topN}`);
}

export async function fetchDoubanCountryDistribution(topN = 10) {
  return await request(`${BASE_URL}/api/charts/douban-country?top_n=${topN}`);
}

export async function fetchDoubanYearTrend() {
  return await request(`${BASE_URL}/api/charts/douban-year-trend`);
}

export async function fetchDoubanRatingCountTop(topN = 10) {
  return await request(`${BASE_URL}/api/charts/douban-rating-count-top?top_n=${topN}`);
}

export async function fetchDoubanKeywords(topN = 30) {
  return await request(`${BASE_URL}/api/charts/douban-keywords?top_n=${topN}`);
}

export async function fetchDoubanReviewKeywords(topN = 30, sentimentType = "") {
  const params = new URLSearchParams({
    top_n: String(topN),
  });

  if (sentimentType) {
    params.set("sentiment_type", sentimentType);
  }

  return await request(`${BASE_URL}/api/charts/douban-review-keywords?${params.toString()}`);
}

export async function fetchDoubanReviewWordCloud(topN = 80, sentimentType = "") {
  const params = new URLSearchParams({
    top_n: String(topN),
  });

  if (sentimentType) {
    params.set("sentiment_type", sentimentType);
  }

  return await request(`${BASE_URL}/api/charts/douban-review-wordcloud?${params.toString()}`);
}

export async function fetchDoubanYearGenreShare(topN = 6) {
  return await request(`${BASE_URL}/api/charts/douban-year-genre-share?top_n=${topN}`);
}
