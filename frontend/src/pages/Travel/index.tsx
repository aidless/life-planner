/**
 * Travel 旅行页面
 *
 * 旅行记录 + 心愿单（bucket list → trips 自动转换）
 */

import { useEffect, useState } from "react";
import {
  Card, Form, Input, InputNumber, DatePicker, Select, Button, Table, Tag, Typography,
  Row, Col, Progress, message, Tabs, Rate,
} from "antd";
import { GlobalOutlined } from "@ant-design/icons";
import apiClient from "@/api/client";
import dayjs from "dayjs";

const { Title, Text } = Typography;

interface Trip {
  id: number;
  destination: string;
  start_date: string;
  end_date: string | null;
  cost_cny: number | null;
  rating: number | null;
  photo_count: number;
}

interface BucketItem {
  id: number;
  destination: string;
  priority: number;
  note: string | null;
  completed: boolean;
}

export default function Travel() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [bucket, setBucket] = useState<BucketItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [tripForm] = Form.useForm();
  const [bucketForm] = Form.useForm();

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [tr, br] = await Promise.all([
        apiClient.get("/travel/trips"),
        apiClient.get("/travel/bucket-list"),
      ]);
      setTrips(tr.data.data || []);
      setBucket(br.data.data || []);
    } catch (err: any) {
      message.error(err?.userMessage || "加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  const handleAddTrip = async (values: Record<string, unknown>) => {
    try {
      await apiClient.post("/travel/trips", {
        ...values,
        start_date: values.start_date ? dayjs(values.start_date as string).format("YYYY-MM-DD") : null,
        end_date: values.end_date ? dayjs(values.end_date as string).format("YYYY-MM-DD") : null,
      });
      message.success("旅行已添加");
      tripForm.resetFields();
      fetchAll();
    } catch (err: any) {
      message.error("添加失败");
    }
  };

  const handleAddBucket = async (values: Record<string, unknown>) => {
    try {
      await apiClient.post("/travel/bucket-list", values);
      message.success("心愿单已添加");
      bucketForm.resetFields();
      fetchAll();
    } catch (err: any) {
      message.error("添加失败");
    }
  };

  const completedCount = bucket.filter((b) => b.completed).length;
  const completionRate = bucket.length > 0 ? (completedCount / bucket.length) * 100 : 0;
  const thisYearTrips = trips.filter((t) => t.start_date.startsWith(new Date().getFullYear().toString()));

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: "0 auto" }}>
      <Title level={3} style={{ margin: 0 }}>
        <GlobalOutlined style={{ color: "#52c41a", marginRight: 12 }} />
        旅行 · Travel
      </Title>
      <Text type="secondary">看世界、跨文化体验 — 旅行扩展认知边界</Text>
      <div style={{ marginBottom: 24 }} />

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card><Text type="secondary">旅行总数</Text><div style={{ fontSize: 30, fontWeight: 600 }}>{trips.length}</div></Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card><Text type="secondary">今年</Text><div style={{ fontSize: 30, color: "#52c41a", fontWeight: 600 }}>{thisYearTrips.length}</div></Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card><Text type="secondary">心愿单</Text><div style={{ fontSize: 30, fontWeight: 600 }}>{bucket.length}</div></Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card><Text type="secondary">完成率</Text><Progress percent={Math.round(completionRate)} strokeColor="#52c41a" /></Card>
        </Col>
      </Row>

      <Tabs
        defaultActiveKey="trips"
        items={[
          {
            key: "trips",
            label: `🧳 旅行记录 (${trips.length})`,
            children: (
              <>
                <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
                  <Col xs={24} md={12}>
                    <Card title="✈️ 添加旅行">
                      <Form form={tripForm} layout="vertical" onFinish={handleAddTrip}>
                        <Form.Item name="destination" label="目的地" rules={[{ required: true }]}>
                          <Input placeholder="如：京都、罗马、新西兰" />
                        </Form.Item>
                        <Form.Item name="start_date" label="出发日期" rules={[{ required: true }]}>
                          <DatePicker style={{ width: "100%" }} />
                        </Form.Item>
                        <Form.Item name="end_date" label="返回日期">
                          <DatePicker style={{ width: "100%" }} />
                        </Form.Item>
                        <Form.Item name="cost_cny" label="花费（元）">
                          <InputNumber min={0} style={{ width: "100%" }} />
                        </Form.Item>
                        <Form.Item name="rating" label="评分">
                          <Rate />
                        </Form.Item>
                        <Form.Item name="note" label="回忆">
                          <Input.TextArea rows={2} />
                        </Form.Item>
                        <Button type="primary" htmlType="submit">添加</Button>
                      </Form>
                    </Card>
                  </Col>
                  <Col xs={24} md={12}>
                    <Card title="💡 旅行哲学">
                      <p>每年至少 4 次旅行 = 季度目标</p>
                      <p>每段旅行记录 3 件事：</p>
                      <ul>
                        <li>看过的风景</li>
                        <li>遇到的人</li>
                        <li>改变的想法</li>
                      </ul>
                    </Card>
                  </Col>
                </Row>

                <Card title="🗺️ 我的旅行地图">
                  <Table
                    dataSource={trips}
                    rowKey="id"
                    loading={loading}
                    pagination={{ pageSize: 10 }}
                    columns={[
                      { title: "目的地", dataIndex: "destination", key: "destination" },
                      { title: "出发", dataIndex: "start_date", key: "start_date" },
                      { title: "返回", dataIndex: "end_date", key: "end_date" },
                      { title: "花费", dataIndex: "cost_cny", key: "cost_cny", render: (c: number | null) => c ? `¥${c}` : "—" },
                      {
                        title: "评分",
                        dataIndex: "rating",
                        key: "rating",
                        render: (r: number | null) => r != null ? `${r} / 5` : "—",
                      },
                      { title: "照片", dataIndex: "photo_count", key: "photo_count" },
                    ]}
                  />
                </Card>
              </>
            ),
          },
          {
            key: "bucket",
            label: `🎯 心愿单 (${completedCount}/${bucket.length})`,
            children: (
              <>
                <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
                  <Col xs={24} md={12}>
                    <Card title="✨ 添加心愿">
                      <Form form={bucketForm} layout="vertical" onFinish={handleAddBucket} initialValues={{ priority: 1 }}>
                        <Form.Item name="destination" label="目的地" rules={[{ required: true }]}>
                          <Input placeholder="想去的地方" />
                        </Form.Item>
                        <Form.Item name="priority" label="优先级">
                          <Select
                            options={[
                              { value: 1, label: "⭐ 必去" },
                              { value: 2, label: "想去" },
                              { value: 3, label: "以后" },
                            ]}
                          />
                        </Form.Item>
                        <Form.Item name="note" label="备注">
                          <Input.TextArea rows={2} />
                        </Form.Item>
                        <Button type="primary" htmlType="submit">添加</Button>
                      </Form>
                    </Card>
                  </Col>
                </Row>

                <Card title={`🌍 心愿单（${completedCount} / ${bucket.length} 已完成）`}>
                  <Table
                    dataSource={bucket}
                    rowKey="id"
                    loading={loading}
                    pagination={{ pageSize: 10 }}
                    columns={[
                      { title: "目的地", dataIndex: "destination", key: "destination" },
                      {
                        title: "优先级",
                        dataIndex: "priority",
                        key: "priority",
                        render: (p: number) => <Tag color={p === 1 ? "red" : p === 2 ? "orange" : "default"}>{p === 1 ? "必去" : p === 2 ? "想去" : "以后"}</Tag>,
                      },
                      {
                        title: "状态",
                        dataIndex: "completed",
                        key: "completed",
                        render: (c: boolean) => c ? <Tag color="green">✓ 已完成</Tag> : <Tag>待完成</Tag>,
                      },
                      { title: "备注", dataIndex: "note", key: "note" },
                    ]}
                  />
                </Card>
              </>
            ),
          },
        ]}
      />
    </div>
  );
}