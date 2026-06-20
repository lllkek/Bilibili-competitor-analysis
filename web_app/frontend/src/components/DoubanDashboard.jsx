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
        ] = await Promise.all([
          fetchDoubanRatingDistribution(),
          fetchDoubanGenreDistribution(topN),
          fetchDoubanCountryDistribution(topN),
          fetchDoubanYearTrend(),
          fetchDoubanRatingCountTop(topN),
          fetchDoubanKeywords(30),
        ]);

        setRatingData(ratingResult.data);
        setGenreData(genreResult.data);
        setCountryData(countryResult.data);
        setYearTrendData(yearTrendResult.data);
        setRatingCountData(ratingCountResult.data);
        setKeywordData(keywordResult.data);
      } catch (error) {
        setErrorMessage("豆瓣电影可视化数据加载失败，请检查 Flask 后端和 MySQL 是否正常运行。");
        console.error(error);
      } finally {
        setLoading(false);
      }
    }

    loadAllData();
  }, [topN]);

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