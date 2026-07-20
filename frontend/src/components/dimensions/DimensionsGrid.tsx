/**
 * DimensionsGrid — 12 维度网格布局
 *
 * 上半 6 核心 + 下半 6 辅助，每行 6 个。
 */

import { Col, Row, Typography } from "antd";
import {
  AUXILIARY_DIMENSIONS,
  CORE_DIMENSIONS,
  DIMENSIONS,
} from "@/config/dimensionConfig";
import DimensionCard from "./DimensionCard";

const { Title, Text } = Typography;

interface Props {
  /** 每个维度的健康度 0-100 */
  scores: Record<string, number>;
}

export default function DimensionsGrid({ scores }: Props) {
  const getScore = (key: string): number => {
    return scores[key] ?? 0;
  };

  return (
    <div>
      {/* 6 核心 */}
      <div style={{ marginBottom: 24 }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            marginBottom: 16,
          }}
        >
          <Title level={5} style={{ margin: 0 }}>
            ⭐ 6 核心维度
          </Title>
          <Text type="secondary" style={{ fontSize: 12 }}>
            （学业/职业、健康、财务、习惯、心理、家庭）
          </Text>
        </div>
        <Row gutter={[16, 16]}>
          {CORE_DIMENSIONS.map((dim) => (
            <Col xs={24} sm={12} md={8} lg={4} key={dim.key}>
              <DimensionCard meta={dim} score={getScore(dim.key)} />
            </Col>
          ))}
        </Row>
      </div>

      {/* 6 辅助 */}
      <div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            marginBottom: 16,
          }}
        >
          <Title level={5} style={{ margin: 0 }}>
            🌱 6 辅助维度
          </Title>
          <Text type="secondary" style={{ fontSize: 12 }}>
            （兴趣、社交、学习、旅行、亲密、意义）
          </Text>
        </div>
        <Row gutter={[16, 16]}>
          {AUXILIARY_DIMENSIONS.map((dim) => (
            <Col xs={24} sm={12} md={8} lg={4} key={dim.key}>
              <DimensionCard meta={dim} score={getScore(dim.key)} />
            </Col>
          ))}
        </Row>
      </div>
    </div>
  );
}