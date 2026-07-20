/**
 * DimensionCard — 单个维度卡片
 *
 * 用于 12 维度网格。
 */

import { Card, Progress, Tag, Tooltip, Typography } from "antd";
import { useNavigate } from "react-router-dom";
import {
  ArrowRightOutlined,
  CheckCircleFilled,
  ClockCircleOutlined,
} from "@ant-design/icons";
import {
  type DimensionMeta,
  getHealthLevel,
} from "@/config/dimensionConfig";

const { Text } = Typography;

interface Props {
  meta: DimensionMeta;
  score: number; // 0-100
}

export default function DimensionCard({ meta, score }: Props) {
  const navigate = useNavigate();
  const level = getHealthLevel(score);
  const isComing = meta.status === "coming_soon";

  const handleClick = () => {
    if (meta.path) {
      navigate(meta.path);
    }
  };

  return (
    <Card
      hoverable={!isComing}
      onClick={isComing ? undefined : handleClick}
      style={{
        borderRadius: 12,
        height: "100%",
        background: meta.bgColor,
        cursor: isComing ? "default" : "pointer",
        opacity: isComing ? 0.85 : 1,
      }}
      styles={{
        body: {
          padding: 20,
          display: "flex",
          flexDirection: "column",
          gap: 12,
        },
      }}
    >
      {/* Header: icon + name + status */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
          }}
        >
          <div
            style={{
              fontSize: 24,
              color: meta.color,
              background: "#fff",
              width: 40,
              height: 40,
              borderRadius: 10,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {meta.icon}
          </div>
          <div>
            <Text strong style={{ fontSize: 16, display: "block" }}>
              {meta.name}
            </Text>
            <Text type="secondary" style={{ fontSize: 11 }}>
              {meta.englishName}
            </Text>
          </div>
        </div>
        {isComing ? (
          <Tag icon={<ClockCircleOutlined />} color="default">
            即将上线
          </Tag>
        ) : (
          <Tag color={meta.priority === "P0" ? "red" : "blue"}>
            {meta.priority}
          </Tag>
        )}
      </div>

      {/* Score progress */}
      <div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: 6,
          }}
        >
          <Text type="secondary" style={{ fontSize: 12 }}>
            健康度
          </Text>
          <Tooltip title={`等级：${level.label}`}>
            <Text
              strong
              style={{ color: level.color, fontSize: 12 }}
            >
              {score} · {level.label}
            </Text>
          </Tooltip>
        </div>
        <Progress
          percent={score}
          strokeColor={level.color}
          showInfo={false}
          size="small"
        />
      </div>

      {/* Description */}
      <Text
        type="secondary"
        style={{ fontSize: 12, lineHeight: 1.5, flex: 1 }}
      >
        {meta.description}
      </Text>

      {/* Footer */}
      {!isComing && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "flex-end",
            color: meta.color,
            fontSize: 12,
          }}
        >
          进入 <ArrowRightOutlined style={{ marginLeft: 4 }} />
        </div>
      )}
    </Card>
  );
}