/**
 * Meaning 意义页面
 *
 * 价值观（最多 5 个推荐）+ 人生使命（多版本管理）
 */

import { useEffect, useState } from "react";
import {
  Card, Form, Input, InputNumber, Button, Table, Tag, Typography,
  Row, Col, message, Modal, Empty, InputNumber as AntInputNumber,
} from "antd";
import { BulbOutlined, EditOutlined, DeleteOutlined } from "@ant-design/icons";
import apiClient from "@/api/client";

const { Title, Text, Paragraph } = Typography;

interface Value {
  id: number;
  name: string;
  description: string | null;
  importance: number;
}

interface Purpose {
  id: number;
  statement: string;
  version: number;
  is_current: boolean;
  created_at: string;
}

export default function Meaning() {
  const [values, setValues] = useState<Value[]>([]);
  const [purpose, setPurpose] = useState<Purpose | null>(null);
  const [loading, setLoading] = useState(false);
  const [valueForm] = Form.useForm();
  const [purposeModalOpen, setPurposeModalOpen] = useState(false);
  const [purposeForm] = Form.useForm();
  const [editingValue, setEditingValue] = useState<Value | null>(null);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [vr, pr] = await Promise.all([
        apiClient.get("/meaning/values"),
        apiClient.get("/meaning/purpose"),
      ]);
      setValues(vr.data.data || []);
      setPurpose(pr.data.data);
    } catch (err: any) {
      message.error(err?.userMessage || "加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  const handleAddValue = async (values: Record<string, unknown>) => {
    try {
      await apiClient.post("/meaning/values", values);
      message.success("价值观已添加");
      valueForm.resetFields();
      fetchAll();
    } catch (err: any) {
      message.error("添加失败");
    }
  };

  const handleUpdateValue = async (id: number, fields: Record<string, unknown>) => {
    try {
      await apiClient.put(`/meaning/values/${id}`, fields);
      message.success("已更新");
      setEditingValue(null);
      fetchAll();
    } catch (err: any) {
      message.error("更新失败");
    }
  };

  const handleDeleteValue = async (id: number) => {
    try {
      await apiClient.delete(`/meaning/values/${id}`);
      message.success("已删除");
      fetchAll();
    } catch (err: any) {
      message.error(err?.userMessage || "删除失败");
    }
  };

  const handleUpdatePurpose = async (fields: Record<string, unknown>) => {
    try {
      await apiClient.put("/meaning/purpose", fields);
      message.success("人生使命已更新");
      setPurposeModalOpen(false);
      purposeForm.resetFields();
      fetchAll();
    } catch (err: any) {
      message.error("更新失败");
    }
  };

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: "0 auto" }}>
      <Title level={3} style={{ margin: 0 }}>
        <BulbOutlined style={{ color: "#fadb14", marginRight: 12 }} />
        意义 · Meaning
      </Title>
      <Text type="secondary">价值观、人生使命 — 意义感是长期幸福的基石</Text>
      <div style={{ marginBottom: 24 }} />

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={8}>
          <Card><Text type="secondary">价值观</Text><div style={{ fontSize: 30, fontWeight: 600 }}>{values.length}</div></Card>
        </Col>
        <Col xs={12} sm={8}>
          <Card>
            <Text type="secondary">使命</Text>
            <div style={{ fontSize: 18, color: purpose ? "#52c41a" : "#999" }}>
              {purpose ? `✓ v${purpose.version}` : "未设定"}
            </div>
          </Card>
        </Col>
        <Col xs={12} sm={8}>
          <Card><Text type="secondary">平均重要性</Text><div style={{ fontSize: 30, color: "#fadb14", fontWeight: 600 }}>{values.length > 0 ? (values.reduce((sum, v) => sum + v.importance, 0) / values.length).toFixed(1) : "0"}</div></Card>
        </Col>
      </Row>

      {/* 人生使命 — 中心卡片 */}
      <Card
        title={
          <span>
            <BulbOutlined style={{ color: "#fadb14", marginRight: 8 }} />
            人生使命
          </span>
        }
        extra={<Button type="primary" icon={<EditOutlined />} onClick={() => setPurposeModalOpen(true)}>{purpose ? "更新" : "设定"}</Button>}
        style={{ marginBottom: 24, background: "#fffbe6" }}
      >
        {purpose ? (
          <Paragraph style={{ fontSize: 18, lineHeight: 1.8, marginBottom: 0 }}>
            "{purpose.statement}"
          </Paragraph>
        ) : (
          <Empty description="还没有设定人生使命。点击右上角设定 →" />
        )}
      </Card>

      <Row gutter={[16, 16]}>
        {/* 价值观录入 */}
        <Col xs={24} md={12}>
          <Card title="⭐ 添加价值观">
            <Form form={valueForm} layout="vertical" onFinish={handleAddValue} initialValues={{ importance: 8 }}>
              <Form.Item name="name" label="价值观名称" rules={[{ required: true }]}>
                <Input placeholder="如：自由、家庭、成长、贡献" />
              </Form.Item>
              <Form.Item name="importance" label="重要性（1-10）">
                <AntInputNumber min={1} max={10} style={{ width: "100%" }} />
              </Form.Item>
              <Form.Item name="description" label="为什么重要？">
                <Input.TextArea rows={3} />
              </Form.Item>
              <Button type="primary" htmlType="submit">添加</Button>
            </Form>
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card title="💭 价值观建议">
            <Paragraph>推荐保留 5 个核心价值观。</Paragraph>
            <Paragraph>每个价值观：</Paragraph>
            <ul>
              <li>具体可衡量（不只是"成功"）</li>
              <li>与你的日常选择一致</li>
              <li>10 年后仍适用</li>
            </ul>
            <Paragraph type="secondary" style={{ fontSize: 12 }}>
              常见的 5 个：自由 / 家庭 / 健康 / 成长 / 贡献
            </Paragraph>
          </Card>
        </Col>
      </Row>

      {/* 价值观列表 */}
      <Card title={`⭐ 价值观（${values.length}/5）`} style={{ marginTop: 24 }}>
        <Table
          dataSource={values}
          rowKey="id"
          loading={loading}
          pagination={false}
          columns={[
            { title: "名称", dataIndex: "name", key: "name" },
            {
              title: "重要性",
              dataIndex: "importance",
              key: "importance",
              render: (i: number) => (
                <Tag color={i >= 9 ? "red" : i >= 7 ? "orange" : i >= 5 ? "blue" : "default"}>
                  {"⭐".repeat(Math.min(10, i))} {i}/10
                </Tag>
              ),
            },
            { title: "描述", dataIndex: "description", key: "description" },
            {
              title: "操作",
              key: "actions",
              render: (v: Value) => (
                <span>
                  <Button size="small" icon={<EditOutlined />} onClick={() => setEditingValue(v)}>编辑</Button>
                  <Button
                    size="small"
                    danger
                    icon={<DeleteOutlined />}
                    style={{ marginLeft: 8 }}
                    onClick={() => handleDeleteValue(v.id)}
                  >
                    删除
                  </Button>
                </span>
              ),
            },
          ]}
        />
      </Card>

      {/* 人生使命 Modal */}
      <Modal
        title="更新人生使命"
        open={purposeModalOpen}
        onCancel={() => setPurposeModalOpen(false)}
        footer={null}
      >
        <Form form={purposeForm} layout="vertical" onFinish={handleUpdatePurpose} initialValues={purpose ? { statement: purpose.statement } : {}}>
          <Form.Item name="statement" label="你的人生使命是什么？" rules={[{ required: true, min: 10 }]}>
            <Input.TextArea rows={6} placeholder="如：用我的研究让 AI 更值得信赖，让家人过上更稳定的生活。" />
          </Form.Item>
          <Paragraph type="secondary" style={{ fontSize: 12 }}>
            提示：使命感会随年龄变化。每次更新会创建新版本（旧版本保留）。
          </Paragraph>
          <Button type="primary" htmlType="submit">保存</Button>
        </Form>
      </Modal>

      {editingValue && (
        <Card
          title={`编辑《${editingValue.name}》`}
          style={{ marginTop: 24 }}
          extra={<Button onClick={() => setEditingValue(null)}>取消</Button>}
        >
          <Form
            layout="inline"
            onFinish={(v) => handleUpdateValue(editingValue.id, v)}
            initialValues={editingValue}
          >
            <Form.Item name="importance" label="重要性">
              <AntInputNumber min={1} max={10} />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit">保存</Button>
            </Form.Item>
          </Form>
        </Card>
      )}
    </div>
  );
}