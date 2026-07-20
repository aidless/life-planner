import { Card, Typography, Input, Button, Form, Select } from "antd";
import { useState } from "react";
import apiClient from "@/api/client";

const { Title, Paragraph } = Typography;

export default function CareerAdvisor() {
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async (values: Record<string, unknown>) => {
    setLoading(true);
    try {
      const res = await apiClient.post("/ai/analyze", {
        module: "career",
        data: JSON.stringify(values, null, 2),
      });
      setResult(res.data.data.answer);
    } catch {
      setResult("AI 分析失败，请检查 API 配置");
    } finally { setLoading(false); }
  };

  return (
    <div>
      <Title level={3}>职业发展</Title>
      <Paragraph type="secondary">从实习到求职，AI 帮你规划职业道路</Paragraph>
      <Card style={{ maxWidth: 700 }}>
        <Form layout="vertical" onFinish={handleAnalyze}>
          <Form.Item name="stage" label="当前阶段">
            <Select options={[
              { label: "大一·大二 - 探索期", value: "early" },
              { label: "大三 - 实习期", value: "intern" },
              { label: "大四 - 求职期", value: "job" },
              { label: "应届毕业 - 已毕业", value: "graduate" },
            ]} /></Form.Item>
          <Form.Item name="major" label="专业"><Input placeholder="如: 计算机科学" /></Form.Item>
          <Form.Item name="skills" label="技能">
            <Input.TextArea rows={2} placeholder="如: Python, React, SQL" /></Form.Item>
          <Form.Item name="target_industry" label="目标行业">
            <Input placeholder="如: 互联网、金融" /></Form.Item>
          <Form.Item name="questions" label="具体问题">
            <Input.TextArea rows={3} placeholder="描述你想了解的问题" /></Form.Item>
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
