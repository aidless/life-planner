/**
 * Psychology 心理页面
 *
 * 心情 + 能量 + 压力 3 维度评分
 * 反思/感恩日记
 * 避免心理咨询/医疗建议
 */

import { useEffect, useState } from "react";
import {
  Card, Form, Input, Button, Table, Tag, Typography,
  Row, Col, Progress, Space, message, Rate, Modal, Alert,
} from "antd";
import { SmileOutlined, BulbOutlined, HeartOutlined } from "@ant-design/icons";
import apiClient from "@/api/client";
import LoadingState from "@/components/LoadingState";

const { Title, Text, Paragraph } = Typography;

interface Mood {
  id: number;
  date: string;
  mood_score: number;
  energy_score: number | null;
  stress_score: number | null;
  note: string | null;
  created_at: string;
}

interface Reflection {
  id: number;
  date: string;
  prompt: string | null;
  content: string;
  gratitude: string | null;
}

interface Stats {
  days: number;
  avg_mood: number;
  avg_energy: number;
  avg_stress: number;
  score: number;
}

export default function Psychology() {
  const [moods, setMoods] = useState<Mood[]>([]);
  const [reflections, setReflections] = useState<Reflection[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [moodForm] = Form.useForm();
  const [reflForm] = Form.useForm();
  const [reflModalOpen, setReflModalOpen] = useState(false);

  const today = new Date().toISOString().slice(0, 10);

  const fetchAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [mr, rr, sr] = await Promise.all([
        apiClient.get("/psychology/moods", { params: { days: 30 } }),
        apiClient.get("/psychology/reflections", { params: { limit: 20 } }),
        apiClient.get("/psychology/stats", { params: { days: 30 } }),
      ]);
      setMoods(mr.data.data || []);
      setReflections(rr.data.data || []);
      setStats(sr.data.data);
    } catch (err: any) {
      setError(err?.userMessage || err?.message || "加载失败，请稍后重试");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  const handleMoodSubmit = async (values: Record<string, unknown>) => {
    try {
      await apiClient.post("/psychology/moods", { date: today, ...values });
      message.success("心情已记录");
      moodForm.resetFields();
      fetchAll();
    } catch (err: any) {
      message.error(err?.userMessage || "记录失败");
    }
  };

  const handleReflSubmit = async (values: Record<string, unknown>) => {
    try {
      await apiClient.post("/psychology/reflections", { date: today, ...values });
      message.success("反思已保存");
      reflForm.resetFields();
      setReflModalOpen(false);
      fetchAll();
    } catch (err: any) {
      message.error(err?.userMessage || "保存失败");
    }
  };

  const scoreColor = (s: number) => s >= 80 ? "#52c41a" : s >= 60 ? "#1677ff" : s >= 40 ? "#faad14" : "#f5222d";

  // 首次加载用全屏 loading（避免空白闪烁）
  if (loading && !stats && !error) {
    return <LoadingState loading={true} loadingText="加载心理数据..." fullScreen />;
  }

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: "0 auto" }}>
      {error && (
        <Alert
          type="error"
          showIcon
          message="数据加载失败"
          description={error}
          action={<a onClick={() => fetchAll()}>重试</a>}
          style={{ marginBottom: 16 }}
          closable
        />
      )}

      <Row align="middle" justify="space-between" style={{ marginBottom: 24 }}>
        <Col>
          <Title level={3} style={{ margin: 0 }}>
            <SmileOutlined style={{ color: "#fa8c16", marginRight: 12 }} />
            心理 · Psychology
          </Title>
          <Text type="secondary">心情、能量、压力 — 心理健康与学业表现直接相关</Text>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Text type="secondary">心情健康度</Text>
            <div style={{ fontSize: 36, color: scoreColor(stats?.score || 0), fontWeight: 700 }}>
              {stats?.score || 0}
            </div>
            <Text type="secondary">{stats?.days || 0} 天记录 · {stats?.avg_mood?.toFixed(1) || "0"} 平均心情</Text>
          </Card>
        </Col>
        <Col xs={12} sm={4}>
          <Card>
            <Text type="secondary">能量</Text>
            <Progress percent={stats ? stats.avg_energy * 10 : 0} strokeColor="#fa8c16" format={(p) => `${p?.toFixed(0)}`} />
            <Text type="secondary" style={{ fontSize: 12 }}>{stats?.avg_energy?.toFixed(1) || "0"} / 10</Text>
          </Card>
        </Col>
        <Col xs={12} sm={4}>
          <Card>
            <Text type="secondary">压力</Text>
            <Progress percent={stats ? stats.avg_stress * 10 : 0} strokeColor="#f5222d" format={(p) => `${p?.toFixed(0)}`} />
            <Text type="secondary" style={{ fontSize: 12 }}>{stats?.avg_stress?.toFixed(1) || "0"} / 10</Text>
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Text type="secondary">💡 建议</Text>
            <Paragraph style={{ marginTop: 8, marginBottom: 0 }}>
              坚持每日记录情绪，可发现压力源与情绪规律。
            </Paragraph>
          </Card>
        </Col>
      </Row>

      <Card title="📝 今日心情记录" style={{ marginBottom: 24 }}>
        <Form form={moodForm} layout="inline" onFinish={handleMoodSubmit}>
          <Form.Item name="mood_score" label="心情" rules={[{ required: true }]}>
            <Rate count={10} />
          </Form.Item>
          <Form.Item name="energy_score" label="能量">
            <Rate count={10} />
          </Form.Item>
          <Form.Item name="stress_score" label="压力">
            <Rate count={10} />
          </Form.Item>
          <Form.Item name="note" label="备注">
            <Input style={{ width: 200 }} placeholder="为什么这个分数？" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">记录</Button>
          </Form.Item>
        </Form>
      </Card>

      <Card
        title={<Space><BulbOutlined /><span>每日反思</span></Space>}
        style={{ marginBottom: 24 }}
        extra={<Button type="primary" onClick={() => setReflModalOpen(true)}>新增反思</Button>}
      >
        {reflections.length === 0 ? (
          <Text type="secondary">还没有反思。从每天 3 件事感恩开始 ✨</Text>
        ) : (
          <Row gutter={[16, 16]}>
            {reflections.slice(0, 6).map((r) => (
              <Col xs={24} md={12} key={r.id}>
                <Card type="inner" size="small" title={`📅 ${r.date}`}>
                  <Paragraph style={{ marginBottom: 8 }}>{r.content}</Paragraph>
                  {r.gratitude && (
                    <div style={{ background: "#fff7e6", padding: 8, borderRadius: 4 }}>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        <HeartOutlined /> 感恩：{r.gratitude}
                      </Text>
                    </div>
                  )}
                </Card>
              </Col>
            ))}
          </Row>
        )}
      </Card>

      <Card title="📊 心情历史（最近 30 天）">
        <Table
          dataSource={moods}
          loading={loading}
          rowKey="id"
          pagination={{ pageSize: 10 }}
          columns={[
            { title: "日期", dataIndex: "date", key: "date" },
            {
              title: "心情", dataIndex: "mood_score", key: "mood_score",
              render: (s: number) => <Tag color={s >= 7 ? "green" : s >= 4 ? "orange" : "red"}>{s} / 10</Tag>,
            },
            {
              title: "能量", dataIndex: "energy_score", key: "energy_score",
              render: (s: number | null) => s != null ? `${s} / 10` : "—",
            },
            {
              title: "压力", dataIndex: "stress_score", key: "stress_score",
              render: (s: number | null) => s != null ? `${s} / 10` : "—",
            },
            { title: "备注", dataIndex: "note", key: "note" },
          ]}
        />
      </Card>

      <Modal
        title="每日反思"
        open={reflModalOpen}
        onCancel={() => setReflModalOpen(false)}
        footer={null}
      >
        <Form form={reflForm} layout="vertical" onFinish={handleReflSubmit}>
          <Form.Item name="prompt" label="今日问题（可选）">
            <Input placeholder="如：今天学到了什么？" />
          </Form.Item>
          <Form.Item name="content" label="思考" rules={[{ required: true, min: 5 }]}>
            <Input.TextArea rows={4} />
          </Form.Item>
          <Form.Item name="gratitude" label="感恩 3 件事（可选）">
            <Input.TextArea rows={3} placeholder="如：朋友的鼓励 / 完成的作业 / 阳光" />
          </Form.Item>
          <Button type="primary" htmlType="submit">保存</Button>
        </Form>
      </Modal>
    </div>
  );
}