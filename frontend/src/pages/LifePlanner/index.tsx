import { useState } from "react";
import {
  Card, List, Button, Modal, Form, Input, Select, DatePicker,
  Tag, Typography, message, Progress, Space, Slider, Alert,
} from "antd";
import { PlusOutlined, DeleteOutlined, EditOutlined } from "@ant-design/icons";
import apiClient from "@/api/client";
import { useAsyncData } from "@/hooks/useAsyncData";
import type { LifeGoal } from "@/types";
import dayjs from "dayjs";

const { Title } = Typography;

const categories = [
  { label: "学习", value: "study" }, { label: "职业", value: "career" },
  { label: "健康", value: "health" }, { label: "财务", value: "finance" },
  { label: "人际关系", value: "relationships" }, { label: "个人成长", value: "growth" },
  { label: "通用", value: "general" },
];

const catColors: Record<string, string> = {
  study: "blue", career: "orange", health: "green",
  finance: "gold", relationships: "pink", growth: "purple", general: "default",
};

const statusLabels: Record<string, string> = {
  active: "进行中", completed: "已完成", archived: "已归档",
};

export default function LifePlanner() {
  const [modalOpen, setModalOpen] = useState(false);
  const [editingGoal, setEditingGoal] = useState<LifeGoal | null>(null);
  const [form] = Form.useForm();

  const { data: goals, loading, error, reload } = useAsyncData<LifeGoal[]>(
    async () => {
      const res = await apiClient.get("/goals");
      return res.data.data || [];
    },
  );

  const handleSubmit = async (values: Record<string, unknown>) => {
    try {
      if (editingGoal) {
        await apiClient.put(`/goals/${editingGoal.id}`, values);
        message.success("目标已更新");
      } else {
        await apiClient.post("/goals", values);
        message.success("目标已创建");
      }
      setModalOpen(false); setEditingGoal(null); form.resetFields();
      reload();
    } catch (err: any) {
      message.error(err?.userMessage || "操作失败");
    }
  };

  const handleEdit = (goal: LifeGoal) => {
    setEditingGoal(goal);
    form.setFieldsValue({
      ...goal,
      target_date: goal.target_date ? dayjs(goal.target_date) : null,
    });
    setModalOpen(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await apiClient.delete(`/goals/${id}`);
      message.success("已删除");
      reload();
    } catch (err: any) {
      message.error(err?.userMessage || "删除失败");
    }
  };

  const handleProgress = async (goal: LifeGoal, progress: number) => {
    try {
      await apiClient.put(`/goals/${goal.id}`, {
        progress,
        status: progress >= 100 ? "completed" : "active",
      });
      reload();
    } catch (err: any) {
      message.error(err?.userMessage || "更新失败");
    }
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
        <Title level={3}>人生目标</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => {
          setEditingGoal(null); form.resetFields(); setModalOpen(true);
        }}>添加目标</Button>
      </div>
      {error && (
        <Alert
          type="error"
          showIcon
          message="数据加载失败"
          description={error}
          action={<a onClick={() => reload()}>重试</a>}
          style={{ marginBottom: 16 }}
          closable
        />
      )}
      <Card>
        <List
          dataSource={goals || []}
          loading={loading}
          locale={{ emptyText: error ? "加载失败" : "还没有人生目标，开始制定吧!" }}
          renderItem={(goal) => (
            <List.Item
              actions={[
                <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(goal)} key="edit">编辑</Button>,
                <Button size="small" danger icon={<DeleteOutlined />} onClick={() => handleDelete(goal.id)} key="del" />,
              ]}
            >
              <List.Item.Meta
                title={
                  <Space>
                    <Tag color={catColors[goal.category]}>{goal.category}</Tag>
                    <span>{goal.title}</span>
                    <Tag>{statusLabels[goal.status] || goal.status}</Tag>
                  </Space>
                }
                description={
                  <div>
                    {goal.description && <p>{goal.description}</p>}
                    <Progress percent={Math.round(goal.progress)} size="small"
                      style={{ maxWidth: 300, marginBottom: 8 }} />
                    <Slider min={0} max={100} value={goal.progress}
                      onChange={(v) => handleProgress(goal, v)} style={{ maxWidth: 300 }} />
                    <Space size="large">
                      {goal.target_date && <span>目标: {dayjs(goal.target_date).format("YYYY-MM-DD")}</span>}
                      <span>优先级: {"⭐".repeat(goal.priority)}</span>
                    </Space>
                  </div>
                }
              />
            </List.Item>
          )}
        />
      </Card>

      <Modal title={editingGoal ? "编辑目标" : "添加目标"} open={modalOpen}
        onCancel={() => { setModalOpen(false); setEditingGoal(null); form.resetFields(); }}
        onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="title" label="目标标题" rules={[{ required: true }]}>
            <Input placeholder="如: 每天跑步5公里" /></Form.Item>
          <Form.Item name="description" label="详细描述">
            <Input.TextArea rows={3} /></Form.Item>
          <Form.Item name="category" label="分类" initialValue="general">
            <Select options={categories} /></Form.Item>
          <Form.Item name="priority" label="优先级" initialValue={1}>
            <Select options={[
              { label: "⭐ 低", value: 1 }, { label: "⭐⭐ 中", value: 2 }, { label: "⭐⭐⭐ 高", value: 3 },
            ]} /></Form.Item>
          <Form.Item name="target_date" label="目标日期">
            <DatePicker style={{ width: "100%" }} /></Form.Item>
          <Form.Item name="progress" label="进度" initialValue={0}>
            <Slider min={0} max={100} /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
