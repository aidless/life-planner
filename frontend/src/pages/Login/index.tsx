import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Form, Input, Button, Card, Typography, Alert } from "antd";
import { UserOutlined, LockOutlined } from "@ant-design/icons";
import { useAuthStore } from "@/store/authStore";

const { Title, Text } = Typography;

export default function Login() {
  const [loading, setLoading] = useState(false);
  const { login, error, clearError } = useAuthStore();
  const navigate = useNavigate();

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    clearError();
    const ok = await login(values.username, values.password);
    setLoading(false);
    if (ok) navigate("/dashboard");
  };

  return (
    <div style={{
      minHeight: "100vh", display: "flex", alignItems: "center",
      justifyContent: "center",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    }}>
      <Card style={{ width: 400, borderRadius: 12, boxShadow: "0 8px 32px rgba(0,0,0,0.2)" }}>
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <Title level={3} style={{ marginBottom: 4 }}>人生规划系统</Title>
          <Text type="secondary">AI 驱动的人生规划助手</Text>
        </div>
        {error && <Alert message={error} type="error" showIcon style={{ marginBottom: 16 }} closable onClose={clearError} />}
        <Form onFinish={onFinish} size="large">
          <Form.Item name="username" rules={[{ required: true, message: "请输入用户名" }, { min: 3, message: "用户名至少 3 位" }]}>
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: "请输入密码" }, { min: 6, message: "密码至少 6 位" }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block style={{ height: 44, fontSize: 16 }}>
              登录
            </Button>
          </Form.Item>
        </Form>
        <div style={{ textAlign: "center" }}>
          <Text type="secondary">还没有账号？</Text> <Link to="/register" style={{ color: "#1677ff" }}>立即注册</Link>
        </div>
      </Card>
    </div>
  );
}