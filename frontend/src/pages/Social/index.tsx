/**
 * Social 社交页面
 *
 * 联系人列表 + 亲密度 + 久未联系提醒（仅 closeness ≥ 7）
 */

import { useEffect, useState } from "react";
import {
  Card, Form, Input, Select, InputNumber, Button, Table, Tag, Typography,
  Row, Col, message, Space, Alert,
} from "antd";
import { TeamOutlined, BellOutlined } from "@ant-design/icons";
import apiClient from "@/api/client";

const { Title, Text } = Typography;

interface Contact {
  id: number;
  name: string;
  relation: string | null;
  closeness: number;
  note: string | null;
  days_since_last_contact: number | null;
  needs_reconnect: boolean;
}

interface Interaction {
  id: number;
  contact_id: number;
  date: string;
  interaction_type: string;
  duration_minutes: number | null;
}

interface ReconnectItem {
  contact_id: number;
  name: string;
  closeness: number;
  days_since_last: number;
}

export default function Social() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [reconnect, setReconnect] = useState<ReconnectItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [contactForm] = Form.useForm();
  const [interForm] = Form.useForm();

  const contactOptions = contacts.map((c) => ({ label: c.name, value: c.id }));

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [cr, ir, rr] = await Promise.all([
        apiClient.get("/social/contacts"),
        apiClient.get("/social/interactions", { params: { days: 30 } }),
        apiClient.get("/social/reconnect"),
      ]);
      setContacts(cr.data.data || []);
      setInteractions(ir.data.data || []);
      setReconnect(rr.data.data || []);
    } catch (err: any) {
      message.error(err?.userMessage || "加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  const handleAddContact = async (values: Record<string, unknown>) => {
    try {
      await apiClient.post("/social/contacts", values);
      message.success("联系人已添加");
      contactForm.resetFields();
      fetchAll();
    } catch (err: any) {
      message.error("添加失败");
    }
  };

  const handleAddInter = async (values: Record<string, unknown>) => {
    try {
      const today = new Date().toISOString().slice(0, 10);
      await apiClient.post("/social/interactions", { date: today, ...values });
      message.success("互动已记录");
      interForm.resetFields();
      fetchAll();
    } catch (err: any) {
      message.error(err?.userMessage || "记录失败");
    }
  };

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: "0 auto" }}>
      <Title level={3} style={{ margin: 0 }}>
        <TeamOutlined style={{ color: "#13c2c2", marginRight: 12 }} />
        社交 · Social
      </Title>
      <Text type="secondary">友谊、深度关系、社交网络 — 社交能力是领导力基础</Text>
      <div style={{ marginBottom: 24 }} />

      {/* 久未联系提醒 */}
      {reconnect.length > 0 && (
        <Alert
          type="warning"
          message="📞 该联系了"
          description={
            <div>
              {reconnect.map((r) => (
                <Tag key={r.contact_id} color="orange" style={{ margin: 4 }}>
                  {r.name} · {r.days_since_last} 天未联系 · 亲密度 {r.closeness}
                </Tag>
              ))}
            </div>
          }
          style={{ marginBottom: 24 }}
          showIcon
          icon={<BellOutlined />}
        />
      )}

      {/* 联系人总览 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card><Text type="secondary">联系人</Text><div style={{ fontSize: 30, fontWeight: 600 }}>{contacts.length}</div></Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card><Text type="secondary">亲密朋友（≥8）</Text><div style={{ fontSize: 30, color: "#13c2c2", fontWeight: 600 }}>{contacts.filter((c) => c.closeness >= 8).length}</div></Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card><Text type="secondary">30 天互动</Text><div style={{ fontSize: 30, color: "#52c41a", fontWeight: 600 }}>{interactions.length}</div></Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card><Text type="secondary">需联系</Text><div style={{ fontSize: 30, color: "#fa8c16", fontWeight: 600 }}>{reconnect.length}</div></Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} md={12}>
          <Card title="👥 添加联系人">
            <Form form={contactForm} layout="vertical" onFinish={handleAddContact} initialValues={{ closeness: 5 }}>
              <Form.Item name="name" label="姓名" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
              <Form.Item name="relation" label="关系">
                <Select
                  options={[
                    { value: "朋友", label: "朋友" }, { value: "同事", label: "同事" },
                    { value: "同学", label: "同学" }, { value: "亲戚", label: "亲戚" },
                    { value: "其他", label: "其他" },
                  ]}
                />
              </Form.Item>
              <Form.Item name="closeness" label="亲密度（1-10）">
                <InputNumber min={1} max={10} style={{ width: "100%" }} />
              </Form.Item>
              <Form.Item name="note" label="备注">
                <Input.TextArea rows={2} />
              </Form.Item>
              <Button type="primary" htmlType="submit">添加</Button>
            </Form>
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card title="📞 记录互动">
            <Form form={interForm} layout="vertical" onFinish={handleAddInter}>
              <Form.Item name="contact_id" label="联系人" rules={[{ required: true }]}>
                <Select options={contactOptions} placeholder="选择联系人" disabled={contactOptions.length === 0} />
              </Form.Item>
              <Form.Item name="interaction_type" label="方式" rules={[{ required: true }]}>
                <Select
                  options={[
                    { value: "call", label: "📞 电话" }, { value: "message", label: "💬 消息" },
                    { value: "meet", label: "🤝 见面" }, { value: "video", label: "📹 视频" },
                    { value: "other", label: "其他" },
                  ]}
                />
              </Form.Item>
              <Form.Item name="duration_minutes" label="时长（分钟）">
                <InputNumber min={0} style={{ width: "100%" }} />
              </Form.Item>
              <Button type="primary" htmlType="submit" disabled={contactOptions.length === 0}>记录</Button>
            </Form>
          </Card>
        </Col>
      </Row>

      <Card title={`👥 联系人列表（${contacts.length}）`}>
        <Table
          dataSource={contacts}
          rowKey="id"
          loading={loading}
          pagination={false}
          columns={[
            { title: "姓名", dataIndex: "name", key: "name" },
            { title: "关系", dataIndex: "relation", key: "relation" },
            {
              title: "亲密度",
              dataIndex: "closeness",
              key: "closeness",
              render: (c: number) => <Tag color={c >= 8 ? "red" : c >= 5 ? "orange" : "default"}>{c} / 10</Tag>,
            },
            {
              title: "上次联系",
              dataIndex: "days_since_last_contact",
              key: "days",
              render: (d: number | null) => d == null ? <Tag>从未</Tag> : d > 30 ? <Tag color="red">{d} 天前</Tag> : d > 7 ? <Tag color="orange">{d} 天前</Tag> : <Tag color="green">{d} 天前</Tag>,
            },
            {
              title: "状态",
              dataIndex: "needs_reconnect",
              key: "status",
              render: (n: boolean) => n ? <Tag color="red">需联系</Tag> : <Tag color="green">良好</Tag>,
            },
          ]}
        />
      </Card>
    </div>
  );
}