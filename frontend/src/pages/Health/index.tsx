/**
 * Health 健康页面（P4-3）
 *
 * 健康日志（/api/health/logs）+ 运动记录（/exercises）+ 统计（/stats）+ 评分（/score）
 * 后端：backend/app/modules/health（prefix /api/health）
 */

import { useEffect, useState } from "react";
import {
  Card, Form, Input, InputNumber, Select, DatePicker, Button, Table,
  Typography, Row, Col, message, Space, Progress, Descriptions,
} from "antd";
import { HeartOutlined, ThunderboltOutlined, DashboardOutlined } from "@ant-design/icons";
import apiClient from "@/api/client";
import dayjs from "dayjs";

const { Title, Text, Paragraph } = Typography;

interface HealthLog {
  id: number;
  date: string;
  weight_kg: number | null;
  sleep_hours: number | null;
  exercise_minutes: number | null;
  steps: number | null;
  water_ml: number | null;
  mood_score: number | null;
  notes: string | null;
  created_at: string;
}

interface Exercise {
  id: number;
  date: string;
  exercise_type: string;
  duration_minutes: number;
  intensity: string | null;
  calories_burned: number | null;
  notes: string | null;
  created_at: string;
}

interface Stats {
  days: number;
  avg_steps: number;
  avg_sleep_hours: number;
  avg_exercise_minutes: number;
  avg_weight: number | null;
  avg_water_ml: number;
  bmi: number | null;
}

interface ScoreComponent {
  value: number;
  rate: number;
  weight: number;
}

interface Score {
  score: number;
  level: string;
  components: Record<string, ScoreComponent>;
}

const componentLabel: Record<string, string> = {
  steps: "步数",
  sleep: "睡眠",
  exercise: "运动",
};

const intensityLabel: Record<string, string> = {
  light: "轻松",
  moderate: "中等",
  intense: "高强度",
};

