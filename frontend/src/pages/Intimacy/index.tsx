/**
 * Intimacy 亲密页面
 *
 * 关系元数据 + 纪念日倒计时（不存私密内容）
 */

import { useEffect, useState } from "react";
import {
  Card, Form, Input, Select, DatePicker, Button, Table, Tag, Typography,
  Row, Col, message, Alert, Tabs,
} from "antd";
import { HeartOutlined } from "@ant-design/icons";
import apiClient from "@/api/client";
import dayjs from "dayjs";

const { Title, Text } = Typography;

interface Relationship {
  id: number;
  name: string;
  relation_type: string;
  anniversary: string | null;
  status: string;
  note: string | null;
  days_to_anniversary: number | null;
}

interface Anniversary {
  id: number;
  title: string;
  date: string;
  recurring: boolean;
  note: string | null;
  days_until: number | null;
}

export default function Intimacy() {
  const [relationships, setRelationships] = useState<Relationship[]>([]);
  const [anniversaries, setAnniversaries] = useState<Anniversary[]>([]);
  const [loading, setLoading] = useState(false);
  const [relForm] = Form.useForm();
  const [annForm] = Form.useForm();

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [rr, ar] = await Promise.all([
        apiClient.get("/intimacy/relationships"),
        apiClient.get("/intimacy/anniversaries"),
      ]);
      setRelationships(rr.data.data || []);
      setAnniversaries(ar.data.data || []);
    } catch (err: any) {
      message.error(err?.userMessage || "加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  const handleAddRel = async (values: Record<string, unknown>) => {
    try {
      await apiClient.post("/intimacy/relationships", {
        ...values,
        anniversary: values.anniversary ? dayjs(values.anniversary as string).format("YYYY-MM-DD") : null,
      });
      message.success("关系已添加");
      relForm.resetFields();
      fetchAll();
    } catch (err: any) {
      message.error("添加失败");
    }
  };

  const handleAddAnn = async (values: Record<string, unknown>) => {
    try {
      await apiClient.post("/intimacy/anniversaries", {
        ...values,
        date: dayjs(values.date as string).format("YYYY-MM-DD"),
        recurring: values.recurring === "recurring" || values.recurring === true,
      });
      message.success("纪念日已添加");
      annForm.resetFields();
      fetchAll();
    } catch (err: any) {
      message.error("添加失败");
    }
  };

  const upcoming = anniversaries.filter((a) => a.days_until != null && a.days_until <= 30).sort((a, b) => (a.days_until || 0) - (b.days_until || 0));

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: "0 auto" }}>
      <Title level={3} style={{ margin: 0 }}>
        <HeartOutlined style={{ color: "#ff4d4f", marginRight: 12 }} />
        亲密 · Intimacy
      </Title>
      <Text type="secondary">爱情、深度关系 — 亲密关系是幸福感的核心来源</Text>
      <div style={{ marginBottom: 24 }} />

      {/* 30 天内纪念日 */}
      {upcoming.length > 0 && (
        <Alert
          type="info"
          message="💝 即将到来的纪念日"
          description={
            <Row gutter={[12, 12]}>
              {upcoming.slice(0, 6).map((a) => (
                <Col xs={24} sm={12} md={8} key={a.id}>
                  <Card type="inner" size="small">
                    <Text strong>{a.title}</Text>
                    <div style={{ fontSize: 20, color: "#ff4d4f", fontWeight: 600 }}>
                      还有 {a.days_until} 天
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          }
          style={{ marginBottom: 24 }}
          showIcon
        />
      )}

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={8}>
          <Card><Text type="secondary">关系</Text><div style={{ fontSize: 30, fontWeight: 600 }}>{relationships.length}</div></Card>
        </Col>
        <Col xs={12} sm={8}>
          <Card><Text type="secondary">纪念日</Text><div style={{ fontSize: 30, fontWeight: 600 }}>{anniversaries.length}</div></Card>
        </Col>
        <Col xs={12} sm={8}>
          <Card><Text type="secondary">活跃</Text><div style={{ fontSize: 30, color: "#52c41a", fontWeight: 600 }}>{relationships.filter((r) => r.status === "active").length}</div></Card>
        </Col>
      </Row>

      <Tabs
        defaultActiveKey="rel"
        items={[
          {
            key: "rel",
            label: `💝 关系 (${relationships.length})`,
            children: (
              <>
                <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
                  <Col xs={24} md={12}>
                    <Card title="💝 添加关系">
                      <Form form={relForm} layout="vertical" onFinish={handleAddRel}>
                        <Form.Item name="name" label="姓名" rules={[{ required: true }]}>
                          <Input />
                        </Form.Item>
                        <Form.Item name="relation_type" label="关系类型" rules={[{ required: true }]}>
                          <Select
                            options={[
                              { value: "伴侣", label: "伴侣" }, { value: "配偶", label: "配偶" },
                              { value: "好友", label: "好友" }, { value: "其他", label: "其他" },
                            ]}
                          />
                        </Form.Item>
                        <Form.Item name="anniversary" label="纪念日">
                          <DatePicker style={{ width: "100%" }} />
                        </Form.Item>
                        <Form.Item name="note" label="备注">
                          <Input.TextArea rows={2} />
                        </Form.Item>
                        <Button type="primary" htmlType="submit">添加</Button>
                      </Form>
                    </Card>
                  </Col>
                </Row>

                <Card title="💕 关系列表">
                  <Table
                    dataSource={relationships}
                    rowKey="id"
                    loading={loading}
                    pagination={false}
                    columns={[
                      { title: "姓名", dataIndex: "name", key: "name" },
                      { title: "类型", dataIndex: "relation_type", key: "relation_type" },
                      { title: "纪念日", dataIndex: "anniversary", key: "anniversary" },
                      {
                        title: "距纪念日",
                        dataIndex: "days_to_anniversary",
                        key: "days",
                        render: (d: number | null) => d != null ? (
                          d < 0 ? <Tag>{d} 天</Tag> : <Tag color="#ff4d4f">{d} 天</Tag>
                        ) : "—",
                      },
                      {
                        title: "状态",
                        dataIndex: "status",
                        key: "status",
                        render: (s: string) => <Tag color={s === "active" ? "green" : "default"}>{s === "active" ? "活跃" : "已结束"}</Tag>,
                      },
                    ]}
                  />
                </Card>
              </>
            ),
          },
          {
            key: "ann",
            label: `📅 纪念日 (${anniversaries.length})`,
            children: (
              <>
                <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
                  <Col xs={24} md={12}>
                    <Card title="📅 添加纪念日">
                      <Form
                        form={annForm}
                        layout="vertical"
                        onFinish={handleAddAnn}
                        initialValues={{ recurring: "recurring" }}
                      >
                        <Form.Item name="title" label="纪念日" rules={[{ required: true }]}>
                          <Input placeholder="如：结婚纪念日、初次见面" />
                        </Form.Item>
                        <Form.Item name="date" label="日期" rules={[{ required: true }]}>
                          <DatePicker style={{ width: "100%" }} />
                        </Form.Item>
                        <Form.Item name="recurring" label="是否每年">
                          <Select
                            options={[
                              { value: "recurring", label: "✓ 每年循环" },
                              { value: "once", label: "✗ 一次性" },
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

                <Card title="📅 纪念日列表">
                  <Table
                    dataSource={anniversaries}
                    rowKey="id"
                    loading={loading}
                    pagination={false}
                    columns={[
                      { title: "标题", dataIndex: "title", key: "title" },
                      { title: "日期", dataIndex: "date", key: "date" },
                      {
                        title: "循环",
                        dataIndex: "recurring",
                        key: "recurring",
                        render: (r: boolean) => r ? <Tag color="blue">每年</Tag> : <Tag>一次性</Tag>,
                      },
                      {
                        title: "倒计时",
                        dataIndex: "days_until",
                        key: "days",
                        render: (d: number | null) => d != null ? `${d} 天` : "—",
                      },
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