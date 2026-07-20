import { Card, Typography, Input, Button, Form, Select } from "antd";
import { useState } from "react";
import apiClient from "@/api/client";

const { Title, Paragraph } = Typography;

export default function GradAdvisor() {
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async (values: Record<string, unknown>) => {
    setLoading(true);
    try {
      const res = await apiClient.post("/ai/analyze", {
        module: "grad",
        data: JSON.stringify(values, null, 2),
      });
      setResult(res.data.data.answer);
    } catch {
      setResult("AI 分析失败，请检查 API 配置");
    } finally { setLoading(false); }
  };

  return (
    <div>
      <Title level={3}>研究生规划</Title>
      <Paragraph type="secondary">研究方向选择、学校申请、导师选择的 AI 指导</Paragraph>
      <Card style={{ maxWidth: 700 }}>
        <Form layout="vertical" onFinish={handleAnalyze}>
          <Form.Item name="degree" label="目标学位">
            <Select options={[
              { label: "硕士 (Master)", value: "master" },
              { label: "博士 (PhD)", value: "phd" },
            ]} /></Form.Item>
          <Form.Item name="major" label="本科专业"><Input placeholder="如: 计算机科学" /></Form.Item>
          <Form.Item name="interests" label="研究兴趣">
            <Input.TextArea rows={2} placeholder="如: 人工智能、自然语言处理" /></Form.Item>
          <Form.Item name="target_schools" label="意向学校">
            <Input placeholder="如: 清华、北大、浙大" /></Form.Item>
          <Form.Item name="questions" label="具体问题">
            <Input.TextArea rows={3} placeholder="如: 如何选择导师？研究方向怎么定？" /></Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>AI 咨询</Button>
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