export default function Health() {
  const [days, setDays] = useState(30);
  const [logs, setLogs] = useState<HealthLog[]>([]);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [score, setScore] = useState<Score | null>(null);
  const [loading, setLoading] = useState(false);
  const [logForm] = Form.useForm();
  const [exForm] = Form.useForm();

  const fetchAll = async (d: number) => {
    setLoading(true);
    try {
      const [lr, er, sr, cr] = await Promise.all([
        apiClient.get("/health/logs", { params: { days: d } }),
        apiClient.get("/health/exercises", { params: { days: d } }),
        apiClient.get("/health/stats", { params: { days: d } }),
        apiClient.get("/health/score"),
      ]);
      setLogs(lr.data.data || []);
      setExercises(er.data.data || []);
      setStats(sr.data.data || null);
      setScore(cr.data.data || null);
    } catch (err: any) {
      message.error(err?.userMessage || "加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll(days);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [days]);

  const submitLog = async (v: any) => {
    try {
      await apiClient.post("/health/logs", {
        date: dayjs(v.date).format("YYYY-MM-DD"),
        weight_kg: v.weight_kg ?? null,
        sleep_hours: v.sleep_hours ?? null,
        exercise_minutes: v.exercise_minutes ?? null,
        steps: v.steps ?? null,
        water_ml: v.water_ml ?? null,
        mood_score: v.mood_score ?? null,
        notes: v.notes || null,
      });
      message.success("健康日志已记录");
      logForm.resetFields();
      fetchAll(days);
    } catch (err: any) {
      message.error(err?.userMessage || "记录失败");
    }
  };

  const submitExercise = async (v: any) => {
    try {
      await apiClient.post("/health/exercises", {
        date: dayjs(v.date).format("YYYY-MM-DD"),
        exercise_type: v.exercise_type,
        duration_minutes: v.duration_minutes,
        intensity: v.intensity || null,
        calories_burned: v.calories_burned ?? null,
        notes: v.notes || null,
      });
      message.success("运动已记录");
      exForm.resetFields();
      fetchAll(days);
    } catch (err: any) {
      message.error(err?.userMessage || "记录失败");
    }
  };

  const logColumns = [
    { title: "日期", dataIndex: "date", key: "date", width: 105 },
    { title: "体重kg", dataIndex: "weight_kg", key: "w", width: 80, render: (v: number | null) => v ?? "—" },
    { title: "睡眠h", dataIndex: "sleep_hours", key: "s", width: 75, render: (v: number | null) => v ?? "—" },
    { title: "运动min", dataIndex: "exercise_minutes", key: "e", width: 85, render: (v: number | null) => v ?? "—" },
    { title: "步数", dataIndex: "steps", key: "st", width: 85, render: (v: number | null) => v ?? "—" },
    { title: "饮水ml", dataIndex: "water_ml", key: "wa", width: 85, render: (v: number | null) => v ?? "—" },
    { title: "心情", dataIndex: "mood_score", key: "m", width: 65, render: (v: number | null) => v ? `${v}/10` : "—" },
    { title: "备注", dataIndex: "notes", key: "n", ellipsis: true },
  ];

  const exColumns = [
    { title: "日期", dataIndex: "date", key: "date", width: 105 },
    { title: "项目", dataIndex: "exercise_type", key: "t", width: 110 },
    { title: "时长min", dataIndex: "duration_minutes", key: "d", width: 90 },
    {
      title: "强度", dataIndex: "intensity", key: "i", width: 85,
      render: (v: string | null) => (v ? intensityLabel[v] || v : "—"),
    },
    { title: "消耗kcal", dataIndex: "calories_burned", key: "c", width: 95, render: (v: number | null) => v ?? "—" },
  ];

  return (
    <div>
      <Title level={3}><HeartOutlined /> 健康管理</Title>
      <Space style={{ marginBottom: 16 }}>
        <Text>统计范围：</Text>
        <Select
          value={days}
          style={{ width: 130 }}
          onChange={(v) => setDays(v)}
          options={[
            { label: "近 7 天", value: 7 },
            { label: "近 30 天", value: 30 },
            { label: "近 90 天", value: 90 },
          ]}
        />
      </Space>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card loading={loading}>
            <Space align="center">
              <DashboardOutlined style={{ fontSize: 28, color: "#1677ff" }} />
              <div>
                <Text type="secondary">健康评分</Text>
                <Title level={3} style={{ margin: 0 }}>
                  {score ? `${score.score} 分 · ${score.level}` : "暂无数据"}
                </Title>
              </div>
            </Space>
            {score && <Progress percent={score.score} size="small" style={{ marginTop: 8 }} />}
          </Card>
        </Col>
        <Col span={16}>
          <Card loading={loading} title="阶段平均">
            {stats ? (
              <Descriptions column={3} size="small">
                <Descriptions.Item label="日均步数">{Math.round(stats.avg_steps)}</Descriptions.Item>
                <Descriptions.Item label="日均睡眠">{stats.avg_sleep_hours.toFixed(1)} h</Descriptions.Item>
                <Descriptions.Item label="日均运动">{stats.avg_exercise_minutes.toFixed(0)} min</Descriptions.Item>
                <Descriptions.Item label="平均体重">{stats.avg_weight != null ? `${stats.avg_weight.toFixed(1)} kg` : "—"}</Descriptions.Item>
                <Descriptions.Item label="日均饮水">{Math.round(stats.avg_water_ml)} ml</Descriptions.Item>
                <Descriptions.Item label="BMI">{stats.bmi != null ? stats.bmi.toFixed(1) : "—"}</Descriptions.Item>
              </Descriptions>
            ) : (
              <Paragraph type="secondary">暂无统计数据，先记一条健康日志吧。</Paragraph>
            )}
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={14}>
          <Card title="健康日志" loading={loading} style={{ marginBottom: 16 }}>
            <Form form={logForm} layout="inline" onFinish={submitLog} style={{ marginBottom: 16, rowGap: 8 }}>
              <Form.Item name="date" rules={[{ required: true, message: "选日期" }]}>
                <DatePicker placeholder="日期" />
              </Form.Item>
              <Form.Item name="weight_kg"><InputNumber placeholder="体重kg" min={20} max={300} step={0.1} style={{ width: 110 }} /></Form.Item>
              <Form.Item name="sleep_hours"><InputNumber placeholder="睡眠h" min={0} max={24} step={0.5} style={{ width: 100 }} /></Form.Item>
              <Form.Item name="steps"><InputNumber placeholder="步数" min={0} style={{ width: 110 }} /></Form.Item>
              <Form.Item name="water_ml"><InputNumber placeholder="饮水ml" min={0} style={{ width: 110 }} /></Form.Item>
              <Form.Item name="mood_score"><InputNumber placeholder="心情1-10" min={1} max={10} style={{ width: 120 }} /></Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit">记录</Button>
              </Form.Item>
            </Form>
            <Table dataSource={logs} columns={logColumns} rowKey="id" pagination={{ pageSize: 8 }} size="small" />
          </Card>
          <Card title={<><ThunderboltOutlined /> 运动记录</>} loading={loading}>
            <Form form={exForm} layout="inline" onFinish={submitExercise} style={{ marginBottom: 16, rowGap: 8 }}>
              <Form.Item name="date" rules={[{ required: true, message: "选日期" }]}>
                <DatePicker placeholder="日期" />
              </Form.Item>
              <Form.Item name="exercise_type" rules={[{ required: true, message: "填项目" }]}>
                <Input placeholder="项目，如：跑步" style={{ width: 130 }} />
              </Form.Item>
              <Form.Item name="duration_minutes" rules={[{ required: true, message: "填时长" }]}>
                <InputNumber placeholder="时长min" min={1} max={600} style={{ width: 110 }} />
              </Form.Item>
              <Form.Item name="intensity">
                <Select placeholder="强度" allowClear style={{ width: 100 }} options={[
                  { label: "轻松", value: "light" },
                  { label: "中等", value: "moderate" },
                  { label: "高强度", value: "intense" },
                ]} />
              </Form.Item>
              <Form.Item name="calories_burned"><InputNumber placeholder="消耗kcal" min={0} style={{ width: 120 }} /></Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit">记录</Button>
              </Form.Item>
            </Form>
            <Table dataSource={exercises} columns={exColumns} rowKey="id" pagination={{ pageSize: 8 }} size="small" />
          </Card>
        </Col>
        <Col span={10}>
          <Card title="评分构成" loading={loading}>
            {score && score.components ? (
              Object.entries(score.components).map(([k, c]) => (
                <div key={k} style={{ marginBottom: 12 }}>
                  <Space style={{ width: "100%", justifyContent: "space-between" }}>
                    <Text>{componentLabel[k] || k}</Text>
                    <Text type="secondary">
                      均值 {Number(c.value).toFixed(1)} · 权重 {Math.round(c.weight * 100)}%
                    </Text>
                  </Space>
                  <Progress percent={Math.max(0, Math.min(100, Math.round(c.rate * 100)))} size="small" />
                </div>
              ))
            ) : (
              <Paragraph type="secondary">记几条日志后，这里会显示评分构成。</Paragraph>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
}
