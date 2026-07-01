import { useEffect, useState } from "react";
import ReactECharts from "echarts-for-react";
import { Alert, Card, Col, Row, Select, Spin, Tabs, Typography } from "antd";

import {
  fetchDoubanRatingDistribution,
  fetchDoubanGenreDistribution,
  fetchDoubanCountryDistribution,
  fetchDoubanYearTrend,
  fetchDoubanRatingCountTop,
  fetchDoubanKeywords,
  fetchDoubanReviewKeywords,
  fetchDoubanReviewWordCloud,
  fetchDoubanYearGenreShare,
} from "../api/chartApi";

const { Title, Paragraph } = Typography;

function DoubanDashboard() {
  const [topN, setTopN] = useState(10);

  const [ratingData, setRatingData] = useState([]);
  const [genreData, setGenreData] = useState([]);
  const [countryData, setCountryData] = useState([]);
  const [yearTrendData, setYearTrendData] = useState([]);
  const [ratingCountData, setRatingCountData] = useState([]);
  const [keywordData, setKeywordData] = useState([]);
  const [reviewKeywordData, setReviewKeywordData] = useState([]);
  const [reviewWordCloudData, setReviewWordCloudData] = useState([]);
  const [yearGenreShareData, setYearGenreShareData] = useState([]);
  const [reviewSentiment, setReviewSentiment] = useState("");

  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    async function loadAllData() {
      try {
        setLoading(true);

        const [
          ratingResult,
          genreResult,
          countryResult,
          yearTrendResult,
          ratingCountResult,
          keywordResult,
          reviewKeywordResult,
          reviewWordCloudResult,
          yearGenreShareResult,
        ] = await Promise.all([
          fetchDoubanRatingDistribution(),
          fetchDoubanGenreDistribution(topN),
          fetchDoubanCountryDistribution(topN),
          fetchDoubanYearTrend(),
          fetchDoubanRatingCountTop(topN),
          fetchDoubanKeywords(30),
          fetchDoubanReviewKeywords(30, reviewSentiment),
          fetchDoubanReviewWordCloud(80, reviewSentiment),
          fetchDoubanYearGenreShare(6),
        ]);

        setRatingData(ratingResult.data);
        setGenreData(genreResult.data);
        setCountryData(countryResult.data);
        setYearTrendData(yearTrendResult.data);
        setRatingCountData(ratingCountResult.data);
        setKeywordData(keywordResult.data);
        setReviewKeywordData(reviewKeywordResult.data);
        setReviewWordCloudData(reviewWordCloudResult.data);
        setYearGenreShareData(yearGenreShareResult.data);
      } catch (error) {
        setErrorMessage("豆瓣电影可视化数据加载失败，请检查 Flask 后端和 MySQL 是否正常运行。");
        console.error(error);
      } finally {
        setLoading(false);
      }
    }

    loadAllData();
  }, [topN, reviewSentiment]);

  const ratingBarOption = {
    title: {
      text: "豆瓣电影评分分布",
      left: "center",
    },
    tooltip: {
      trigger: "axis",
    },
    xAxis: {
      type: "category",
      name: "评分",
      data: ratingData.map((item) => item.rating_score),
    },
    yAxis: {
      type: "value",
      name: "电影数量",
    },
    series: [
      {
        name: "电影数量",
        type: "bar",
        data: ratingData.map((item) => item.movie_count),
      },
    ],
  };

  const genrePieOption = {
    title: {
      text: "电影类型占比",
      left: "center",
    },
    tooltip: {
      trigger: "item",
      formatter: "{b}: {c} 部 ({d}%)",
    },
    legend: {
      orient: "vertical",
      left: "left",
    },
    series: [
      {
        name: "电影类型",
        type: "pie",
        radius: "60%",
        data: genreData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: "rgba(0, 0, 0, 0.3)",
          },
        },
      },
    ],
  };

  const countryPieOption = {
    title: {
      text: "国家 / 地区占比",
      left: "center",
    },
    tooltip: {
      trigger: "item",
      formatter: "{b}: {c} 部 ({d}%)",
    },
    legend: {
      orient: "vertical",
      left: "left",
    },
    series: [
      {
        name: "国家 / 地区",
        type: "pie",
        radius: ["35%", "65%"],
        data: countryData,
      },
    ],
  };

  const yearLineOption = {
    title: {
      text: "电影年份趋势",
      left: "center",
    },
    tooltip: {
      trigger: "axis",
    },
    legend: {
      top: 30,
      data: ["电影数量", "平均评分"],
    },
    dataZoom: [
      {
        type: "slider",
        start: 0,
        end: 100,
      },
    ],
    xAxis: {
      type: "category",
      name: "上映年份",
      data: yearTrendData.map((item) => item.release_year),
    },
    yAxis: [
      {
        type: "value",
        name: "电影数量",
      },
      {
        type: "value",
        name: "平均评分",
        min: 0,
        max: 10,
      },
    ],
    series: [
      {
        name: "电影数量",
        type: "line",
        smooth: true,
        data: yearTrendData.map((item) => item.movie_count),
      },
      {
        name: "平均评分",
        type: "line",
        smooth: true,
        yAxisIndex: 1,
        data: yearTrendData.map((item) => item.avg_rating),
      },
    ],
  };

  const ratingCountBarOption = {
    title: {
      text: `评分人数 Top${topN}`,
      left: "center",
    },
    tooltip: {
      trigger: "axis",
    },
    grid: {
      left: 120,
      right: 40,
      bottom: 40,
      top: 70,
    },
    xAxis: {
      type: "value",
      name: "评分人数",
    },
    yAxis: {
      type: "category",
      inverse: true,
      data: ratingCountData.map((item) => item.movie_name),
    },
    series: [
      {
        name: "评分人数",
        type: "bar",
        data: ratingCountData.map((item) => item.rating_count),
      },
    ],
  };

  const keywordBarOption = {
    title: {
      text: "豆瓣电影关键词 Top30",
      left: "center",
    },
    tooltip: {
      trigger: "axis",
    },
    grid: {
      left: 100,
      right: 40,
      bottom: 40,
      top: 70,
    },
    xAxis: {
      type: "value",
      name: "出现次数",
    },
    yAxis: {
      type: "category",
      inverse: true,
      data: keywordData.map((item) => item.name),
    },
    series: [
      {
        name: "出现次数",
        type: "bar",
        data: keywordData.map((item) => item.value),
      },
    ],
  };

  const reviewKeywordHotOption = {
    title: {
      text: "评论关键词热度 Top30",
      left: "center",
    },
    tooltip: {
      trigger: "axis",
      formatter(params) {
        const item = params[0]?.data || {};
        return `${item.name}<br/>热度：${item.weighted_score}<br/>出现次数：${item.keyword_count}<br/>平均点赞：${item.avg_like_count}`;
      },
    },
    grid: {
      left: 100,
      right: 40,
      bottom: 40,
      top: 70,
    },
    xAxis: {
      type: "value",
      name: "加权热度",
    },
    yAxis: {
      type: "category",
      inverse: true,
      data: reviewKeywordData.map((item) => item.name),
    },
    series: [
      {
        name: "关键词热度",
        type: "bar",
        data: reviewKeywordData.map((item) => ({
          value: item.weighted_score,
          ...item,
        })),
      },
    ],
  };

  const yearGenreShareOption = {
    title: {
      text: "不同年份电影类型占比",
      left: "center",
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
      valueFormatter: (value) => `${Number(value || 0).toFixed(1)}%`,
    },
    legend: {
      top: 30,
    },
    dataZoom: [
      {
        type: "slider",
        start: 0,
        end: 100,
      },
    ],
    grid: {
      left: 60,
      right: 40,
      top: 80,
      bottom: 70,
    },
    xAxis: {
      type: "category",
      name: "上映年份",
      data: [...new Set(yearGenreShareData.map((item) => item.release_year))],
    },
    yAxis: {
      type: "value",
      name: "类型占比",
      max: 100,
      axisLabel: {
        formatter: "{value}%",
      },
    },
    series: [...new Set(yearGenreShareData.map((item) => item.genre))].map((genre) => ({
      name: genre,
      type: "bar",
      stack: "genreShare",
      emphasis: {
        focus: "series",
      },
      data: [...new Set(yearGenreShareData.map((item) => item.release_year))].map((year) => {
        const found = yearGenreShareData.find(
          (item) => item.release_year === year && item.genre === genre
        );

        return found ? Number((found.share * 100).toFixed(2)) : 0;
      }),
    })),
  };

  function renderKeywordCloud() {
    if (!reviewWordCloudData.length) {
      return <div className="empty-cloud">暂无关键词云数据</div>;
    }

    const values = reviewWordCloudData.map((item) => Number(item.value || 0));
    const max = Math.max(...values, 1);
    const min = Math.min(...values, 0);

    return (
      <div className="keyword-cloud">
        {reviewWordCloudData.map((item, index) => {
          const weight = (Number(item.value || 0) - min) / Math.max(max - min, 1);
          const size = 14 + weight * 24;

          return (
            <span
              key={`${item.name}-${index}`}
              className="cloud-word"
              style={{
                fontSize: `${size}px`,
                opacity: 0.58 + weight * 0.42,
              }}
              title={`热度：${item.value}，出现次数：${item.keyword_count}`}
            >
              {item.name}
            </span>
          );
        })}
      </div>
    );
  }

  if (loading) {
    return (
      <Card>
        <Spin tip="正在加载豆瓣电影数据..." />
      </Card>
    );
  }

  if (errorMessage) {
    return <Alert message={errorMessage} type="error" showIcon />;
  }

  const tabItems = [
    {
      key: "overview",
      label: "综合概览",
      children: (
        <Row gutter={[24, 24]}>
          <Col xs={24} lg={12}>
            <Card title="评分分布">
              <ReactECharts option={ratingBarOption} style={{ height: 420 }} />
            </Card>
          </Col>

          <Col xs={24} lg={12}>
            <Card title="类型占比">
              <ReactECharts option={genrePieOption} style={{ height: 420 }} />
            </Card>
          </Col>

          <Col xs={24} lg={12}>
            <Card title="国家 / 地区占比">
              <ReactECharts option={countryPieOption} style={{ height: 420 }} />
            </Card>
          </Col>

          <Col xs={24} lg={12}>
            <Card title="评分人数 TopN">
              <ReactECharts option={ratingCountBarOption} style={{ height: 420 }} />
            </Card>
          </Col>
        </Row>
      ),
    },
    {
      key: "trend",
      label: "年份趋势",
      children: (
        <Card title="上映年份与评分趋势">
          <ReactECharts option={yearLineOption} style={{ height: 500 }} />
        </Card>
      ),
    },
    {
      key: "ranking",
      label: "热度排行",
      children: (
        <Card title="评分人数 TopN">
          <ReactECharts option={ratingCountBarOption} style={{ height: 520 }} />
        </Card>
      ),
    },
    {
      key: "keywords",
      label: "关键词分析",
      children: (
        <Card title="类型 / 导演 / 演员高频关键词">
          <ReactECharts option={keywordBarOption} style={{ height: 620 }} />
        </Card>
      ),
    },
    {
      key: "reviews",
      label: "评论分析",
      children: (
        <Row gutter={[24, 24]}>
          <Col xs={24}>
            <Card
              title="评论关键词分析"
              extra={
                <Select
                  value={reviewSentiment}
                  style={{ width: 140 }}
                  onChange={(value) => setReviewSentiment(value)}
                  options={[
                    { value: "", label: "全部评论" },
                    { value: "positive", label: "好评" },
                    { value: "neutral", label: "中评" },
                    { value: "negative", label: "差评" },
                  ]}
                />
              }
            >
              <Row gutter={[24, 24]}>
                <Col xs={24} lg={12}>
                  <ReactECharts option={reviewKeywordHotOption} style={{ height: 520 }} />
                </Col>

                <Col xs={24} lg={12}>
                  <div className="cloud-panel">
                    <div className="cloud-title">评论关键词云</div>
                    {renderKeywordCloud()}
                  </div>
                </Col>
              </Row>
            </Card>
          </Col>

          <Col xs={24}>
            <Card title="随着年份变化的不同类型电影占比">
              <ReactECharts option={yearGenreShareOption} style={{ height: 560 }} />
            </Card>
          </Col>
        </Row>
      ),
    },
  ];

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <Title level={2}>豆瓣电影可视化分析 Dashboard</Title>
          <Paragraph>
            本页面基于豆瓣电影 Top100 数据，从评分、类型、地区、年份趋势、评分人数和关键词等维度进行可视化分析。
          </Paragraph>
        </div>

        <div className="topn-selector">
          <span>TopN：</span>
          <Select
            value={topN}
            style={{ width: 120 }}
            onChange={(value) => setTopN(value)}
            options={[
              { value: 5, label: "Top 5" },
              { value: 10, label: "Top 10" },
              { value: 15, label: "Top 15" },
              { value: 20, label: "Top 20" },
            ]}
          />
        </div>
      </div>

      <Tabs defaultActiveKey="overview" items={tabItems} />
    </div>
  );
}

export default DoubanDashboard;
