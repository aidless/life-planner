/**
 * Habits 习惯页面（P4-2）
 *
 * 新建习惯（POST /api/habits，无尾斜杠）+ 打卡（POST /{id}/checkin）+ 连击（GET /{id}/streak）
 * 后端：backend/app/modules/habits（prefix /api/habits）
 */

import { useEffect, useState } from "react";
import {
  Card, Form, Input, InputNumber, Select, Button, Table, Tag,
  Typography, Row, Col, message, Space, Switch,
} from "antd";
import { CheckCircleOutlined, FireOutlined, PlusOutlined } from "@ant-design/icons";
import apiClient from "@/api/client";
import dayjs from "dayjs";

const { Title, Text, Paragraph } = Typography;

interface Habit {
  id: number;
  name: string;
  description: string | null;
  category: string | null;
  frequency: string;
  target_count: number;
  is_active: number;
  streak: number;
  completion_rate_30d: number;
  created_at: string;
}

interface Streak {
  habit_id: number;
  current_streak: number;
  longest_streak: number;
  total_checkins: number;
}

export default function Habits() {
  const [habits, setHabits] = useState<Habit[]>([]);
  const [streaks, setStreaks] = useState<Record<number, Streak>>({});
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  const fetchAll = async () => {
    setLoading(true);
    try {
      const r = await apiClient.get("/habits");
      const list: Habit[] = r.data.data || [];
      setHabits(list);
      // 拉每个习惯的连击数据
      const sm: Record<number, Streak> = {};
      await Promise.all(list.map(async (h) => {
        try {
          const sr = await apiClient.get(`/habits/${h.id}/streak`);
          if (sr.data.data) sm[h.id] = sr.data.data;
        } catch {
          /* 单个连击失败不影响列表 */
        }
      }));
      setStreaks(sm);
    } catch (err: any) {
      message.error(err?.userMessage || "加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const submitHabit = async (v: any) => {
    try {
      // 注意：后端路由是 POST ""（无尾斜杠），不能写成 /habits/
      await apiClient.post("/habits", {
        name: v.name,
        description: v.description || null,
        category: v.category || null,
        frequency: v.frequency || "daily",
        target_count: v.target_count || 1,
      });
      message.success("习惯已创建");
      form.resetFields();
      fetchAll();
    } catch (err: any) {
      message.error(err?.userMessage || "创建失败");
    }
  };

  const checkin = async (id: number) => {
    try {
      await apiClient.post(`/habits/${id}/checkin`, {
        date: dayjs().format("YYYY-MM-DD"),
        completed: true,
      });
      message.success("今日打卡成功");
      fetchAll();
    } catch (err: any) {
      message.error(err?.userMessage || "打卡失败");
    }
  };

  const toggleActive = async (h: Habit, active: boolean) => {
    try {
      await apiClient.put(`/habits/${h.id}`, { is_active: active ? 1 : 0 });
      message.success(active ? "习惯已启用" : "习惯已停用");
      fetchAll();
    } catch (err: any) {
      message.error(err?.userMessage || "更新失败");
    }
  };

  const columns = [
    { title: "习惯", dataIndex: "name", key: "name" },
    {
      title: "分类", dataIndex: "category", key: "category", width: 90,
      render: (c: string | null) => c || <Text type="secondary">—</Text>,
    },
    {
      title: "频率", dataIndex: "frequency", key: "frequency", width: 80,
      render: (f: string) => f === "daily" ? "每天" : "每周",
    },
    {
      title: "当前连击", key: "streak", width: 110,
      render: (_: any, r: Habit) => (
        <Space>
          <FireOutlined style={{ color: "#ff4d4f" }} />
          <Text strong>{streaks[r.id]?.current_streak ?? r.streak ?? 0} 天</Text>
        </Space>
      ),
    },
    {
      title: "最长/累计", key: "total", width: 120,
      render: (_: any, r: Habit) => {
        const s = streaks[r.id];
        return s ? <Text type="secondary">{s.longest_streak} / {s.total_checkins}</Text>
          : <Text type="secondary">—</Text>;
      },
    },
    {
      title: "30天完成率", dataIndex: "completion_rate_30d", key: "rate", width: 120,
      render: (v: number) => `${Math.round((v ?? 0) * 100)}%`,
    },
    {
      title: "状态", dataIndex: "is_active", key: "active", width: 90,
      render: (v: number) => v === 1 ? <Tag color="green">进行中</Tag> : <Tag>已停用</Tag>,
    },
    {
      title: "操作", key: "op", width: 200,
      render: (_: any, r: Habit) => (
        <Space>
          <Button
            type="primary" size="small" icon={<CheckCircleOutlined />}
            disabled={r.is_active !== 1}
            onClick={() => checkin(r.id)}
          >
            打卡
          </Button>
          <Switch
            size="small" checked={r.is_active === 1}
            onChange={(v) => toggleActive(r, v)}
          />
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={3}><CheckCircleOutlined /> 习惯养成</Title>
      <Paragraph type="secondary">
        每天打卡一次，攒起你的连击天数。停用习惯会保留历史打卡，只是不再提醒。
      </Paragraph>

      <Row gutter={16}>
        <Col span={16}>
          <Card title="我的习惯" loading={loading}>
            <Table dataSource={habits} columns={columns} rowKey="id" pagination={{ pageSize: 10 }} size="small" />
          </Card>
        </Col>
        <Col span={8}>
          <Card title={<><PlusOutlined /> 新建习惯</>}>
            <Form form={form} layout="vertical" onFinish={submitHabit}>
              <Form.Item name="name" label="习惯名称" rules={[{ required: true, message: "填习惯名称" }]}>
                <Input placeholder="如：晨跑 30 分钟" maxLength={100} />
              </Form.Item>
              <Form.Item name="description" label="描述">
                <Input.TextArea placeholder="为什么要养成这个习惯？（可选）" rows={2} maxLength={500} />
              </Form.Item>
              <Form.Item name="category" label="分类">
                <Input placeholder="如：健康 / 学习（可选）" maxLength={50} />
              </Form.Item>
              <Space>
                <Form.Item name="frequency" label="频率" initialValue="daily">
                  <Select style={{ width: 110 }} options={[
                    { label: "每天", value: "daily" },
                    { label: "每周", value: "weekly" },
                  ]} />
                </Form.Item>
                <Form.Item name="target_count" label="每日目标次数" initialValue={1}>
                  <InputNumber min={1} max={10} style={{ width: 130 }} />
                </Form.Item>
              </Space>
              <Form.Item style={{ marginBottom: 0 }}>
                <Button type="primary" htmlType="submit" block>创建习惯</Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>
      </Row>
    </div>
  );
}
