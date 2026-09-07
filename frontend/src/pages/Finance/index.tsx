/**
 * Finance 财务页面（P4-1）
 *
 * 记账（transactions）+ 预算（budgets）+ 储蓄目标（goals）+ 月统计（stats）
 * 后端：backend/app/modules/finance（prefix /api/finance）
 */

import { useEffect, useState } from "react";
import {
  Card, Form, Input, InputNumber, Select, DatePicker, Button, Table, Tag,
  Typography, Row, Col, message, Space, Progress,
} from "antd";
import { WalletOutlined, PieChartOutlined, FlagOutlined } from "@ant-design/icons";
import apiClient from "@/api/client";
import dayjs from "dayjs";

const { Title, Text } = Typography;

interface Tx {
  id: number;
  date: string;
  type: string;
  category: string;
  amount: number;
  note: string | null;
  created_at: string;
}

interface Budget {
  id: number;
  month: string;
  category: string;
  amount: number;
}

interface Goal {
  id: number;
  title: string;
  target_amount: number;
  current_amount: number;
  deadline: string | null;
  note: string | null;
  progress: number;
  created_at: string;
}

interface Stats {
  month: string;
  income: number;
  expense: number;
  savings: number;
  budget_compliance: number;
  savings_progress: number;
}

export default function Finance() {
  const [month, setMonth] = useState(dayjs().format("YYYY-MM"));
  const [txs, setTxs] = useState<Tx[]>([]);
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(false);
  const [txForm] = Form.useForm();
  const [budgetForm] = Form.useForm();
  const [goalForm] = Form.useForm();

  const fetchAll = async (m: string) => {
    setLoading(true);
    try {
      const [tr, br, gr, sr] = await Promise.all([
        apiClient.get("/finance/transactions", { params: { month: m } }),
        apiClient.get("/finance/budgets", { params: { month: m } }),
        apiClient.get("/finance/goals"),
        apiClient.get("/finance/stats", { params: { month: m } }),
      ]);
      setTxs(tr.data.data || []);
      setBudgets(br.data.data || []);
      setGoals(gr.data.data || []);
      setStats(sr.data.data || null);
    } catch (err: any) {
      message.error(err?.userMessage || "加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll(month);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [month]);

  const submitTx = async (v: any) => {
    try {
      await apiClient.post("/finance/transactions", {
        date: dayjs(v.date).format("YYYY-MM-DD"),
        type: v.type,
        category: v.category,
        amount: v.amount,
        note: v.note || null,
      });
      message.success("记账成功");
      txForm.resetFields();
      fetchAll(month);
    } catch (err: any) {
      message.error(err?.userMessage || "记账失败");
    }
  };

  const submitBudget = async (v: any) => {
    try {
      await apiClient.post("/finance/budgets", {
        month,
        category: v.category,
        amount: v.amount,
      });
      message.success("预算已设置");
      budgetForm.resetFields();
      fetchAll(month);
    } catch (err: any) {
      message.error(err?.userMessage || "设置预算失败");
    }
  };

  const submitGoal = async (v: any) => {
    try {
      await apiClient.post("/finance/goals", {
        title: v.title,
        target_amount: v.target_amount,
        deadline: v.deadline ? dayjs(v.deadline).format("YYYY-MM-DD") : null,
        note: v.note || null,
      });
      message.success("目标已创建");
      goalForm.resetFields();
      fetchAll(month);
    } catch (err: any) {
      message.error(err?.userMessage || "创建目标失败");
    }
  };

  const txColumns = [
    { title: "日期", dataIndex: "date", key: "date", width: 110 },
    {
      title: "类型", dataIndex: "type", key: "type", width: 80,
      render: (t: string) => t === "income"
        ? <Tag color="green">收入</Tag> : <Tag color="red">支出</Tag>,
    },
    { title: "分类", dataIndex: "category", key: "category", width: 100 },
    {
      title: "金额", dataIndex: "amount", key: "amount", width: 110,
      render: (a: number, r: Tx) => (
        <Text type={r.type === "income" ? "success" : "danger"}>
          {r.type === "income" ? "+" : "-"}{a.toFixed(2)}
        </Text>
      ),
    },
    { title: "备注", dataIndex: "note", key: "note", ellipsis: true },
  ];

  const budgetColumns = [
    { title: "分类", dataIndex: "category", key: "category" },
    {
      title: "预算", dataIndex: "amount", key: "amount",
      render: (a: number) => `¥${a.toFixed(2)}`,
    },
  ];

  return (
    <div>
      <Title level={3}><WalletOutlined /> 财务管理</Title>
      <Space style={{ marginBottom: 16 }}>
        <Text>月份：</Text>
        <DatePicker
          picker="month"
          value={dayjs(month)}
          onChange={(d) => d && setMonth(d.format("YYYY-MM"))}
          allowClear={false}
        />
      </Space>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card loading={loading}><Text type="secondary">本月收入</Text>
            <Title level={4} style={{ margin: 0, color: "#52c41a" }}>
              +{(stats?.income ?? 0).toFixed(2)}
            </Title>
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}><Text type="secondary">本月支出</Text>
            <Title level={4} style={{ margin: 0, color: "#ff4d4f" }}>
              -{(stats?.expense ?? 0).toFixed(2)}
            </Title>
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}><Text type="secondary">本月结余</Text>
            <Title level={4} style={{ margin: 0 }}>
              {(stats?.savings ?? 0).toFixed(2)}
            </Title>
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}><Text type="secondary">预算执行率</Text>
            <Title level={4} style={{ margin: 0 }}>
              {((stats?.budget_compliance ?? 0) * 100).toFixed(0)}%
            </Title>
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={16}>
          <Card title={<><WalletOutlined /> 收支明细</>} loading={loading}>
            <Form form={txForm} layout="inline" onFinish={submitTx} style={{ marginBottom: 16 }}>
              <Form.Item name="date" rules={[{ required: true, message: "选日期" }]}>
                <DatePicker placeholder="日期" />
              </Form.Item>
              <Form.Item name="type" rules={[{ required: true, message: "选类型" }]} initialValue="expense">
                <Select style={{ width: 90 }} options={[
                  { label: "支出", value: "expense" },
                  { label: "收入", value: "income" },
                ]} />
              </Form.Item>
              <Form.Item name="category" rules={[{ required: true, message: "填分类" }]}>
                <Input placeholder="分类" style={{ width: 110 }} />
              </Form.Item>
              <Form.Item name="amount" rules={[{ required: true, message: "填金额" }]}>
                <InputNumber placeholder="金额" min={0.01} precision={2} style={{ width: 120 }} />
              </Form.Item>
              <Form.Item name="note">
                <Input placeholder="备注（可选）" style={{ width: 140 }} />
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit">记一笔</Button>
              </Form.Item>
            </Form>
            <Table dataSource={txs} columns={txColumns} rowKey="id" pagination={{ pageSize: 8 }} size="small" />
          </Card>
        </Col>
        <Col span={8}>
          <Card title={<><PieChartOutlined /> 月预算</>} loading={loading} style={{ marginBottom: 16 }}>
            <Form form={budgetForm} layout="inline" onFinish={submitBudget} style={{ marginBottom: 16 }}>
              <Form.Item name="category" rules={[{ required: true, message: "填分类" }]}>
                <Input placeholder="分类" style={{ width: 110 }} />
              </Form.Item>
              <Form.Item name="amount" rules={[{ required: true, message: "填金额" }]}>
                <InputNumber placeholder="金额" min={0.01} precision={2} style={{ width: 120 }} />
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit">设置</Button>
              </Form.Item>
            </Form>
            <Table dataSource={budgets} columns={budgetColumns} rowKey="id" pagination={false} size="small" />
          </Card>
          <Card title={<><FlagOutlined /> 储蓄目标</>} loading={loading}>
            <Form form={goalForm} layout="vertical" onFinish={submitGoal} style={{ marginBottom: 16 }}>
              <Form.Item name="title" rules={[{ required: true, message: "填目标名称" }]}>
                <Input placeholder="目标名称，如：旅行基金" />
              </Form.Item>
              <Space>
                <Form.Item name="target_amount" rules={[{ required: true, message: "填目标金额" }]} noStyle>
                  <InputNumber placeholder="目标金额" min={0.01} precision={2} style={{ width: 150 }} />
                </Form.Item>
                <Form.Item name="deadline" noStyle>
                  <DatePicker placeholder="截止日期（可选）" />
                </Form.Item>
              </Space>
              <Form.Item name="note" style={{ marginTop: 8, marginBottom: 8 }}>
                <Input placeholder="备注（可选）" />
              </Form.Item>
              <Form.Item style={{ marginBottom: 0 }}>
                <Button type="primary" htmlType="submit">新建目标</Button>
              </Form.Item>
            </Form>
            {goals.map((g) => (
              <div key={g.id} style={{ marginBottom: 12 }}>
                <Space style={{ width: "100%", justifyContent: "space-between" }}>
                  <Text strong>{g.title}</Text>
                  <Text type="secondary">{g.current_amount.toFixed(0)} / {g.target_amount.toFixed(0)}</Text>
                </Space>
                <Progress percent={Math.round((g.progress ?? 0) * 100)} size="small" />
              </div>
            ))}
          </Card>
        </Col>
      </Row>
    </div>
  );
}
