/**
 * Interest 兴趣页面
 *
 * 爱好列表 + 活动记录 + 实际周时长 vs 目标
 */

import { useEffect, useState } from "react";
import {
  Card, Form, Input, Select, InputNumber, Button, Table, Tag, Typography,
  Row, Col, Progress, message, Space,
} from "antd";
import { StarOutlined } from "@ant-design/icons";
import apiClient from "@/api/client";

const { Title, Text } = Typography;

interface Interest {
  id: number;
  name: string;
  category: string | null;
  description: string | null;
  weekly_target_hours: number;
  actual_weekly_hours: number;
}

interface Activity {
  id: number;
  interest_id: number;
  date: string;
  duration_minutes: number;
  note: string | null;
}

export default function Interest() {
  const [interests, setInterests] = useState<Interest[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(false);
  const [interestForm] = Form.useForm();
  const [activityForm] = Form.useForm();

  const interestOptions = interests.map((i) => ({ label: i.name, value: i.id }));

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [ir, ar] = await Promise.all([
        apiClient.get("/interest"),
        apiClient.get("/interest/activities", { params: { days: 30 } }),
      ]);
      setInterests(ir.data.data || []);
      setActivities(ar.data.data || []);
    } catch (err: any) {
      message.error(err?.userMessage || "加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  const handleAddInterest = async (values: Record<string, unknown>) => {
    try {
      await apiClient.post("/interest", values);
      message.success("兴趣已添加");
      interestForm.resetFields();
      fetchAll();
    } catch (err: any) {
      message.error("添加失败");
    }
  };

  const handleAddActivity = async (values: Record<string, unknown>) => {
    try {
      const today = new Date().toISOString().slice(0, 10);
      await apiClient.post("/interest/activities", { date: today, ...values });
      message.success("活动已记录");
      activityForm.resetFields();
      fetchAll();
    } catch (err: any) {
      message.error(err?.userMessage || "记录失败");
    }
  };

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: "0 auto" }}>
      <Title level={3} style={{ margin: 0 }}>
        <StarOutlined style={{ color: "#722ed1", marginRight: 12 }} />
        兴趣 · Interest
      </Title>
      <Text type="secondary">爱好、特长、激情 — 多元兴趣激发人生宽度</Text>
      <div style={{ marginBottom: 24 }} />

      {/* 兴趣总览 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {interests.length === 0 ? (
          <Col span={24}>
            <Card><Text type="secondary">还没有兴趣。先添加一个吧。</Text></Card>
          </Col>
        ) : interests.map((i) => {
          const rate = i.weekly_target_hours > 0
            ? Math.min(100, (i.actual_weekly_hours / i.weekly_target_hours) * 100)
            : Math.min(100, i.actual_weekly_hours * 10);
          return (
            <Col xs={24} sm={12} md={8} lg={6} key={i.id}>
              <Card
                title={<Space><span>{i.name}</span>{i.category && <Tag>{i.category}</Tag>}</Space>}
                size="small"
              >
                <div style={{ fontSize: 24, fontWeight: 600 }}>
                  {i.actual_weekly_hours.toFixed(1)} / {i.weekly_target_hours} h
                </div>
                <Text type="secondary" style={{ fontSize: 12 }}>本周</Text>
                <Progress percent={Math.round(rate)} strokeColor="#722ed1" size="small" style={{ marginTop: 8 }} />
              </Card>
            </Col>
          );
        })}
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} md={12}>
          <Card title="⭐ 添加兴趣">
            <Form form={interestForm} layout="vertical" onFinish={handleAddInterest}>
              <Form.Item name="name" label="兴趣名称" rules={[{ required: true }]}>
                <Input placeholder="如：钢琴、跑步、阅读" />
              </Form.Item>
              <Form.Item name="category" label="类别">
                <Select
                  options={[
                    { value: "音乐", label: "音乐" }, { value: "运动", label: "运动" },
                    { value: "创作", label: "创作" }, { value: "阅读", label: "阅读" },
                    { value: "游戏", label: "游戏" }, { value: "其他", label: "其他" },
                  ]}
                />
              </Form.Item>
              <Form.Item name="weekly_target_hours" label="周目标时长（小时）" initialValue={3}>
                <InputNumber min={0} max={168} step={0.5} style={{ width: "100%" }} />
              </Form.Item>
              <Form.Item name="description" label="描述">
                <Input.TextArea rows={2} />
              </Form.Item>
              <Button type="primary" htmlType="submit">添加</Button>
            </Form>
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card title="📝 记录活动">
            <Form form={activityForm} layout="vertical" onFinish={handleAddActivity}>
              <Form.Item name="interest_id" label="兴趣" rules={[{ required: true }]}>
                <Select options={interestOptions} placeholder="选择兴趣" disabled={interestOptions.length === 0} />
              </Form.Item>
              <Form.Item name="duration_minutes" label="时长（分钟）" rules={[{ required: true }]}>
                <InputNumber min={1} max={1440} style={{ width: "100%" }} />
              </Form.Item>
              <Form.Item name="note" label="备注">
                <Input.TextArea rows={2} />
              </Form.Item>
              <Button type="primary" htmlType="submit" disabled={interestOptions.length === 0}>记录</Button>
            </Form>
          </Card>
        </Col>
      </Row>

      <Card title="📊 活动记录（30 天）">
        <Table
          dataSource={activities.map((a) => ({
            ...a,
            interest_name: interests.find((i) => i.id === a.interest_id)?.name || "未知",
          }))}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
          columns={[
            { title: "日期", dataIndex: "date", key: "date" },
            { title: "兴趣", dataIndex: "interest_name", key: "interest_name" },
            { title: "时长", dataIndex: "duration_minutes", key: "duration_minutes", render: (m: number) => `${m} 分钟` },
            { title: "备注", dataIndex: "note", key: "note" },
          ]}
        />
      </Card>
    </div>
  );
}