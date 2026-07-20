/**
 * FiveYearOverview — 5 年人生总览时间轴
 *
 * 横向 5 列：今年 / 明年 / 后年 / 3 年 / 5 年
 * 每列：年份 + 学业 + 健康 + 财务 + 一句亮点
 */

import { Card, Col, Row, Tag, Typography } from "antd";
import { FIVE_YEAR_MILESTONES } from "@/config/dimensionConfig";

const { Title, Text } = Typography;

export default function FiveYearOverview() {
  return (
    <Card
      title={
        <span>
          🎯 5 年人生总览{" "}
          <Text type="secondary" style={{ fontSize: 12, fontWeight: "normal" }}>
            （今年 → 5 年后）
          </Text>
        </span>
      }
      style={{ borderRadius: 12 }}
      styles={{ body: { padding: 20 } }}
    >
      <Row gutter={[12, 12]}>
        {FIVE_YEAR_MILESTONES.map((m, idx) => (
          <Col xs={24} sm={12} md={8} lg={24 / 5} key={m.year}>
            <div
              style={{
                background:
                  idx === 0
                    ? "linear-gradient(135deg, #fff7e6 0%, #ffe7ba 100%)"
                    : "#fafafa",
                borderRadius: 10,
                padding: 16,
                height: "100%",
                border: idx === 0 ? "2px solid #fa8c16" : "1px solid #f0f0f0",
                position: "relative",
              }}
            >
              {/* 年份 */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginBottom: 12,
                }}
              >
                <Title
                  level={4}
                  style={{ margin: 0, color: idx === 0 ? "#fa8c16" : "#333" }}
                >
                  {m.year}
                </Title>
                {idx === 0 && <Tag color="orange">今年</Tag>}
              </div>
              <Text type="secondary" style={{ fontSize: 11, display: "block" }}>
                {m.label}
              </Text>

              {/* 三维度 */}
              <div style={{ marginTop: 12, display: "grid", gap: 6 }}>
                <Row align="middle" gutter={8}>
                  <Col>
                    <span style={{ fontSize: 14 }}>📚</span>
                  </Col>
                  <Col flex="auto">
                    <Text style={{ fontSize: 12 }}>{m.career}</Text>
                  </Col>
                </Row>
                <Row align="middle" gutter={8}>
                  <Col>
                    <span style={{ fontSize: 14 }}>❤️</span>
                  </Col>
                  <Col flex="auto">
                    <Text style={{ fontSize: 12 }}>{m.health}</Text>
                  </Col>
                </Row>
                <Row align="middle" gutter={8}>
                  <Col>
                    <span style={{ fontSize: 14 }}>💰</span>
                  </Col>
                  <Col flex="auto">
                    <Text style={{ fontSize: 12 }}>{m.finance}</Text>
                  </Col>
                </Row>
              </div>

              {/* 亮点 */}
              <div
                style={{
                  marginTop: 12,
                  paddingTop: 12,
                  borderTop: "1px dashed #d9d9d9",
                  textAlign: "center",
                  fontSize: 14,
                  fontWeight: 500,
                }}
              >
                {m.highlight}
              </div>
            </div>
          </Col>
        ))}
      </Row>
    </Card>
  );
}