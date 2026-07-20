import { Card, Typography, Input, Button, Form, InputNumber, Select } from "antd";
import { useState } from "react";
import apiClient from "@/api/client";

const { Title, Paragraph } = Typography;

export default function StudyPlanner() {
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async (values: Record<string, unknown>) => {
    setLoading(true);
    try {
      const res = await apiClient.post("/ai/analyze", {
        module: "study",
        data: JSON.stringify(values, null, 2),
      });
      setResult(res.data.data.answer);
    } catch {
      setResult("AI 分析失败，请检查 API 配置");
    } finally { setLoading(false); }
  };

  return (
    <div>
      <Title level={3}>学习规划</Title>
      <Paragraph type="secondary">AI 帮你制定科学高效的学习计划</Paragraph>
      <Card style={{ maxWidth: 700 }}>
        <Form layout="vertical" onFinish={handleAnalyze}>
          <Form.Item name="level" label="学段">
            <Select options={[
              { label: "初中", value: "junior" },
              { label: "高中", value: "senior" },
              { label: "大学本科", value: "undergrad" },
              { label: "研究生", value: "grad" },
            ]} /></Form.Item>
          <Form.Item name="subjects" label="学习科目">
            <Input placeholder="如: 数学、英语、物理" /></Form.Item>
          <Form.Item name="goal" label="目标">
            <Input.TextArea rows={2} placeholder="如: 期末考进年级前50" /></Form.Item>
          <Form.Item name="weekly_hours" label="每周学习时间(小时)">
            <InputNumber min={1} max={100} style={{ width: "100%" }} /></Form.Item>
          <Form.Item name="challenges" label="当前困难">
            <Input.TextArea rows={3} placeholder="描述你遇到的学习困难" /></Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>AI 制定计划</Button>
        </Form>
        {result && (
          <Card style={{ marginTop: 16, background: "#f6f8fa" }}>
            <Paragraph style={{ whiteSpace: "pre-wrap" }}>{result}</Paragraph>
          </Card>
        )}
      </Card>
    </div>
  );
}
