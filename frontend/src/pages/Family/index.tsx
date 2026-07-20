/**
 * Family 家庭页面
 *
 * 家人元数据（公开信息）+ 重要日期 + 互动记录
 * 隐私优先：不存对话/私密内容
 */

import { useEffect, useState } from "react";
import {
  Card, Form, Input, Select, DatePicker, Button, Table, Tag, Typography,
  Row, Col, message, Space,
} from "antd";
import { HomeOutlined, CalendarOutlined } from "@ant-design/icons";
import apiClient from "@/api/client";
import dayjs from "dayjs";

const { Title, Text } = Typography;

interface Member {
  id: number;
  name: string;
  relation: string;
  birthday: string | null;
  note: string | null;
  days_to_birthday: number | null;
  created_at: string;
}

interface Interaction {
  id: number;
  member_id: number;
  date: string;
  interaction_type: string;
  duration_minutes: number | null;
  note: string | null;
}

interface Upcoming {
  member_id: number;
  name: string;
  relation: string;
  birthday: string;
  days_until: number;
}

export default function Family() {
  const [members, setMembers] = useState<Member[]>([]);
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [upcoming, setUpcoming] = useState<Upcoming[]>([]);
  const [loading, setLoading] = useState(false);
  const [memberForm] = Form.useForm();
  const [interForm] = Form.useForm();

  const memberOptions = members.map((m) => ({ label: `${m.name} (${m.relation})`, value: m.id }));
  const interactionTypes = [
    { label: "📞 电话", value: "call" },
    { label: "🏠 见面", value: "visit" },
    { label: "💬 消息", value: "message" },
    { label: "🎁 礼物", value: "gift" },
    { label: "其他", value: "other" },
  ];

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [mr, ir, ur] = await Promise.all([
        apiClient.get("/family/members"),
        apiClient.get("/family/interactions", { params: { days: 30 } }),
        apiClient.get("/family/upcoming", { params: { within_days: 30 } }),
      ]);
      setMembers(mr.data.data || []);
      setInteractions(ir.data.data || []);
      setUpcoming(ur.data.data || []);
    } catch (err: any) {
      message.error(err?.userMessage || "加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  const handleAddMember = async (values: Record<string, unknown>) => {
    try {
      await apiClient.post("/family/members", {
        ...values,
        birthday: values.birthday ? dayjs(values.birthday as string).format("YYYY-MM-DD") : null,
      });
      message.success("成员已添加");
      memberForm.resetFields();
      fetchAll();
    } catch (err: any) {
      message.error("添加失败");
    }
  };

  const handleAddInteraction = async (values: Record<string, unknown>) => {
    try {
      await apiClient.post("/family/interactions", {
        ...values,
        date: dayjs().format("YYYY-MM-DD"),
      });
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
        <HomeOutlined style={{ color: "#eb2f96", marginRight: 12 }} />
        家庭 · Family
      </Title>
      <Text type="secondary">家人关系、重要日期、亲情 — 家庭支持是人生韧性来源</Text>
      <div style={{ marginBottom: 24 }} />

      {/* 30 天内生日提醒 */}
      <Card
        title={
          <Space>
            <CalendarOutlined />
            <span>📅 30 天内生日</span>
          </Space>
        }
        style={{ marginBottom: 24 }}
      >
        {upcoming.length === 0 ? (
          <Text type="secondary">未来 30 天没有生日，添加家人后会显示</Text>
        ) : (
          <Row gutter={[12, 12]}>
            {upcoming.map((u) => (
              <Col xs={24} sm={12} md={8} key={u.member_id}>
                <Card type="inner" size="small">
                  <Text strong>{u.name}</Text> <Tag>{u.relation}</Tag>
                  <div style={{ fontSize: 24, color: "#eb2f96", fontWeight: 600, marginTop: 4 }}>
                    还有 {u.days_until} 天
                  </div>
                  <Text type="secondary" style={{ fontSize: 12 }}>{u.birthday}</Text>
                </Card>
              </Col>
            ))}
          </Row>
        )}
      </Card>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {/* 添加家人 */}
        <Col xs={24} md={12}>
          <Card title="👨‍👩‍👧 添加家人">
            <Form form={memberForm} layout="vertical" onFinish={handleAddMember}>
              <Form.Item name="name" label="姓名" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
              <Form.Item name="relation" label="关系" rules={[{ required: true }]}>
                <Select
                  options={[
                    { value: "父", label: "父" }, { value: "母", label: "母" },
                    { value: "兄", label: "兄" }, { value: "姐", label: "姐" },
                    { value: "弟", label: "弟" }, { value: "妹", label: "妹" },
                    { value: "其他", label: "其他" },
                  ]}
                />
              </Form.Item>
              <Form.Item name="birthday" label="生日">
                <DatePicker style={{ width: "100%" }} />
              </Form.Item>
              <Form.Item name="note" label="备注">
                <Input.TextArea rows={2} />
              </Form.Item>
              <Button type="primary" htmlType="submit">添加</Button>
            </Form>
          </Card>
        </Col>

        {/* 记录互动 */}
        <Col xs={24} md={12}>
          <Card title="📞 记录互动">
            <Form form={interForm} layout="vertical" onFinish={handleAddInteraction}>
              <Form.Item name="member_id" label="家人" rules={[{ required: true }]}>
                <Select options={memberOptions} placeholder="选择家人" disabled={memberOptions.length === 0} />
              </Form.Item>
              <Form.Item name="interaction_type" label="方式" rules={[{ required: true }]}>
                <Select options={interactionTypes} />
              </Form.Item>
              <Form.Item name="duration_minutes" label="时长（分钟）">
                <Input type="number" />
              </Form.Item>
              <Form.Item name="note" label="备注">
                <Input.TextArea rows={2} />
              </Form.Item>
              <Button type="primary" htmlType="submit" disabled={memberOptions.length === 0}>记录</Button>
            </Form>
          </Card>
        </Col>
      </Row>

      {/* 家人列表 */}
      <Card title={`👨‍👩‍👧‍👦 家人列表（${members.length}）`} style={{ marginBottom: 24 }}>
        <Table
          dataSource={members}
          rowKey="id"
          loading={loading}
          pagination={false}
          columns={[
            { title: "姓名", dataIndex: "name", key: "name" },
            { title: "关系", dataIndex: "relation", key: "relation" },
            { title: "生日", dataIndex: "birthday", key: "birthday" },
            {
              title: "距生日",
              dataIndex: "days_to_birthday",
              key: "days",
              render: (d: number | null) => d != null ? <Tag color="#eb2f96">{d} 天</Tag> : "—",
            },
            { title: "备注", dataIndex: "note", key: "note" },
          ]}
        />
      </Card>

      {/* 最近互动 */}
      <Card title="📋 最近互动（30 天）">
        <Table
          dataSource={interactions.map((i) => ({
            ...i,
            member_name: members.find((m) => m.id === i.member_id)?.name || "未知",
          }))}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
          columns={[
            { title: "日期", dataIndex: "date", key: "date" },
            { title: "家人", dataIndex: "member_name", key: "member_name" },
            { title: "方式", dataIndex: "interaction_type", key: "interaction_type" },
            { title: "时长", dataIndex: "duration_minutes", key: "duration_minutes" },
            { title: "备注", dataIndex: "note", key: "note" },
          ]}
        />
      </Card>
    </div>
  );
}