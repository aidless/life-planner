import { useState } from "react";
import {
  Card, Table, Button, Modal, Form, Input, Select, InputNumber,
  DatePicker, Tag, Typography, message, Space, Alert, Descriptions,
} from "antd";
import { PlusOutlined, RobotOutlined, DeleteOutlined } from "@ant-design/icons";
import apiClient from "@/api/client";
import { useAsyncData } from "@/hooks/useAsyncData";
import type { DailyLog } from "@/types";
import dayjs from "dayjs";

const { Title } = Typography;

const activityTypes = [
  { label: "学习", value: "study" },
  { label: "运动", value: "exercise" },
  { label: "工作", value: "work" },
  { label: "休闲", value: "leisure" },
  { label: "社交", value: "social" },
  { label: "睡眠", value: "sleep" },
  { label: "其他", value: "other" },
];

const typeColors: Record<string, string> = {
  study: "blue", exercise: "green", work: "orange",
  leisure: "purple", social: "cyan", sleep: "gray", other: "default",
};

export default function DailyTracker() {
  const [modalOpen, setModalOpen] = useState(false);
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [selectedLog, setSelectedLog] = useState<DailyLog | null>(null);
  const [form] = Form.useForm();

  const { data: logs, loading, error, reload } = useAsyncData<DailyLog[]>(
    async () => {
      const res = await apiClient.get("/daily-logs");
      return res.data.data || [];
    },
  );

  const handleCreate = async (values: Record<string, unknown>) => {
    try {
      await apiClient.post("/daily-logs", {
        ...values,
        date: values.date ? dayjs(values.date as string).format("YYYY-MM-DD") : dayjs().format("YYYY-MM-DD"),
      });
      message.success("记录已添加");
      setModalOpen(false);
      form.resetFields();
      reload();
    } catch (err: any) {
      message.error(err?.userMessage || "添加失败");
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await apiClient.delete(`/daily-logs/${id}`);
      message.success("记录已删除");
      reload();
    } catch (err: any) {
      message.error(err?.userMessage || "删除失败");
    }
  };

  const handleAnalyze = async (log: DailyLog) => {
    setSelectedLog(log);
    setFeedback("");
    setFeedbackOpen(true);
    setAnalyzing(true);
    try {
      const res = await apiClient.post(`/daily-logs/${log.id}/analyze`);
      setFeedback(res.data.data.feedback);
    } catch (err: any) {
      setFeedback(err?.userMessage || "AI 分析失败，请检查 API 配置");
    } finally {
      setAnalyzing(false);
    }
  };

  const columns = [
    { title: "日期", dataIndex: "date", key: "date",
      render: (d: string) => dayjs(d).format("YYYY-MM-DD") },
    { title: "类型", dataIndex: "activity_type", key: "type",
      render: (t: string) => <Tag color={typeColors[t] || "default"}>{t}</Tag> },
    { title: "描述", dataIndex: "description", key: "desc" },
    { title: "时长", dataIndex: "duration_minutes", key: "dur",
      render: (v: number) => `${v}分钟` },
    { title: "心情", dataIndex: "mood_level", key: "mood",
      render: (v: number | null) => v ? `${v}/5` : "-" },
    { title: "操作", key: "actions",
      render: (_: unknown, record: DailyLog) => (
        <Space>
          <Button size="small" icon={<RobotOutlined />} onClick={() => handleAnalyze(record)}>AI</Button>
          <Button size="small" danger icon={<DeleteOutlined />} onClick={() => handleDelete(record.id)} />
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
        <Title level={3}>日常记录</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>添加记录</Button>
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
        <Table
          dataSource={logs || []}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
          locale={{ emptyText: error ? "加载失败" : "还没有记录，点上方按钮添加" }}
        />
      </Card>

      <Modal title="添加日常记录" open={modalOpen}
        onCancel={() => setModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item name="date" label="日期" initialValue={dayjs()}>
            <DatePicker style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="activity_type" label="活动类型" rules={[{ required: true }]}>
            <Select options={activityTypes} />
          </Form.Item>
          <Form.Item name="description" label="描述" rules={[{ required: true }]}>
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item name="duration_minutes" label="时长(分钟)" initialValue={30}>
            <InputNumber min={1} max={1440} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="mood_level" label="心情(1-5)">
            <InputNumber min={1} max={5} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="energy_level" label="精力(1-5)">
            <InputNumber min={1} max={5} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="notes" label="备注"><Input.TextArea rows={2} /></Form.Item>
        </Form>
      </Modal>

      <Modal title="AI 活动分析" open={feedbackOpen}
        onCancel={() => setFeedbackOpen(false)} footer={null} width={600}>
        {selectedLog && (
          <Descriptions column={1} size="small" style={{ marginBottom: 16 }}>
            <Descriptions.Item label="日期">{dayjs(selectedLog.date).format("YYYY-MM-DD")}</Descriptions.Item>
            <Descriptions.Item label="活动">{selectedLog.description}</Descriptions.Item>
          </Descriptions>
        )}
        <Card style={{ background: "#f6f8fa" }}>
          <Typography.Paragraph style={{ whiteSpace: "pre-wrap" }}>
            {feedback || "正在生成 AI 分析..."}
          </Typography.Paragraph>
        </Card>
      </Modal>
    </div>
  );
}
