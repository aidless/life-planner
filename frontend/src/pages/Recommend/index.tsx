/**
 * Recommend 智能推荐页面（P5）
 *
 * 打开即算：GET /api/recommend/today 现场计算；
 * 定时推送：cron 早晚各一次，high 级进通知箱。
 * LLM 只做文案润色（coach_note），数字全部来自规则引擎。
 */

import { useEffect, useState } from "react";
import {
  Card, Button, Table, Tag, Typography, Row, Col, message, Space, Badge,
} from "antd";
import { BulbOutlined, BellOutlined, HistoryOutlined } from "@ant-design/icons";
import { Link } from "react-router-dom";
import apiClient from "@/api/client";

const { Title, Text, Paragraph } = Typography;

interface RecItem {
  rule: string;
  module: string;
  priority: "high" | "medium" | "low";
  title: string;
  reason: string;
  action_link: string;
  computed_at: string;
}

interface Notif {
  id: number;
  date: string;
  priority: string;
  title: string;
  body: string | null;
  module: string;
  is_read: number;
}

interface HistRun {
  date: string;
  slot: string;
  items: RecItem[];
}

const priorityMeta: Record<string, { color: string; label: string }> = {
  high: { color: "red", label: "重要" },
  medium: { color: "orange", label: "建议" },
  low: { color: "green", label: "保持" },
};

export default function Recommend() {
  const [items, setItems] = useState<RecItem[]>([]);
  const [coachNote, setCoachNote] = useState<string | null>(null);
  const [coachMode, setCoachMode] = useState("rule");
  const [notifs, setNotifs] = useState<Notif[]>([]);
  const [history, setHistory] = useState<HistRun[]>([]);
  const [loading, setLoading] = useState(false);

  const unread = notifs.filter((n) => n.is_read === 0).length;

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [tr, nr, hr] = await Promise.all([
        apiClient.get("/recommend/today"),
        apiClient.get("/recommend/notifications"),
        apiClient.get("/recommend/history", { params: { days: 7 } }),
      ]);
      setItems(tr.data.data?.items || []);
      setCoachNote(tr.data.data?.coach_note || null);
      setCoachMode(tr.data.data?.coach_mode || "rule");
      setNotifs(nr.data.data || []);
      setHistory(hr.data.data || []);
    } catch (err: any) {
      message.error(err?.userMessage || "加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  const markRead = async (id: number) => {
    try {
      await apiClient.post(`/recommend/notifications/${id}/read`);
      setNotifs((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: 1 } : n)));
    } catch {
      message.error("标记失败");
    }
  };

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: "0 auto" }}>
      <Title level={3} style={{ margin: 0 }}>
        <BulbOutlined style={{ color: "#fa8c16", marginRight: 12 }} />
        智能推荐 · 今日决策
        {unread > 0 && <Badge count={unread} style={{ marginLeft: 12 }} />}
      </Title>
      <Text type="secondary">
        按你的最新数据即时计算 {coachMode === "llm" ? "· 教练点评由 AI 生成" : "· 当前为规则模式（未配 AI 密钥）"}
      </Text>
      <div style={{ marginBottom: 24 }} />

      {coachNote && (
        <Card title="🎙️ 教练一句话" style={{ marginBottom: 24 }}>
          <Paragraph style={{ fontSize: 16, margin: 0 }}>{coachNote}</Paragraph>
        </Card>
      )}

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={14}>
          <Card title={`📋 今日推荐（${items.length}）`} loading={loading}>
            {items.length === 0 ? (
              <Text type="secondary">暂无推荐</Text>
            ) : (
              <Space direction="vertical" style={{ width: "100%" }} size={12}>
                {items.map((it) => (
                  <Card type="inner" size="small" key={`${it.rule}-${it.title}`}>
                    <Space>
                      <Tag color={priorityMeta[it.priority].color}>
                        {priorityMeta[it.priority].label}
                      </Tag>
                      <Text strong>{it.title}</Text>
                    </Space>
                    <Paragraph type="secondary" style={{ margin: "8px 0" }}>
                      {it.reason}
                    </Paragraph>
                    <Link to={it.action_link}>
                      <Button size="small" type="link">去处理 →</Button>
                    </Link>
                  </Card>
                ))}
              </Space>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={10}>
          <Card
            title={
              <Space>
                <BellOutlined />
                <span>通知箱{unread > 0 ? `（${unread} 未读）` : ""}</span>
              </Space>
            }
            style={{ marginBottom: 16 }}
          >
            {notifs.length === 0 ? (
              <Text type="secondary">没有重要推送——说明一切正常</Text>
            ) : (
              <Table
                dataSource={notifs.slice(0, 10)}
                rowKey="id"
                pagination={false}
                size="small"
                columns={[
                  {
                    title: "事项", dataIndex: "title", key: "title",
                    render: (t: string, r: Notif) => (
                      <Text delete={r.is_read === 1} strong={r.is_read === 0}>{t}</Text>
                    ),
                  },
                  { title: "日期", dataIndex: "date", key: "date", width: 100 },
                  {
                    title: "", key: "op", width: 70,
                    render: (_: unknown, r: Notif) => r.is_read === 0 ? (
                      <Button size="small" type="link" onClick={() => markRead(r.id)}>
                        已读
                      </Button>
                    ) : null,
                  },
                ]}
              />
            )}
          </Card>

          <Card
            title={
              <Space>
                <HistoryOutlined />
                <span>近 7 天快照</span>
              </Space>
            }
          >
            {history.length === 0 ? (
              <Text type="secondary">暂无历史快照（定时任务运行后产生）</Text>
            ) : (
              <Table
                dataSource={history}
                rowKey={(r) => `${r.date}-${r.slot}`}
                pagination={false}
                size="small"
                columns={[
                  { title: "日期", dataIndex: "date", key: "date", width: 110 },
                  { title: "批次", dataIndex: "slot", key: "slot", width: 90 },
                  {
                    title: "推荐数", key: "count",
                    render: (_: unknown, r: HistRun) => r.items.length,
                    width: 80,
                  },
                ]}
              />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
}
