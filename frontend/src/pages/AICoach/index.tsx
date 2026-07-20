import { useState } from "react";
import { Card, Button, Typography, Space, List, Tag } from "antd";
import { RobotOutlined, SendOutlined } from "@ant-design/icons";
import apiClient from "@/api/client";

const { Title, Paragraph } = Typography;

const modules = [
  { key: "life", name: "人生规划" },
  { key: "study", name: "学习规划" },
  { key: "college", name: "高考志愿" },
  { key: "career", name: "职业发展" },
  { key: "grad", name: "研究生" },
  { key: "general", name: "通用" },
];

interface ChatMsg { role: "user" | "ai"; content: string }

export default function AICoach() {
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [input, setInput] = useState("");
  const [module, setModule] = useState("general");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);
    try {
      const ctx = messages.slice(-6).map((m) => m.content).join("\n");
      const res = await apiClient.post("/ai/chat", { module, question: userMsg, context: ctx });
      setMessages((prev) => [...prev, { role: "ai", content: res.data.data.answer }]);
    } catch {
      setMessages((prev) => [...prev, { role: "ai", content: "AI 服务暂时不可用，请检查 API 配置。" }]);
    } finally { setLoading(false); }
  };

  return (
    <div>
      <Title level={3}>AI 教练</Title>
      <Paragraph type="secondary">选择领域，向 AI 教练提问，获取个性化指导</Paragraph>

      <div style={{ marginBottom: 16 }}>
        <Space wrap>
          {modules.map((m) => (
            <Tag.CheckableTag
              key={m.key}
              checked={module === m.key}
              onChange={() => setModule(m.key)}
              style={{ padding: "4px 12px", fontSize: 14 }}
            >
              {m.name}
            </Tag.CheckableTag>
          ))}
        </Space>
      </div>

      <Card style={{ height: 400, overflow: "auto", marginBottom: 16 }}>
        {messages.length === 0 ? (
          <div style={{ textAlign: "center", color: "#999", paddingTop: 150 }}>
            <RobotOutlined style={{ fontSize: 48, marginBottom: 16 }} />
            <p>选择领域后开始与 AI 教练对话</p>
          </div>
        ) : (
          <List
            dataSource={messages}
            renderItem={(msg) => (
              <List.Item style={{
                justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
                border: "none", padding: "8px 0",
              }}>
                <Card size="small" style={{
                  maxWidth: "80%",
                  background: msg.role === "user" ? "#e6f4ff" : "#f6f8fa",
                  borderRadius: 12,
                }}>
                  <Paragraph style={{ margin: 0, whiteSpace: "pre-wrap" }}>{msg.content}</Paragraph>
                </Card>
              </List.Item>
            )}
          />
        )}
      </Card>

      <Space.Compact style={{ width: "100%" }}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
          }}
          placeholder="输入你的问题，按 Enter 发送..."
          rows={2}
          disabled={loading}
          style={{
            flex: 1, resize: "none", borderRadius: "6px 0 0 6px",
            border: "1px solid #d9d9d9", padding: "8px 12px", fontSize: 14,
          }}
        />
        <Button type="primary" icon={<SendOutlined />} onClick={handleSend}
          loading={loading} style={{ height: "auto", borderRadius: "0 6px 6px 0" }}>
          发送
        </Button>
      </Space.Compact>
    </div>
  );
}
